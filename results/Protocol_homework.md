# XRPL Protocol Comprehensive Homework Assignment

**Instructions:**  
This assignment covers all major components of the XRPL Protocol. You are expected to write code, unit tests, and provide detailed explanations. Reference specific files and documentation as needed. Submit your code, test cases, and written answers in a well-organized repository or archive.

---

## Part 1: Protocol Buffers and gRPC

### 1.1 Adding a New gRPC Method

**Task:**  
Add a new gRPC method called `GetLedgerSummary` to the XRPL gRPC interface.

- Define the method in `xrp_ledger.proto` following naming conventions.
- Create `GetLedgerSummaryRequest` and `GetLedgerSummaryResponse` messages in a new proto file.
- Implement the handler in the appropriate file under `src/ripple/rpc/handlers/`.
- Register the method in `GRPCServerImpl::setupListeners()`.

**Edge Cases:**
- Ensure the handler returns a well-formed error if the requested ledger does not exist.
- Handle malformed requests (e.g., missing required fields).

**Unit Test:**
- Implement a test client (see `GrpcTxClient` in `Tx_test.cpp`) and write tests for:
  - Successful summary retrieval.
  - Requesting a non-existent ledger.
  - Sending a malformed request.

**References:**  
- [Protocol Buffers Language Guide](https://developers.google.com/protocol-buffers/docs/proto3)  
- `xrp_ledger.proto`, `Tx_test.cpp`

---

## Part 2: Core Protocol Classes

### 2.1 Serialization/Deserialization

**Task:**  
Write code that serializes and deserializes an `STObject` containing at least three fields, including an optional field.

- Demonstrate the use of `x[sfFoo]` and `x[~sfFoo]` for field access.
- Show what happens if a required field is missing during deserialization.

**Edge Cases:**
- Attempt to deserialize an object with an unknown field.
- Attempt to serialize an object with a missing required field.

**Unit Test:**
- Write tests for successful and failed (edge case) serialization/deserialization.

**References:**  
- `xrpl/protocol/STObject.h`, `xrpl/protocol/SField.h`

---

### 2.2 STVar and STIssue

**Task:**  
- Create an `STVar` that can hold either an `STAmount` or an `STAccount`.
- Write code to safely extract and use the value, handling the case where the type is not as expected.
- Create and compare two `STIssue` objects, demonstrating equality and ordering.

**Unit Test:**
- Test all code paths, including type mismatches.

**References:**  
- `xrpl/protocol/STVar.h`, `xrpl/protocol/STIssue.h`

---

## Part 3: Protocol Constants and Limits

### 3.1 Constants

**Task:**  
- List three protocol constants (e.g., maximum transaction size, minimum reserve).
- Write code that enforces one of these limits in a transaction validation function.

**Edge Cases:**
- Test the function with values at, above, and below the limit.

**References:**  
- `xrpl/protocol/Protocol.h`

---

## Part 4: Message Handling and Dispatch

### 4.1 Message Dispatch

**Task:**  
- Implement a message dispatch function that routes messages based on type.
- Handle the case where the message type is unknown.

**Edge Cases:**
- Pass a message with an invalid or unrecognized type.

**Unit Test:**
- Test dispatch for known and unknown types.

**References:**  
- `xrpl/protocol/Message.h` (or equivalent message type definitions)

---

## Part 5: Version Negotiation and Handshake

### 5.1 Version Negotiation

**Task:**  
- Write code that negotiates protocol version between two peers, given their supported version ranges.
- Handle negotiation failure (no compatible version).

**Edge Cases:**
- One peer supports no versions.
- Ranges do not overlap.

**Unit Test:**
- Test successful and failed negotiations.

**References:**  
- `xrpl/protocol/Protocol.h`

---

### 5.2 Handshake and Feature Negotiation

**Task:**  
- List all HTTP fields used in the XRPL handshake.
- Write code that validates the presence and format of each field.
- Simulate a handshake with a missing or malformed field and show the error handling path.

**References:**  
- XRPL handshake documentation, relevant code in handshake processing.

---

## Part 6: Protocol Message Types

### 6.1 Message Types

**Task:**  
- List all protocol message types defined in the codebase.
- For one message type, explain its structure and purpose.
- Write code to construct, serialize, and parse this message type.

**References:**  
- `xrpl/protocol/Message.h`, protocol documentation.

---

## Part 7: Supporting Utilities

### 7.1 Utilities

**Task:**  
- Use at least three supporting utilities (e.g., `strHex`, `safe_cast`, `base_uint`) in code that processes protocol data.
- Explain the purpose and correct usage of each utility.

**References:**  
- `xrpl/basics/StringUtilities.h`, `xrpl/basics/safe_cast.h`, `xrpl/basics/base_uint.h`

---

## Part 8: Code Analysis and Explanation

### 8.1 Protocol Feature Enforcement

**Task:**  
- Choose one protocol feature (e.g., transaction signature validation, field presence enforcement, message size limits).
- Explain, with code references, how this feature is enforced in the codebase.
- Discuss what would happen if this enforcement were removed or bypassed.

---

## Submission Checklist

- [ ] All code files and unit tests.
- [ ] Written answers and explanations.
- [ ] References to files and documentation.
- [ ] Clear organization and comments.

---

**Grading Rubric:**  
- Correctness and completeness of code (40%)  
- Quality and coverage of unit tests (20%)  
- Depth and clarity of explanations (20%)  
- Handling of edge cases and error paths (20%)  

---

**Good luck!**