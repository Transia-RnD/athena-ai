# XRPL Cryptography Functionality: Comprehensive Lesson Plan

This document provides a detailed, component-level breakdown of the cryptography functionality in the XRPL (XRP Ledger) source code. Every aspect is explained strictly according to the provided code and context, with direct references to source files and code snippets.

---

## Table of Contents

- CSPRNG: Cryptographically Secure Pseudorandom Number Generation
- Secret Key Management
- Public Key Management
- Key Pair Generation
- Digital Signatures
- Base58 Encoding/Decoding of Keys
- RFC1751 English Key Representation
- Secure Memory Erasure
- Digest and Hashing Utilities
- How These Components Work Together

---

## CSPRNG: Cryptographically Secure Pseudorandom Number Generation

### csprng_engine

- **File:** [src/libxrpl/crypto/csprng.cpp](src/libxrpl/crypto/csprng.cpp.txt)
- **Header:** [include/xrpl/crypto/csprng.h](include/xrpl/crypto/csprng.h.txt)

#### csprng_engine::csprng_engine

- On construction, calls `RAND_poll()` from OpenSSL to seed the random number generator with system entropy.
- If `RAND_poll()` fails, throws a `std::runtime_error` ("CSPRNG: Initial polling failed").
- Ensures the PRNG is securely seeded before use.

#### csprng_engine::operator()(void* ptr, std::size_t count)

- Fills the buffer at `ptr` with `count` cryptographically secure random bytes using `RAND_bytes`.
- Ensures thread safety on older OpenSSL versions by locking a mutex.
- Throws a `std::runtime_error` ("CSPRNG: Insufficient entropy") if `RAND_bytes` fails.

#### csprng_engine::operator()()

- Returns a single 64-bit random value by filling a `std::uint64_t` with random bytes.

#### csprng_engine::mix_entropy

- Gathers additional entropy from `std::random_device` and mixes it into OpenSSL's PRNG using `RAND_add`.
- If a buffer is provided, mixes that buffer into the entropy pool.

#### csprng_engine::~csprng_engine

- For OpenSSL versions older than 1.1.0, calls `RAND_cleanup()` to clean up the PRNG state.

#### crypto_prng()

- Returns a reference to a static singleton instance of `csprng_engine`.
- Ensures only one instance of the PRNG engine is used throughout the program.

**Relevant code:**
src/libxrpl/crypto/csprng.cpp.txt

---

## Secret Key Management

### SecretKey Class

- **Header:** [include/xrpl/protocol/SecretKey.h](include/xrpl/protocol/SecretKey.h.txt)
- **Implementation:** [src/libxrpl/protocol/SecretKey.cpp](src/libxrpl/protocol/SecretKey.cpp.txt)

#### SecretKey::SecretKey(std::array<std::uint8_t, 32> const& key)

- Copies the 32 bytes from the input array into the internal buffer `buf_`.

#### SecretKey::SecretKey(Slice const& slice)

- Checks that the input slice is exactly 32 bytes.
- Copies the bytes into the internal buffer.
- Throws a logic error if the size is not 32 bytes.

#### SecretKey::~SecretKey

- Securely erases the internal buffer using `secure_erase` (which calls `OPENSSL_cleanse`) when the object is destroyed.

#### SecretKey::to_string

- Returns the hexadecimal string representation of the secret key's bytes using `strHex`.

#### randomSecretKey

- Allocates a 32-byte buffer.
- Fills it with cryptographically secure random bytes using `beast::rngfill` and `crypto_prng()`.
- Constructs a `SecretKey` from the buffer.
- Securely erases the buffer after use.

#### generateSecretKey(KeyType type, Seed const& seed)

- For `ed25519`: Uses the seed directly or via standard ed25519 derivation to produce a 32-byte key.
- For `secp256k1`: Calls `deriveDeterministicRootKey(seed)` to derive a deterministic root key, using SHA-512 half-hash and sequence numbers, checking for key validity.
- Constructs a `SecretKey` from the resulting 32 bytes.
- Securely erases temporary buffers.

**Relevant code:**
src/libxrpl/protocol/SecretKey.cpp.txt

---

## Public Key Management

### PublicKey Class

- **Header:** [include/xrpl/protocol/PublicKey.h](include/xrpl/protocol/PublicKey.h.txt)
- **Implementation:** [src/libxrpl/protocol/PublicKey.cpp](src/libxrpl/protocol/PublicKey.cpp.txt)

#### PublicKey::PublicKey(Slice const& slice)

- Constructs a public key from a 33-byte slice.

#### operator<<(std::ostream&, PublicKey const&)

- Outputs the hexadecimal string representation of the public key to a stream using `strHex`.

