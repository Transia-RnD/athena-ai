---

# Homework Assignment: Consensus_Amendments Deep Dive

**Instructions:**  
Answer each question thoroughly. Reference specific files, classes, or functions as requested. Where code is required, ensure it is well-commented. For scenario and design questions, justify your reasoning.

---

## 1. **Code Reading: Amendment State Management**

**a.**  
Examine the function signature and implementation of `readAmendments` in `Amendments.cpp`.  
- What is the purpose of the `callback` parameter?  
- How does the function handle amendments that are missing a name or vote in the database?

**b.**  
In `Amendments.h`, what is the role of the `AmendmentVote` enum? How is it used in the amendment voting process?

---

## 2. **Short Answer: Voting and Consensus Integration**

**a.**  
Describe the process by which amendment votes are collected and tallied during consensus. Reference the `doVoting` method signature and its parameters.

**b.**  
What is the significance of the `majorityAmendments_t` type in the voting process? Where is it used?

---

## 3. **Code Writing: Ledger Application**

**a.**  
Write a function (in C++ pseudocode) that applies a newly enabled amendment to the ledger state. Your function should:
- Accept the current ledger and a set of enabled amendments.
- Update the ledger to reflect the new amendment.
- Log the change.

Reference the relevant interfaces in `Ledger.h` and `Amendments.h`.

---

## 4. **Scenario Analysis: Persistence and Recovery**

**a.**  
Suppose the node crashes immediately after an amendment is enabled but before the change is persisted to the database.  
- What mechanisms are in place to ensure amendment state consistency after restart?  
- Reference the relevant code in `Amendments.cpp` and any database interaction functions.

---

## 5. **Design/Architecture: RPC/Admin Interfaces**

**a.**  
Review the admin RPC interface for viewing and voting on amendments (see `RPCHandler.cpp` and `Amendments.cpp`).  
- Propose an extension to the RPC interface that allows querying the voting history for a specific amendment.  
- What data structures and code changes would be required to support this feature?

---

## 6. **Short Answer: Operational Consequences**

**a.**  
What are the operational consequences if a validator fails to apply an enabled amendment at the correct ledger sequence?  
- Reference the consensus and ledger application flow.

---

## 7. **Code Reading: Edge Cases**

**a.**  
In `Amendments.cpp`, how does the code handle the case where an amendment is enabled but not supported by the local node?  
- What are the consequences for consensus participation?

---

## 8. **Scenario Analysis: Standalone Mode**

**a.**  
Describe how amendment voting and application behave in standalone mode.  
- Reference the `setStandAlone()` method and any related logic in `Consensus_Amendments.cpp`.

---

## 9. **Code Writing: Negative UNL Interactions**

**a.**  
Write a code snippet that demonstrates how the Negative UNL (Unique Node List) could affect amendment voting.  
- Assume you have access to the set of trusted validators and the Negative UNL list.
- Show how you would exclude Negative UNL validators from the amendment vote tally.

---

## 10. **Design/Architecture: End-to-End Amendment Lifecycle**

**a.**  
Draw (or describe in detail) the end-to-end lifecycle of an amendment from proposal, through voting, to activation and persistence.  
- Reference the key classes and methods involved (e.g., `processTrustedProposal`, `doVoting`, `voteAmendment`, `readAmendments`, ledger application).
- Highlight where consensus, persistence, and RPC/admin interfaces interact.

---

**Submission:**  
Submit your answers as a PDF or Markdown file. Include code snippets and diagrams as appropriate. Be sure to reference specific files, classes, and methods in your answers.

---

**Grading Rubric:**  
- **Code Reading/Short Answer:** 2 points each  
- **Code Writing/Scenario/Design:** 4 points each  
- **Total:** 30 points

---

**End of Assignment**