#!/usr/bin/env python
# coding: utf-8

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled-escrow", "v1")
# indexer.build_from_dirs(
#     path,
#     ["include", "src/libxrpl", "src/test", "src/xrpld"],
#     True,
# )

from athenah_ai.client import AthenahClient
from playgrounds.core_dev.utils import collect_ai_v1_contents

idea1: str = """
```
```markdown
# XRPL Core Library Documentation Template

This document provides an overview of the key files in the `protocol` folder of the XRPL (XRP Ledger) core library. Each section describes the main purpose and functionality of a file, focusing on its role within the protocol. This structure is intended as a template for documenting other folders in the XRPL codebase.

---

## Table of Contents

- [Feature Management](#feature-management)
- [Cross-Chain and Asset Handling](#cross-chain-and-asset-handling)
- [Serialization and Data Structures](#serialization-and-data-structures)
- [Ledger and Transaction Processing](#ledger-and-transaction-processing)
- [Account and Key Management](#account-and-key-management)
- [Error Handling and Utilities](#error-handling-and-utilities)
- [AMM and Order Book Logic](#amm-and-order-book-logic)
- [NFT and Token Support](#nft-and-token-support)
- [Permissions and Rules](#permissions-and-rules)
- [Cryptography and Hashing](#cryptography-and-hashing)
- [Versioning and Build Information](#versioning-and-build-information)

---

## Feature Management

### Feature.cpp

Implements the management of protocol features (amendments) in XRPL. It defines a `FeatureCollections` class to register, track, and access features by name or ID, manage their support and voting status, and ensure registration is finalized before use. Global functions allow registering, retiring, and querying features, with macros automating feature registration.

---

## Cross-Chain and Asset Handling

### STXChainBridge.cpp

Implements the `STXChainBridge` class, representing a cross-chain bridge structure. Provides constructors for various input types, serialization, JSON conversion, text representation, and equivalence checking. Encapsulates details about locking and issuing chains, ensuring data validity.

### Asset.cpp

Implements the `Asset` class, supporting both `Issue` and `MPTIssue` types via `std::variant`. Provides methods for asset comparison, validation, JSON serialization, and construction from JSON, ensuring consistent asset representation.

### MPTIssue.cpp

Implements the `MPTIssue` class, encapsulating an MPTID for token issuance. Provides methods for extracting the issuer, serialization/deserialization, and string conversion, with error handling for JSON parsing.

---

## Serialization and Data Structures

### Serializer.cpp

Implements the `Serializer` and `SerialIter` classes. `Serializer` manages serialization of various data types and internal byte buffers, while `SerialIter` allows safe iteration and extraction of serialized data, supporting multiple integer sizes and variable-length fields.

### STObject.cpp

Implements the `STObject` class, a core data structure for representing and manipulating serialized objects with various field types. Provides constructors, field accessors, mutators, serialization/deserialization, template application, comparison, and JSON conversion, ensuring field ordering and type safety.

### STArray.cpp

Implements the `STArray` class, representing an array of `STObject` elements. Supports construction, move semantics, serialization/deserialization, JSON/text conversion, sorting, and comparison, ensuring only valid objects are added.

### STBase.cpp

Implements the `STBase` class, a foundational class for serialized types. Provides basic construction, assignment, comparison, and field name management, serving as a base for more specific data structures.

### STVar.cpp

Implements the `STVar` class, a type-erased wrapper for various serialized types. Manages construction, destruction, copying, and moving of protocol objects, supporting stack and heap allocation, and enforces maximum nesting depth.

### SOTemplate.cpp

Implements the `SOTemplate` class, managing a template of fields for protocol objects. Constructs a list of unique and common fields, checks for valid and non-duplicate field indices, and provides efficient field lookup.

### STLedgerEntry.cpp

Implements the `STLedgerEntry` class, representing a ledger entry. Provides constructors, serialization, JSON conversion, text representation, and logic for handling ledger entry types and transaction threading.

### STAccount.cpp

Implements the `STAccount` class, representing an account field in serialized objects. Provides constructors, serialization logic, equivalence checks, and string conversion, managing account data and ensuring correct serialization.

### STAmount.cpp

Implements the `STAmount` class, representing and manipulating amounts of native XRP, IOUs, and MPT tokens. Provides arithmetic operations, serialization/deserialization, JSON conversion, and canonicalization logic, ensuring type safety and correct formatting.

### STNumber.cpp

Implements the `STNumber` class, representing a serialized numeric value with mantissa and exponent. Provides construction, serialization, deserialization, comparison, and conversion from JSON and string representations, with parsing logic for numbers.

### STBlob.cpp

Implements the `STBlob` class, representing a variable-length binary field. Provides methods for copying, moving, serializing, comparing blob data, and converting to hexadecimal, supporting default value checks.

### STVector256.cpp

Implements the `STVector256` class, representing a vector of 256-bit values. Provides serialization/deserialization, JSON conversion, comparison, and manipulation of vector contents, ensuring correct handling of binary data.

### STIssue.cpp

Implements the `STIssue` class, representing an issued asset or currency. Handles serialization, deserialization, JSON conversion, and equivalence checks for different issue types, ensuring consistency and correct construction.

### STCurrency.cpp

Implements the `STCurrency` class, representing a currency type in serialized objects. Provides constructors, serialization, JSON conversion, comparison, and utility methods for handling currency values, including validation from JSON.

### STPathSet.cpp

Implements the `STPathSet` and related classes, handling sets of payment paths for pathfinding and transaction routing. Provides serialization/deserialization, path equivalence checks, path addition, JSON conversion, and hashing for path elements.

### STParsedJSON.cpp

Implements parsing of JSON objects and arrays into protocol-specific data structures. Provides error handling for type mismatches, unknown fields, invalid data, and nesting depth, converting JSON input into strongly-typed protocol objects.

---

## Ledger and Transaction Processing

### TxFormats.cpp

Defines the `TxFormats` class, managing formats and required fields for transaction types. Establishes common transaction fields and uses macros to add specific formats, implemented as a singleton.

### LedgerFormats.cpp

Implements the `LedgerFormats` class, defining structure and required fields for ledger entry types. Uses macros to register entries with common and specific fields, following a singleton pattern.

### TxMeta.cpp

Implements the `TxMeta` class, managing transaction metadata such as affected ledger nodes, transaction results, and delivered amounts. Provides methods for setting/retrieving affected nodes and accounts, and serialization functions.

### STTx.cpp

Implements the `STTx` class, representing a serialized transaction. Provides construction, serialization, signature handling (single, multi, batch), validation checks, and JSON/database representations, with utility functions for transaction checks.

### STValidation.cpp

Implements the `STValidation` class, handling validation objects used in consensus. Provides methods for copying, moving, serializing, checking validity, extracting key fields, and managing validation formats, supporting both full and partial validations.

### InnerObjectFormats.cpp

Defines the `InnerObjectFormats` class, registering and managing formats of inner objects used in the ledger. Specifies required, optional, and default fields for each object type, providing methods to retrieve templates.

### Indexes.cpp

Implements functions for generating unique indices and keylets for ledger objects (accounts, offers, trust lines, tickets, escrows, NFTs, AMMs, etc.). Defines the `LedgerNameSpace` enum and provides hashing utilities for unique identifiers.

### Keylet.cpp

Implements the `Keylet::check` function, verifying if a ledger entry matches the expected type and key, with special cases for flexible validation.

### LedgerHeader.cpp

Implements serialization and deserialization for the `LedgerHeader` structure, providing methods to add fields to a serializer and reconstruct from serialized data.

---

## Account and Key Management

### AccountID.cpp

Implements functions and classes for handling AccountIDs, including Base58 encoding/decoding, parsing from strings, and calculating AccountIDs from public keys. Features an `AccountIdCache` for optimized lookups and utility functions for special accounts.

### PublicKey.cpp

Implements functionality for handling and verifying public keys, supporting secp256k1 and ed25519 types. Includes parsing, copying, comparing, signature verification, and utilities for hexadecimal/Base58 conversion and node ID calculation.

### SecretKey.cpp

Implements logic for handling secret keys, supporting secp256k1 and ed25519. Provides functions for generating, deriving, securely erasing keys, signing messages, and key pair generation, with Base58 parsing/encoding.

### Seed.cpp

Implements the `Seed` class and related functions for secure creation, parsing, and management of cryptographic seeds. Supports random generation, derivation from passphrases, parsing from various formats, and secure memory erasure.

---

## Error Handling and Utilities

### TER.cpp

Defines and implements functions for handling transaction engine result (TER) codes. Maps codes to string tokens and descriptions, providing utilities for error handling and messaging in transaction processing.

### ErrorCodes.cpp

Defines and manages error codes for the RPC interface. Provides a list of error codes with tokens, messages, and HTTP status codes, and functions for error information retrieval and JSON error responses.

### RPCErr.cpp

Defines utility functions for handling RPC errors, generating JSON error objects from error codes, and checking for errors in JSON results.

---

## AMM and Order Book Logic

### AMMCore.cpp

Implements core logic for Automated Market Maker (AMM) functionality. Provides functions for generating AMM liquidity pool token currencies, validating assets and amounts, determining auction slots, and checking feature enablement.

### Book.cpp

Implements utility functions for the `Book` class, including consistency checks, string conversion, stream output, and reversing input/output issues. Ensures valid currency pairs for order book operations.

### Quality.cpp

Implements the `Quality` class, representing exchange rates between assets. Provides constructors, increment/decrement operators, rounding, and functions for computing quality ceilings and composing/rounding qualities.

### QualityFunction.cpp

Implements the `QualityFunction` class, modeling and manipulating quality rates for order book and AMM calculations. Provides methods for initialization, combining qualities, and computing output amounts.

### Rate2.cpp

Implements utility functions for handling `Rate` objects, including conversion to `STAmount`, multiplication/division with optional rounding, and transfer fee conversion. Ensures no-ops at parity and valid input.

---

## NFT and Token Support

### NFTokenID.cpp

Implements functions for handling NFToken IDs, determining if a transaction can have an NFToken ID, extracting IDs from metadata, and inserting them into JSON responses. Focuses on NFT-related transaction types.

### NFTokenOfferID.cpp

Implements logic for handling NFToken offer IDs, determining if a transaction can have an offer ID, extracting from metadata, and inserting into JSON responses, with checks for transaction type and status.

### NFTSyntheticSerializer.cpp

Defines a function to insert synthetic NFT-related data (NFTokenID and NFTokenOfferID) into a JSON response based on transaction and metadata, using helper functions for extraction and insertion.

### XChainAttestations.cpp

Implements classes and logic for handling cross-chain attestations, defining data structures for attestations, serialization/deserialization, signature verification, equality checks, and container classes for managing attestations.

---

## Permissions and Rules

### Rules.cpp

Implements the `Rules` class, managing feature flags (amendments) enabled in a ledger. Provides mechanisms to check feature enablement, manage rule presets, compare rule sets, and handle NFT-related features, with thread-local transaction rule management.

### Permissions.cpp

Implements the `Permission` class, managing mappings between transaction types, permissions, and delegatability. Initializes maps using macros, provides query methods, and enforces constraints, implemented as a singleton.

---

## Cryptography and Hashing

### digest.cpp

Implements cryptographic hashers for RIPEMD-160, SHA-256, and SHA-512 using OpenSSL. Each hasher initializes the context, processes input, and produces the digest, providing essential hashing utilities.

### Sign.cpp

Implements cryptographic signing and verification functions for protocol objects. Provides methods to sign/verify `STObject` instances, utilities for multi-signature data, and uses serializers for signing.

---

## Versioning and Build Information

### BuildInfo.cpp

Implements versioning utilities, including functions to retrieve the version string, construct a full version string, encode the version into a 64-bit integer, and check compatibility. Handles parsing, encoding, and comparison of version numbers, including pre-release identifiers.

---

## Currency and Amount Utilities

### UintTypes.cpp

Implements functions for handling and converting currency codes. Provides utilities for conversion between `Currency` objects and strings, validation of ISO codes, and defines special currency constants.

### IOUAmount.cpp

Implements the `IOUAmount` class, handling non-XRP currency amounts with high precision. Provides normalization, arithmetic operations, string conversion, and precise ratio multiplication, supporting legacy and new number handling modes.

### MPTAmount.cpp

Implements the `MPTAmount` class, representing an amount with integer value and providing arithmetic and comparison operators, including a method for the minimum positive amount.

---

## Issue and Token Encoding

### Issue.cpp

Implements the `Issue` class and related functions for representing currency/issuer pairs. Provides methods for string/JSON conversion, consistency checks, handling native XRP vs. issued currencies, and error handling.

### tokens.cpp

Implements encoding and decoding of tokens using Base58, providing functions for various token types with checksums for integrity. Ensures type safety, error handling, and secure/efficient serialization.

---

*This template can be adapted for documenting other folders in the XRPL core library by following the same structure: grouping files by functionality, providing concise descriptions, and highlighting their roles within the protocol.*
```

"""

