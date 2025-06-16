# XRPL Cryptography Functionality

This document provides a comprehensive, code-grounded overview of the cryptography functionality in the XRPL (XRP Ledger) source code. It covers key management, signing and verification, secure erasure, random number generation, hashing, encoding, mnemonic support, node identity binding, error handling, thread safety, and certificate management. All statements are strictly based on the provided code and documentation.

---

## Table of Contents

- [Supported Key Types and Algorithms](#supported-key-types-and-algorithms)
- [Key Management](#key-management)
- [Mnemonic Encoding/Decoding (RFC1751)](#mnemonic-encodingdecoding-rfc1751)
- [Signing and Verification](#signing-and-verification)
- [Signature Canonicality and Error Handling](#signature-canonicality-and-error-handling)
- [Node Identity and SSL/TLS Session Binding](#node-identity-and-ssltls-session-binding)
- [Secure Erasure](#secure-erasure)
- [Random Number Generation](#random-number-generation)
- [Hashing and Digest Functions](#hashing-and-digest-functions)
- [Encoding and Decoding](#encoding-and-decoding)
- [Certificate Management](#certificate-management)
- [Security Notes: Thread Safety and Entropy](#security-notes-thread-safety-and-entropy)
- [Usage Examples](#usage-examples)
- [Standards Compliance](#standards-compliance)
- [References to Source Code](#references-to-source-code)

---

## Supported Key Types and Algorithms

| Key Type    | Purpose                        | Supported Operations                                 |
|-------------|-------------------------------|------------------------------------------------------|
| secp256k1   | Node identity, signing, SSL/TLS| Key generation, signing, verification, session binding|
| ed25519     | (Not detailed in provided code)| (Not detailed in provided code)                      |
| RSA         | SSL/TLS certificates           | Certificate creation, signing, verification (OpenSSL) |
| RFC1751     | Mnemonic encoding/decoding     | Key backup/recovery (see below)                      |

---

## Key Management

Key management is handled via the `SecretKey` and `PublicKey` classes (see `SecretKey.h`, `PublicKey.h`):

- **SecretKey**: Represents a 32-byte private key.
  - Constructed from a 32-byte array or byte slice.
  - Securely erased on destruction.
  - Methods for serialization, comparison, and string conversion.
  - Generation from a seed (`generateSecretKey(KeyType, Seed)`).
  - Random generation (`randomSecretKey()`), using a cryptographically secure PRNG.

- **PublicKey**: Represents a public key (33 bytes for secp256k1).
  - Constructed from a byte slice.
  - Methods for serialization, comparison, and string conversion.
  - Derived from a secret key (`derivePublicKey(KeyType, SecretKey)`).

- **Key Pair Generation**:
  - `generateKeyPair(KeyType, Seed)`: Deterministic key pair from a seed.
  - `randomKeyPair(KeyType)`: Random key pair.

- **Base58 Encoding/Decoding**:
  - Keys can be encoded/decoded to/from Base58 using `toBase58` and `parseBase58`.

---

## Mnemonic Encoding/Decoding (RFC1751)

**RFC1751** support is provided for converting binary keys to/from human-readable English word sequences (mnemonics), facilitating secure backup and recovery.

- **Functions** (see `RFC1751.h`):
  - `getKeyFromEnglish(std::string& key, std::string const& mnemonic)`
  - `getEnglishFromKey(std::string& mnemonic, std::string const& key)`
  - `getWordFromBlob(void const* blob, size_t bytes)`

- **Purpose**: Allows users to encode a binary key as a mnemonic phrase and decode it back, improving usability and backup safety.

---

## Signing and Verification

- **Signing**:
  - `sign(PublicKey, SecretKey, Slice message)`: Signs a message with the provided key pair.
    - For `secp256k1`: Hashes the message with SHA-512/256, then signs with `secp256k1_ecdsa_sign`.
    - For `ed25519`: (Not detailed in provided code).
  - `signDigest(PublicKey, SecretKey, uint256 digest)`: Signs a precomputed digest (secp256k1 only).

- **Verification**:
  - `verify(PublicKey, Slice message, Slice signature, bool mustBeFullyCanonical)`: Verifies a signature.
    - For `secp256k1`: Verifies the signature on the SHA-512/256 hash of the message.
    - Canonicality checks are enforced for secp256k1 signatures.

---

## Signature Canonicality and Error Handling

- **Canonicality**: All secp256k1 signatures must be fully canonical to prevent malleability.
- **Error Handling**: Errors in cryptographic operations (e.g., invalid signature, failed verification) are handled via exceptions or error codes, as appropriate for the operation.

---

## Node Identity and SSL/TLS Session Binding

XRPL nodes use secp256k1 keypairs as unique identities. To prevent MITM attacks and bind SSL/TLS sessions to node identities, XRPL implements a fingerprinting and signing mechanism (see `overlay/README.md`):

1. **Fingerprint Generation**:
   - Each endpoint extracts the `finished` messages from the SSL/TLS session.
   - The local and remote `finished` messages are combined to generate a unique fingerprint.
   - This fingerprint is independently computed by both endpoints and is never transmitted.

2. **Signing**:
   - Each server signs the fingerprint using its private secp256k1 key.

3. **Verification**:
   - The signature is sent over the encrypted SSL/TLS channel during the handshake.
   - The remote endpoint verifies the signature using the sender's public key.
   - If the signature check fails, the link is dropped.

This mechanism ensures that both endpoints are directly connected and not subject to MITM attacks.

---

## Secure Erasure

Sensitive cryptographic material is securely erased from memory to prevent leakage:

- The `secure_erase(void* dest, std::size_t bytes)` function uses `OPENSSL_cleanse` to overwrite memory.
- The `SecretKey` destructor calls `secure_erase` on its internal buffer.
- Temporary buffers used for key generation and signing are also securely erased after use.

---

## Random Number Generation

Cryptographically secure random numbers are generated using the `csprng_engine` class (`csprng.h`):

- Uses OpenSSL's `RAND_bytes` and system entropy sources.
- `randomSecretKey()` and other cryptographic operations use this engine to ensure unpredictability.
- Additional entropy can be mixed in via `mix_entropy`.

---

## Hashing and Digest Functions

Hashing is fundamental to XRPL cryptography for key derivation, signing, and address calculation:

- **Hashers**:
  - `openssl_sha256_hasher`, `openssl_sha512_hasher`, `openssl_ripemd160_hasher` wrap OpenSSL hash functions.
  - `sha512_half_hasher` computes SHA-512 and returns the first 256 bits (used for transaction and signature digests).
  - `ripesha_hasher` computes SHA-256 followed by RIPEMD-160 (used for account and node IDs).

- **Usage**:
  - Key derivation, signature digests, and address calculation all use these hashers.

---

## Encoding and Decoding

- **Base58**: Used for encoding keys and addresses for human readability and error detection.
  - Functions: `encodeBase58Token`, `parseBase58`.
- **Base64**: Used for encoding binary signatures in protocol messages.

---

## Certificate Management

- **Certificate Creation and Verification**:
  - The module uses OpenSSL for managing X.509 certificates, including creation, signing, and verification.
  - SSL/TLS contexts are managed via Boost.Asio and OpenSSL, supporting secure peer authentication and encrypted communication.
  - Certificate files can be loaded and verified as part of SSL context setup.

---

## Security Notes: Thread Safety and Entropy

- **Thread Safety**: Cryptographic operations are not guaranteed to be thread-safe unless explicitly documented. Use appropriate synchronization when sharing objects across threads.
- **Secure Memory Handling**: All sensitive data is securely erased from memory after use.
- **Entropy Requirements**: Key generation and cryptographic operations rely on high-quality entropy sources provided by OpenSSL.

---

## Usage Examples

### Key Generation (secp256k1)
```cpp
// Generate a random secp256k1 keypair
auto [publicKey, secretKey] = randomKeyPair(KeyType::secp256k1);
```

### Signing
```cpp
// Sign a message with a secp256k1 private key
Buffer signature = sign(publicKey, secretKey, messageSlice);
```

### Verification
```cpp
// Verify a signature with a secp256k1 public key
bool valid = verify(publicKey, messageSlice, signature, /*mustBeFullyCanonical=*/true);
```

### Secure Erasure
```cpp
#include <xrpl/crypto/secure_erase.h>
char* sensitive_data = ...;
std::size_t length = ...;
ripple::secure_erase(sensitive_data, length);
```

### RFC1751 Mnemonic Encoding/Decoding
```cpp
// Encode and decode a key using RFC1751
std::string mnemonic;
RFC1751::getEnglishFromKey(mnemonic, binaryKey);
std::string restoredKey;
RFC1751::getKeyFromEnglish(restoredKey, mnemonic);
```

---

## Standards Compliance

- **secp256k1**: Used for node identity and digital signatures.
- **RFC1751**: Supported for mnemonic encoding/decoding.
- **OpenSSL**: Used for cryptographic operations, secure memory handling, and certificate management.

---

## References to Source Code

- `src/libxrpl/protocol/SecretKey.cpp` / `SecretKey.h`: Key management, signing, secure erasure.
- `src/libxrpl/protocol/PublicKey.cpp` / `PublicKey.h`: Public key handling, verification.
- `src/libxrpl/crypto/csprng.cpp` / `csprng.h`: Secure random number generation.
- `src/libxrpl/crypto/secure_erase.cpp` / `secure_erase.h`: Secure memory erasure.
- `src/libxrpl/protocol/digest.cpp` / `digest.h`: Hashing functions.
- `src/libxrpl/protocol/tokens.cpp`: Base58 encoding/decoding.
- `src/libxrpl/basics/base64.cpp`: Base64 encoding/decoding.
- `src/libxrpl/crypto/RFC1751.cpp` / `RFC1751.h`: Mnemonic encoding/decoding.
- `src/xrpld/overlay/README.md`: Node identity and SSL/TLS session binding.

---

This documentation is strictly grounded in the provided code and explanations. For further details, refer to the XRPL source code and module headers.