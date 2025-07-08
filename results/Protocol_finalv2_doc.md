---

# XRPL Protocol: Serialization, Field Codes, and Canonical Binary Format

This section expands the protocol material to include precise, code-grounded details on how to serialize transactions, use field codes, and apply the canonical serialization format in the XRP Ledger (XRPL).

---

## Table of Contents

- [Serialization of Transactions and Protocol Objects](#serialization-of-transactions-and-protocol-objects)
- [Optional and Default Fields ("Type Magic")](#optional-and-default-fields-type-magic)
- [Protocol-level Limits and Constraints](#protocol-level-limits-and-constraints)
- [Handling of Unknown or Extra Fields](#handling-of-unknown-or-extra-fields)
- [Field Codes and Field IDs](#field-codes-and-field-ids)
- [Canonical Field Order](#canonical-field-order)
- [Internal Binary Format for Each Type](#internal-binary-format-for-each-type)
- [Length Prefixing and Nested Fields](#length-prefixing-and-nested-fields)
- [Type List](#type-list)
- [Serialization Format: Field-by-Field](#serialization-format-field-by-field)
- [Field Inclusion/Exclusion in Signing](#field-inclusionexclusion-in-signing)
- [Protocol Buffer Usage in Overlay Networking](#protocol-buffer-usage-in-overlay-networking)
- [References](#references)
- [Summary Table: Serialization Process](#summary-table-serialization-process)

---

## Serialization of Transactions and Protocol Objects

- The XRPL uses a canonical binary format for transactions, ledger entries, and other protocol objects.
- This format is required for digital signatures and for peer-to-peer communication between servers.
- JSON is used for API communication, but **all signing and consensus-critical operations use the binary format**.

### Serialization Steps

To serialize a transaction (or any protocol object):

1. **Ensure all required fields are present**, including auto-fillable fields (e.g., `Sequence`, `Fee`, `SigningPubKey`).
2. **Convert each field's value to its internal binary format** (see [Type List](#type-list)).
3. **Sort fields in canonical order** (see [Canonical Field Order](#canonical-field-order)).
4. **Prefix each field with its Field ID** (see [Field IDs](#field-ids)).
5. **Concatenate all fields (with prefixes) in sorted order** to produce the final binary blob.

- For signing, hash the binary blob with the appropriate prefix (`0x53545800` for single-signing, `0x534D5400` for multi-signing).
- After signing, re-serialize the transaction with the `TxnSignature` field included.

---

## Optional and Default Fields ("Type Magic")

- XRPL serialization supports both required and optional fields, as defined in the field templates (`SOTemplate`, `sfields.macro`).
- **Optional fields** are omitted from the binary serialization if not present in the object. They are not encoded with a default value.
- The codebase uses "type magic" for field access:
    - `x[sfFoo]` returns the value of `Foo` if it exists, or the default value if it doesn't.
    - `x[~sfFoo]` returns the value of `Foo` if it exists, or nothing if it doesn't.
    - Assigning with `x[~sfFoo] = y[~sfFoo]` copies the value if present, or omits the field if absent.
- This ensures that absent optional fields are not serialized, and only present fields appear in the binary format.

---

## Protocol-level Limits and Constraints

The XRPL protocol enforces various limits and constraints on serialized objects and fields. These are defined in the codebase (see `Protocol.h`) and include:

- **Transaction size:** Minimum: 32 bytes (`txMinSizeBytes`), Maximum: 1 megabyte (`txMaxSizeBytes`)
- **Directory node entries:** Maximum: 32 entries per node (`dirNodeMaxEntries`)
- **Directory node pages:** Maximum: 262,144 pages (`dirNodeMaxPages`)
- **Token URI length:** Maximum: 256 bytes (`maxTokenURILength`)
- **DID Document length:** Maximum: 256 bytes (`maxDIDDocumentLength`)
- **Offer removal limits:** Unfunded: 1000, Expired: 256
- **Oversize metadata cap:** 5200 bytes (`oversizeMetaDataCap`)
- **Other limits:** See `Protocol.h` for additional constraints on arrays, fields, and operational caps.

Implementers must ensure that serialized objects and fields do not exceed these protocol-level limits.

---

## Handling of Unknown or Extra Fields

- The XRPL enforces strict templates for each transaction and ledger entry type (see `SOTemplate`, `transactions.macro`, `ledger_entries.macro`).
- **Unknown or extra fields** (fields not defined in the template for the object type) are not serialized and are ignored.
- The codebase enforces this at serialization time: only fields present in the template are included in the binary output.
- This ensures protocol compatibility and prevents the inclusion of unintended or unsupported fields.

---

## Field Codes and Field IDs

### Field Codes

- Each field is defined by a **type code** and a **field code**.
- Type codes are assigned to each data type (e.g., UInt32, Amount, AccountID).
- Field codes are unique within each type and are used to order fields of the same type.

### Field IDs

- The **Field ID** is a compact encoding of the type code and field code, used as a prefix for each field in the binary format.
- The size of the Field ID is 1–3 bytes, depending on the values:
    - **Type code < 16, Field code < 16:** 1 byte (high 4 bits: type, low 4 bits: field)
    - **Type code >= 16 or Field code >= 16:** 2 or 3 bytes (see table below)

|                  | Type Code < 16, Field Code < 16 | Type Code >= 16, Field Code < 16 | Type Code < 16, Field Code >= 16 | Type Code >= 16, Field Code >= 16 |
|------------------|---------------------------------|-----------------------------------|-----------------------------------|-------------------------------------|
| **Bytes**        | 1                               | 2                                 | 2                                 | 3                                   |

- **Do not sort by Field ID bytes**; always sort by (type code, field code) tuple.

---

## Canonical Field Order

- Fields are sorted first by **type code**, then by **field code**.
- This order is critical for signature validity and protocol compatibility.
- Type codes and field codes are defined in the XRPL source (`SField.h`, `sfields.macro`) and in the [definitions file](https://github.com/XRPLF/xrpl.js/blob/main/packages/ripple-binary-codec/src/enums/definitions.json).

---

## Internal Binary Format for Each Type

See the [Type List](#type-list) for all types, their codes, and serialization rules.

### Examples

- **UInt32**: 4 bytes, big-endian.
- **Amount**: 8 bytes for XRP, 8+20+20 bytes for tokens (see [Amount Fields](#amount-fields)).
- **AccountID**: 20 bytes, length-prefixed if top-level field.
- **Blob**: Length-prefixed, arbitrary bytes.
- **STArray**: Sequence of objects, each with its own Field ID, terminated by Array End Field ID (`0xf1`).
- **STObject**: Sequence of fields in canonical order, terminated by Object End Field ID (`0xe1`).

---

## Length Prefixing and Nested Fields

- Some types (e.g., Blob, AccountID, Vector256) are **length-prefixed**.
- The length prefix is 1–3 bytes, depending on the size:
    - 0–192 bytes: 1 byte
    - 193–12480 bytes: 2 bytes
    - 12481–918744 bytes: 3 bytes
- **Length prefixing is only applied when the field is not nested inside another serialized type.**
    - For example, `AccountID` is length-prefixed when it is a direct/top-level field of an object, but **not** when nested inside another type (such as `Amount.issuer`).
    - "Top-level" means the field is a direct member of the serialized object, not a subfield of another serialized type.

---

## Type List

| Type Name     | Type Code | Bit Length | Length-prefixed? | Description    |
|:--------------|:----------|:-----------|:-----------------|----------------|
| AccountID     | 8         | 160        | Yes              | 20 bytes, length-prefixed if direct field. |
| Amount        | 6         | 64/384     | No               | 8 bytes for XRP, 8+20+20 for tokens. |
| Blob          | 7         | Variable   | Yes              | Arbitrary bytes, length-prefixed. |
| Hash128       | 4         | 128        | No               | 16 bytes. |
| Hash160       | 17        | 160        | No               | 20 bytes. |
| Hash256       | 5         | 256        | No               | 32 bytes. |
| PathSet       | 18        | Variable   | No               | See [PathSet Fields](#pathset-fields). |
| STArray       | 15        | Variable   | No               | Array of objects, terminated by Array End. |
| STIssue       | 24        | 160/320    | No               | 20 or 40 bytes. |
| STObject      | 14        | Variable   | No               | Object, terminated by Object End. |
| UInt8         | 16        | 8          | No               | 1 byte. |
| UInt16        | 1         | 16         | No               | 2 bytes. |
| UInt32        | 2         | 32         | No               | 4 bytes. |
| UInt64        | 3         | 64         | No               | 8 bytes. |
| Vector256     | 19        | Variable   | Yes              | Array of 32-byte hashes, length-prefixed. |
| XChainBridge  | 25        | Variable   | No               | See [XChainBridge Fields](#xchainbridge-fields). |

---

## Serialization Format: Field-by-Field

### UInt Fields

- **UInt8/16/32/64**: Big-endian unsigned integer, no length prefix.

### AccountID

- 20 bytes, length-prefixed (prefix is always `0x14` for 20 bytes) if a direct field of the object.
- No length prefix when nested (e.g., in Amount.issuer).

### Amount

- **XRP**: 8 bytes, most significant bit 0, next bit 1 for positive, remaining 62 bits for value.
- **Token**: 8 bytes (see [Token Amount Format](#token-amount-format)), followed by 20 bytes currency code, 20 bytes issuer.

### Blob

- Length-prefixed, arbitrary bytes.

### STArray

- Each element: Field ID + serialized object.
- End: Array End Field ID (`0xf1`), no contents.

### STObject

- Members in canonical order.
- Each: Field ID + value.
- End: Object End Field ID (`0xe1`), no contents.

### PathSet

- 1–6 paths, each 1–8 steps.
- Each step: type byte + fields (account, currency, issuer).
- Path end: `0xff` (more paths) or `0x00` (end).

### XChainBridge

- 4 parts: locking chain door (length-prefixed AccountID), locking chain asset (STIssue), issuing chain door (length-prefixed AccountID), issuing chain asset (STIssue).

---

## Field Inclusion/Exclusion in Signing

- Only fields marked as **signing fields** (see `SField.h`, `sfields.macro`, and the definitions file) are included in the signing hash.
- The `TxnSignature` field is always excluded from signing.
- Other fields may also be excluded if not marked as signing fields.
- When preparing a transaction for signing, include only the fields marked as signing fields in the binary blob to be hashed.

---

## Protocol Buffer Usage in Overlay Networking

- **Peer-to-peer overlay messages** in XRPL are serialized using **Google Protocol Buffers**.
    - See `src/xrpld/overlay/README.md`, `src/xrpld/overlay/detail/ProtocolMessage.h`, and `include/xrpl/protocol/messages.h`.
- This applies to all protocol messages exchanged between peers at the overlay network layer.
- Implementers working at the protocol level should refer to the relevant `.proto` files and generated code for message formats.

---

## References

- [SField.h](https://github.com/XRPLF/rippled/blob/master/include/xrpl/protocol/SField.h)
- [sfields.macro](https://github.com/XRPLF/rippled/blob/master/include/xrpl/protocol/detail/sfields.macro)
- [STObject.cpp](https://github.com/XRPLF/rippled/blob/develop/src/ripple/protocol/impl/STObject.cpp)
- [Protocol.h](https://github.com/XRPLF/rippled/blob/master/include/xrpl/protocol/Protocol.h)
- [definitions.json](https://github.com/XRPLF/xrpl.js/blob/main/packages/ripple-binary-codec/src/enums/definitions.json)
- [Serialization HTML Reference](serialization.html)
- [Overlay Protocol README](https://github.com/XRPLF/rippled/blob/master/src/ripple/overlay/README.md)

---

## Summary Table: Serialization Process

| Step | Action |
|------|--------|
| 1    | Ensure all required fields are present (see transaction/ledger entry definitions) |
| 2    | Convert each field to its internal binary format (see [Type List](#type-list)) |
| 3    | Sort fields by (type code, field code) (see [Canonical Field Order](#canonical-field-order)) |
| 4    | Prefix each field with its Field ID (see [Field IDs](#field-ids)) |
| 5    | Concatenate all fields in order to produce the binary blob |

---

**All statements above are strictly grounded in the provided documentation and source code.**