#### parseBase58(TokenType type, std::string const& s)

- Decodes a Base58-encoded string into binary using `decodeBase58Token`.
- Validates the result as a public key using `publicKeyType`.
- Returns a `PublicKey` object if valid, or `std::nullopt` if invalid.

**Relevant code:**
src/libxrpl/protocol/PublicKey.cpp.txt

---

## Key Pair Generation

### generateKeyPair(KeyType type, Seed const& seed)

- **Header:** [include/xrpl/protocol/SecretKey.h](include/xrpl/protocol/SecretKey.h.txt)
- **Implementation:** [src/libxrpl/protocol/SecretKey.cpp](src/libxrpl/protocol/SecretKey.cpp.txt)

#### For secp256k1

- Uses a `Generator` class:
    - Derives a deterministic root key from the seed.
    - Uses `secp256k1_ec_pubkey_create` and `secp256k1_ec_pubkey_serialize` to create a compressed public key.
    - Applies a tweak (derived from the generator and ordinal) to the root key to produce the final secret key.
    - Returns the pair `{publicKey, secretKey}`.

#### For ed25519

- Hashes the seed with `sha512Half_s` to produce the secret key.
- Uses `ed25519_publickey` to derive the public key.
- Returns the pair `{publicKey, secretKey}`.

### randomKeyPair(KeyType type)

- Calls `randomSecretKey()` to generate a random 32-byte secret key.
- Calls `derivePublicKey(type, sk)` to compute the public key.
- Returns `{publicKey, secretKey}`.

**Relevant code:**
src/libxrpl/protocol/SecretKey.cpp.txt

---

## Digital Signatures

### sign(PublicKey const& pk, SecretKey const& sk, Slice const& m)

- **Header:** [include/xrpl/protocol/SecretKey.h](include/xrpl/protocol/SecretKey.h.txt)
- **Implementation:** [src/libxrpl/protocol/SecretKey.cpp](src/libxrpl/protocol/SecretKey.cpp.txt)

#### For ed25519

- Allocates a 64-byte buffer for the signature.
- Calls `ed25519_sign` with the message, secret key, and public key (skipping the first byte, which is a type marker).
- Returns the signature as a Buffer.

#### For secp256k1

- Computes a SHA-512 half hash of the message.
- Calls `secp256k1_ecdsa_sign` with the digest and secret key, using RFC6979 deterministic nonce.
- Serializes the signature to DER format using `secp256k1_ecdsa_signature_serialize_der`.
- Returns the DER-encoded signature as a Buffer.

#### Error Handling

- Throws a logic error if the key type is invalid or if signing fails.

### signDigest(PublicKey const& pk, SecretKey const& sk, uint256 const& digest)

- Only supports `secp256k1` keys.
- Signs a precomputed digest using ECDSA and returns the DER-encoded signature as a Buffer.
- Throws a logic error if the key type is not `secp256k1` or if signing/serialization fails.

**Relevant code:**
src/libxrpl/protocol/SecretKey.cpp.txt

---

## Base58 Encoding/Decoding of Keys

### encodeBase58Token(TokenType type, void const* token, std::size_t size)

- **File:** [src/libxrpl/protocol/tokens.cpp](src/libxrpl/protocol/tokens.cpp.txt)
- Delegates to either `b58_fast::encodeBase58Token` or `b58_ref::encodeBase58Token` depending on the platform.
- Returns a Base58-encoded string.

### decodeBase58Token(TokenType type, std::string const& s)

- **File:** [src/libxrpl/protocol/tokens.cpp](src/libxrpl/protocol/tokens.cpp.txt)
- Allocates a 64-byte buffer.
- Calls `b58_fast::decodeBase58Token` to decode the string into binary.
- Resizes the buffer to the actual decoded size.
- Returns the decoded bytes as a string, or an empty string on failure.

### parseBase58 for PublicKey

- Decodes the Base58 string.
- Validates the result as a public key.
- Returns a `PublicKey` object or `std::nullopt`.

### parseBase58 for SecretKey

- **Header:** [include/xrpl/protocol/SecretKey.h](include/xrpl/protocol/SecretKey.h.txt)
- The implementation is not present in the provided context. Only the declaration is available.

**Relevant code:**
src/libxrpl/protocol/tokens.cpp.txt  
src/libxrpl/protocol/PublicKey.cpp.txt

---

## RFC1751 English Key Representation

### RFC1751::getEnglishFromKey

- **Header:** [include/xrpl/crypto/RFC1751.h](include/xrpl/crypto/RFC1751.h.txt)
- **Implementation:** [src/libxrpl/crypto/RFC1751.cpp](src/libxrpl/crypto/RFC1751.cpp.txt)

