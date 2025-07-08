---

# XRPL Ledger Functionality: Comprehensive Homework Assignment

## Instructions

- Answer all questions and complete all coding tasks.
- Reference specific source code files and functions where required.
- Submit your code, test cases, and written explanations in a single repository or document.

---

## Part 1: Core Ledger Components

### 1.1 Ledger and LedgerInfo

**a.** Briefly describe the purpose of the `Ledger` and `LedgerInfo` classes.  
**b.** In `xrpld/app/ledger/Ledger.h`, identify and explain the role of at least three key fields in `LedgerInfo`.  
**c.** Write a function that validates the integrity of a `LedgerInfo` object, ensuring all required fields are present and correctly formatted. Include error handling for missing or malformed fields.

---

### 1.2 LedgerHolder and LedgerHistory

**a.** Explain the difference between `LedgerHolder` and `LedgerHistory` as found in `xrpld/app/ledger/LedgerHolder.h` and `xrpld/app/ledger/LedgerHistory.h`.  
**b.** Write a test that simulates a scenario where a requested ledger is not present in `LedgerHolder` but is available in `LedgerHistory`. Ensure your test covers the edge case where the ledger is missing from both.

---

### 1.3 LedgerMaster

**a.** What is the role of `LedgerMaster` (`xrpld/app/ledger/LedgerMaster.h`)?  
**b.** Write a code snippet that demonstrates how `LedgerMaster` manages the transition between open, closed, and validated ledgers.  
**c.** Describe how `LedgerMaster` enforces ledger immutability after validation.

---

### 1.4 InboundLedgers and InboundLedger

**a.** Describe the process of acquiring a missing ledger using `InboundLedgers` and `InboundLedger` (`xrpld/app/ledger/InboundLedgers.h`, `xrpld/app/ledger/InboundLedger.h`).  
**b.** Write a test that simulates a failed ledger acquisition due to network timeout. How does the system handle retries and error reporting?

---

### 1.5 LedgerCleaner

**a.** What is the purpose of `LedgerCleaner` (`xrpld/app/ledger/LedgerCleaner.h`)?  
**b.** Write a function that triggers a cleaning operation and handles any errors that may occur during the process.

---

## Part 2: Ledger Entry Types and Field Semantics

### 2.1 Ledger Entry Types

**a.** List and describe at least four different ledger entry types defined in the XRPL protocol (see `xrpl/protocol/` and `xrpl/protocol/TxFlags.h`).  
**b.** For each entry type, identify key fields and explain their semantics.

---

### 2.2 Protocol Field Codes

**a.** Explain the purpose of protocol field codes in XRPL (see `xrpl/protocol/ErrorCodes.h` and `xrpl/protocol/RPCErr.h`).  
**b.** Write a function that maps a protocol error code to a human-readable error message.

---

## Part 3: Ledger Acquisition, Validation, Storage, and Publication

### 3.1 Acquisition and Validation Flow

**a.** Using references to `xrpld/app/ledger/InboundLedgers.h`, `xrpld/app/ledger/LedgerMaster.h`, and `xrpld/app/consensus/RCLValidations.h`, describe the flow of ledger acquisition and validation from the moment a ledger is requested until it is validated.  
**b.** Identify and explain the role of at least two functions involved in this process.

---

### 3.2 Storage and Publication

**a.** Explain how ledgers are stored and published to the network (see `xrpld/app/ledger/LedgerMaster.h` and `xrpld/app/ledger/TransactionMaster.h`).  
**b.** Write a test that verifies a ledger is correctly stored and published, including edge cases where storage fails.

---

## Part 4: RPC/Query Handlers and Error Recovery

### 4.1 RPC/Query Handlers

**a.** Identify a function in `xrpld/rpc/detail/LegacyPathFind.h` or `xrpld/rpc/detail/RPCHelpers.h` that handles ledger queries.  
**b.** Write a test that queries a ledger by hash and handles the case where the ledger is not found.

---

### 4.2 Error Recovery and Cleaning

**a.** Describe how the system recovers from errors such as missing or corrupted ledgers (see `xrpld/app/ledger/LedgerCleaner.h` and `xrpld/app/ledger/InboundLedgers.h`).  
**b.** Write a function that attempts to recover a missing ledger and logs all recovery attempts and outcomes.

---

## Part 5: Immutability and State Management

### 5.1 Ledger Immutability

**a.** Explain how ledger immutability is enforced after validation (see `xrpld/app/ledger/Ledger.h` and `xrpld/app/ledger/LedgerMaster.h`).  
**b.** Write a test that attempts to modify a validated ledger and verify that the modification is rejected.

---

### 5.2 State Management

**a.** Describe how state transitions are managed between open, closed, and validated ledgers (see `xrpld/app/ledger/OpenLedger.h` and `xrpld/app/ledger/LedgerMaster.h`).  
**b.** Write a function that logs all state transitions for a given ledger.

---

## Submission Checklist

- [ ] All code and tests are included and pass.
- [ ] All written explanations reference the relevant source code files and functions.
- [ ] All edge cases and error handling are addressed.
- [ ] All parts of the assignment are complete.

---

**End of Assignment**