idea2 = """
```markdown
# XRPL Feature and Protocol Object Management

## Overview

XRPL (XRP Ledger) uses a macro-driven system to define and manage protocol features, transaction types, ledger entries, and serialized fields. This approach centralizes definitions, ensures consistency, and simplifies code generation for serialization, validation, and protocol evolution.

---

## 1. Feature Management

### Protocol Amendments

Features and fixes (protocol amendments) are defined using macros in `features.macro`:

- `XRPL_FEATURE(name, supported, vote)`: Registers a new protocol feature.
- `XRPL_FIX(name, supported, vote)`: Registers a protocol fix (for bug fixes).
- `XRPL_RETIRE(name)`: Marks an amendment as retired.

These macros generate code to track, vote on, and enforce amendments across the network. All amendments are listed in `xrpl/protocol/detail/features.macro`, and the total number is tracked in `Feature.h`.

---

## 2. Transaction Type Definitions (`transactions.macro`)

### Purpose

Defines all transaction types supported by XRPL using the `TRANSACTION` macro. Each transaction specifies a tag, numeric value, class name, delegation status, and a list of required/optional fields.

### Example

```cpp
TRANSACTION(ttPAYMENT, 0, Payment, Delegation::delegatable, ({
    {sfDestination, soeREQUIRED},
    {sfAmount, soeREQUIRED, soeMPTSupported},
    {sfSendMax, soeOPTIONAL, soeMPTSupported},
    {sfPaths, soeDEFAULT},
    {sfInvoiceID, soeOPTIONAL},
    {sfDestinationTag, soeOPTIONAL},
    {sfDeliverMin, soeOPTIONAL, soeMPTSupported},
    {sfCredentialIDs, soeOPTIONAL},
}))
```

**Explanation:**  
- `ttPAYMENT`: Transaction tag; `0`: numeric value; `Payment`: class name.
- `Delegation::delegatable`: Indicates the transaction can be delegated.
- Field list: Specifies which SFields are required, optional, or have special handling.

**Mechanics:**  
The macro expands to generate code for transaction processing, validation, and serialization. Adding or modifying transaction types is centralized and straightforward.

---

## 3. Ledger Entry Definitions (`ledger_entries.macro`)

### Purpose

Defines all ledger object types using the `LEDGER_ENTRY` macro. Each entry has a type code, numeric ID, class name, and a list of fields.

### Example

```cpp
LEDGER_ENTRY(ltOFFER, 0x006f, Offer, offer, ({
    {sfAccount,              soeREQUIRED},
    {sfSequence,             soeREQUIRED},
    {sfTakerPays,            soeREQUIRED},
    {sfTakerGets,            soeREQUIRED},
    {sfBookDirectory,        soeREQUIRED},
    {sfBookNode,             soeREQUIRED},
    {sfOwnerNode,            soeREQUIRED},
    {sfPreviousTxnID,        soeREQUIRED},
    {sfPreviousTxnLgrSeq,    soeREQUIRED},
    {sfExpiration,           soeOPTIONAL},
}))
```

**Explanation:**  
- `ltOFFER`: Ledger entry type; `0x006f`: unique code; `Offer`: class name.
- Field list: Defines the structure of an Offer object in the ledger.

**Mechanics:**  
Macros generate code for ledger serialization, deserialization, and validation. In files like `Indexes.cpp`, these definitions are used to compute unique keys for ledger objects (e.g., offers).

---

## 4. Serialized Field Definitions (`sfields.macro`)

### Purpose

Defines all possible fields (SFields) that can appear in transactions and ledger entries, mapping each to a type and unique code. Types correspond to C++ classes (e.g., `STAmount`, `STAccount`).

### Example

```cpp
TYPED_SFIELD(sfAmount, AMOUNT, 1)
TYPED_SFIELD(sfAccount, ACCOUNT, 1)
TYPED_SFIELD(sfSequence, UINT32, 4)
TYPED_SFIELD(sfTakerPays, AMOUNT, 4)
TYPED_SFIELD(sfTakerGets, AMOUNT, 5)
```

**Explanation:**  
- `sfAmount`: Field of type `AMOUNT` (handled by `STAmount`), code `1`.
- `sfAccount`: Field of type `ACCOUNT` (`STAccount`), code `1`.

**Mechanics:**  
Macro expansions generate SField objects used for serialization, deserialization, and validation. Each SField knows its type, code, and processing logic.

---

## 5. How These Components Work Together

- **Transactions:**  
  When a transaction is processed, its type and required fields are determined from `transactions.macro`. Each field's type and code come from `sfields.macro`.

- **Ledger Entries:**  
  Ledger objects (e.g., offers, escrows) are defined in `ledger_entries.macro`, with their fields referencing SFields. In `Indexes.cpp`, these definitions are used to compute unique keys for ledger objects.

- **SFields and Types:**  
  SFields are mapped to C++ types (e.g., `STAmount`, `STAccount`). This mapping ensures correct serialization and validation of protocol objects.

---

## 6. Summary Table

| Macro File             | Defines...                | Example Macro Call | Used For...                                 |
|------------------------|---------------------------|--------------------|---------------------------------------------|
| transactions.macro     | Transaction types         | TRANSACTION(...)   | Transaction processing, validation, ser/de  |
| ledger_entries.macro   | Ledger object types       | LEDGER_ENTRY(...)  | Ledger serialization, key computation       |
| sfields.macro          | Serialized fields (SField)| TYPED_SFIELD(...)  | Field type mapping, ser/de, validation      |

---

## Conclusion

XRPL's macro-driven system for defining features, transactions, ledger entries, and fields ensures maintainability, consistency, and ease of protocol evolution. By centralizing these definitions, the codebase can efficiently generate serialization, validation, and key computation logic, supporting robust and flexible protocol development.
```

"""

prompt = f"""
Combine the following ideas into a single markdown file. The goal is to create a comprehensive documentation file that explains some feature or functionality of the the rippled source code. The file should be structured and easy to read, with clear sections and explanations.
"""
client = AthenahClient("id", "dist", "rippled-ai-core", "v1", "gpt-4.1")
response = client.rag_prompt_v2(prompt, idea1 + idea2)
# print(response)
with open(
    "/Users/darkmatter/projects/transia/athena-ai/playgrounds/core_dev/final.md",
    "w",
) as f:
    f.write(response)