- Splits a binary key into two 8-byte chunks.
- Converts each chunk to a sequence of English words using the `btoe` helper.
- Concatenates the two sequences with a space.

### RFC1751::btoe

- Converts an 8-byte binary chunk into a sequence of 6 English words, using a fixed dictionary of 2048 words (`s_dictionary`).
- Uses the `extract` helper to extract bitfields and map them to dictionary indices.

### RFC1751::getKeyFromEnglish

- Converts a human-readable string of words into a binary key.
- Splits the input into words.
- Looks up each word in the dictionary to get its index.
- Packs the indices into a binary buffer using the `insert` helper.

### RFC1751::getWordFromBlob

- Hashes a blob of data and returns a word from the dictionary based on the hash.

**Relevant code:**
src/libxrpl/crypto/RFC1751.cpp.txt

---

## Secure Memory Erasure

### secure_erase

- **File:** [src/libxrpl/crypto/secure_erase.cpp](src/libxrpl/crypto/secure_erase.cpp.txt)
- **Header:** [include/xrpl/crypto/secure_erase.h](include/xrpl/crypto/secure_erase.h.txt)

- Calls `OPENSSL_cleanse` to securely overwrite a memory region.
- Used in destructors and after handling sensitive data to prevent recovery of secret material.

**Relevant code:**
src/libxrpl/crypto/secure_erase.cpp.txt

---

## Digest and Hashing Utilities

### sha512_half_hasher and sha512_half_hasher_s

- **Header:** [include/xrpl/protocol/digest.h](include/xrpl/protocol/digest.h.txt)
- Used to compute SHA-512 half-hashes (first 256 bits of SHA-512).
- Used in key derivation, signature hashing, and other cryptographic operations.

### openssl_sha256_hasher, openssl_ripemd160_hasher

- Provide SHA-256 and RIPEMD-160 hashing using OpenSSL.

### Usage in Key Derivation

- `deriveDeterministicRootKey` uses SHA-512 half-hash to derive secp256k1 root keys from seeds.
- `generateSecretKey` for ed25519 uses SHA-512 half-hash on the seed.

**Relevant code:**
include/xrpl/protocol/digest.h.txt  
src/libxrpl/protocol/SecretKey.cpp.txt

---

## How These Components Work Together

- **Random Key Generation:**  
  - `randomKeyPair` uses `randomSecretKey` (which uses the CSPRNG) and `derivePublicKey` to produce a random key pair.
- **Deterministic Key Generation:**  
  - `generateKeyPair` uses a seed and key type to deterministically derive a key pair, using hashing and key derivation functions.
- **Signing:**  
  - `sign` and `signDigest` use the secret key to sign messages or digests, using the appropriate cryptographic algorithm for the key type.
- **Encoding/Decoding:**  
  - Keys can be encoded to or decoded from Base58 using `encodeBase58Token` and `decodeBase58Token`, and parsed using `parseBase58`.
- **Secure Handling:**  
  - All secret key material is securely erased from memory after use, using `secure_erase`.
- **Human-Readable Representation:**  
  - Keys can be converted to and from English word sequences using RFC1751 functions for easier manual handling or backup.

---

## Source Code Links and Snippets

- [src/libxrpl/crypto/csprng.cpp](src/libxrpl/crypto/csprng.cpp.txt)
- [src/libxrpl/crypto/secure_erase.cpp](src/libxrpl/crypto/secure_erase.cpp.txt)
- [src/libxrpl/protocol/SecretKey.cpp](src/libxrpl/protocol/SecretKey.cpp.txt)
- [src/libxrpl/protocol/PublicKey.cpp](src/libxrpl/protocol/PublicKey.cpp.txt)
- [src/libxrpl/protocol/tokens.cpp](src/libxrpl/protocol/tokens.cpp.txt)
- [src/libxrpl/crypto/RFC1751.cpp](src/libxrpl/crypto/RFC1751.cpp.txt)
- [include/xrpl/crypto/csprng.h](include/xrpl/crypto/csprng.h.txt)
- [include/xrpl/crypto/secure_erase.h](include/xrpl/crypto/secure_erase.h.txt)
- [include/xrpl/protocol/SecretKey.h](include/xrpl/protocol/SecretKey.h.txt)
- [include/xrpl/protocol/PublicKey.h](include/xrpl/protocol/PublicKey.h.txt)
- [include/xrpl/protocol/digest.h](include/xrpl/protocol/digest.h.txt)
- [include/xrpl/crypto/RFC1751.h](include/xrpl/crypto/RFC1751.h.txt)

---

**All explanations above are strictly grounded in the provided code and context. No assumptions or extrapolations have been made.**