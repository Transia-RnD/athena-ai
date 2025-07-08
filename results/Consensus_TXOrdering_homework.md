---

# Homework: Consensus_TXOrdering in XRPL

## Instructions

- Answer all questions.  
- For code reading and conceptual questions, cite specific files and line numbers where possible.  
- For code writing, provide well-commented code and explain your design choices.  
- For testing/debugging, describe your approach and provide sample test cases or bug fixes.

---

## 1. **CanonicalTXSet Ordering and Tie-Breaking**

### a) **Conceptual (Code Reading)**
- Explain how `CanonicalTXSet` orders transactions.  
- What fields are used for tie-breaking when two transactions have the same account and sequence?  
- Reference the relevant code file(s) and line(s).

### b) **Code Writing**
- Write a function that inserts a batch of transactions into a `CanonicalTXSet` and returns the ordered list of transaction IDs.  
- Ensure your function handles the case where two transactions from the same account have the same sequence number but different transaction IDs.

### c) **Edge Case**
- What happens if two transactions from the same account with the same sequence and identical content are submitted?  
- How does the system prevent replay or duplication?  
- Reference the code and explain.

---

## 2. **Transaction Set Construction**

### a) **Code Reading**
- Describe how a transaction set is constructed for consensus.  
- Which classes and methods are involved in building the set from the open ledger?  
- Reference the relevant files and lines.

### b) **Code Writing**
- Implement a function that, given a set of pending transactions and a ledger state, constructs a valid transaction set for consensus, ensuring all per-account and global limits are respected.

---

## 3. **DisputedTx Lifecycle and Stalling**

### a) **Conceptual**
- What is a `DisputedTx`?  
- Describe its lifecycle from creation to resolution.  
- How does the system handle a transaction that is "stalled" in dispute?  
- Reference the relevant code.

### b) **Debugging**
- Suppose a `DisputedTx` never resolves and remains in the disputed set indefinitely.  
- List possible causes and propose code-level fixes or mitigations.

---

## 4. **checkConsensus Logic and Thresholds**

### a) **Code Reading**
- Summarize the logic of the `checkConsensus` function.  
- What thresholds are used to determine if consensus is reached, and how are they calculated?  
- Reference the code.

### b) **Code Writing**
- Write a test case that simulates a scenario where consensus is not reached due to insufficient agreement.  
- Show how the system responds and what logs or errors are produced.

---

## 5. **TxQ Ordering and Blockers**

### a) **Conceptual**
- Explain how the `TxQ` (Transaction Queue) orders transactions.  
- What are "blockers" in this context, and how are they handled?  
- Reference the code.

### b) **Code Writing**
- Write a function that, given a set of transactions and a current ledger state, identifies which transactions are blocked and which are ready to be applied.

---

## 6. **Per-Account Limits**

### a) **Code Reading**
- Where in the code are per-account transaction limits enforced?  
- What happens if an account submits more transactions than allowed?  
- Reference the code.

### b) **Code Writing**
- Write a test that submits transactions from a single account exceeding the per-account limit.  
- Verify that only the allowed number are processed and the rest are rejected or queued.

---

## 7. **Supporting Classes/Utilities**

### a) **Conceptual**
- List and briefly describe three supporting classes/utilities that are critical to the consensus transaction ordering process (e.g., `ApplyContext`, `TxDetails`, `FeeLevel64`).  
- Reference their definitions in the code.

### b) **Code Reading**
- For one of the above classes, explain how it interacts with the consensus process, citing specific methods and their roles.

---

## 8. **Comprehensive Debugging/Test-Case Design**

### a) **Debugging**
- Given a bug report: "Transactions from the same account are sometimes applied out of order during consensus."  
- List possible causes, referencing code files/lines, and propose a debugging plan.

### b) **Test-Case Design**
- Design a set of test cases (at least three) that would catch ordering, tie-breaking, and per-account limit bugs in the consensus transaction ordering process.  
- For each, describe the setup, expected outcome, and how it would be verified.

---

## Submission

- Submit your answers as a PDF or Markdown file.
- Include code snippets, references, and explanations as required.
- For code writing, include both the code and a brief explanation of your approach.

---

**End of Assignment**