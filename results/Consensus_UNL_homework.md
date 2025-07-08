---

# Homework Assignment: Consensus_UNL and Negative UNL

## Overview

This assignment will test your understanding of the **Consensus_UNL** and **Negative UNL** mechanisms in the Ripple codebase. You will be required to write code, debug scenarios, answer conceptual questions, and reference specific source code files and functions.

**Files of interest:**
- `xrpld/app/consensus/RCLValidations.h`
- `xrpld/app/ledger/Ledger.h`
- `xrpld/app/misc/NegativeUNLVote.h`
- `xrpld/app/misc/NegativeUNLVote.cpp`
- `xrpld/shamap/SHAMapItem.h`

---

## Part 1: Code Writing Tasks

### 1.1 Implementing Negative UNL Voting Logic

**Task:**  
Write a function that, given a set of validator scores and the current Negative UNL, determines which validators should be candidates for disabling and which for re-enabling. Use the watermarks and logic as described in the `NegativeUNLVote` class.

**Requirements:**
- Use the constants: `negativeUNLLowWaterMark`, `negativeUNLHighWaterMark`.
- Ensure you do not add a validator to disable if it is already in the Negative UNL or is a new validator.
- Ensure you do not re-enable a validator unless it is in the Negative UNL.
- **Edge case:** What happens if all validators are already in the Negative UNL?

**Reference:**  
See `NegativeUNLVote::doVoting` and the candidate selection logic.

---

### 1.2 Adding a Negative UNL Transaction

**Task:**  
Write code to add a `ttUNL_MODIFY` transaction to a SHAMap, using the `NegativeUNLVote::addTx` function. Demonstrate both disabling and re-enabling a validator.

**Requirements:**
- Use the correct fields: `sfUNLModifyDisabling`, `sfLedgerSequence`, `sfUNLModifyValidator`.
- Handle the case where adding the transaction to the SHAMap fails.

**Reference:**  
See `NegativeUNLVote::addTx` in `NegativeUNLVote.cpp`.

---

### 1.3 Edge Case: Maximum Negative UNL Size

**Task:**  
Write a function that checks if adding a new validator to the Negative UNL would exceed the maximum allowed size (`negativeUNLMaxListed`). If so, prevent the addition.

**Requirements:**
- Use the constant `negativeUNLMaxListed`.
- Assume you have access to the current UNL size and Negative UNL size.

**Reference:**  
See the `NegativeUNLVote` class definition.

---

## Part 2: Debugging and Testing Scenarios

### 2.1 Debugging: Incorrect Candidate Selection

**Scenario:**  
A bug report states that validators are being re-enabled even though their scores are below the high watermark.

**Task:**  
- Identify which part of the code could cause this.
- Suggest a fix.

**Reference:**  
See the candidate selection logic in `NegativeUNLVote::doVoting`.

---

### 2.2 Testing: UNL Changes

**Scenario:**  
The UNL changes between ledgers. Some validators are removed from the UNL but remain in the Negative UNL.

**Task:**  
- Write a test case to ensure that such validators are considered for re-enabling.
- Explain why this is necessary.

**Reference:**  
See the logic for re-enabling candidates when `toReEnableCandidates` is empty.

---

### 2.3 Edge Case: All Validators Disabled

**Scenario:**  
All validators are in the Negative UNL.

**Task:**  
- What should the system do in this case?
- Write a test to ensure the system does not attempt to disable more validators.

---

## Part 3: Conceptual and Architectural Questions

### 3.1 Purpose of Negative UNL

**Question:**  
Explain the purpose of the Negative UNL in the consensus process. How does it improve network robustness?

---

### 3.2 Watermarks and Voting Thresholds

**Question:**  
Describe the role of `negativeUNLLowWaterMark`, `negativeUNLHighWaterMark`, and `negativeUNLMinLocalValsToVote` in the Negative UNL voting process. Why are these thresholds important?

---

### 3.3 Transaction Construction

**Question:**  
What is the purpose of the `ttUNL_MODIFY` transaction? How is it constructed and added to the ledger?

---

### 3.4 Architectural Integration

**Question:**  
How does the Negative UNL mechanism interact with the main consensus process? Reference the relevant classes and functions.

---

## Part 4: Source Code Reference

For each of the above tasks and questions, **cite the specific file and function** you would use or modify. For example:

- For candidate selection: `NegativeUNLVote::doVoting` in `NegativeUNLVote.cpp`
- For adding a transaction: `NegativeUNLVote::addTx` in `NegativeUNLVote.cpp`
- For constants: `NegativeUNLVote` class in `NegativeUNLVote.h`

---

## Submission Instructions

- Submit your code as `.cpp` files.
- Submit your answers to conceptual questions in a separate document.
- For each code task, include a comment referencing the relevant source file and function.
- For each test, describe the expected outcome.

---

**End of Assignment**