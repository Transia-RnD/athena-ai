---

# Homework Assignment: Consensus_Amendments Deep Dive

## Instructions

- Answer all questions thoroughly. For code questions, submit compilable code and explain your approach.
- For debugging, describe the bug, its impact, and your fix.
- For conceptual and scenario-based questions, provide detailed, well-reasoned answers, referencing source code and documentation as needed.
- Cite specific files, classes, and functions from the codebase where relevant.

---

## 1. **AmendmentTable and AmendmentSet**

### 1.1 Code Writing

**Task:**  
Implement a method in `AmendmentTableImpl` that returns all amendments that have been supported by at least 60% of trusted validators in the last 256 ledgers, but are not yet enabled or in majority.  
- **Edge case:** Ensure your method handles the case where the validator set is very small (e.g., only 2 validators).

**File(s):** `AmendmentTable.cpp`, `AmendmentTable.h`

---

### 1.2 Debugging

**Task:**  
Given the following code snippet from the amendment voting logic, identify and fix the bug that could cause an amendment to be enabled prematurely if the validator set size drops suddenly due to a network partition.

```cpp
auto vote = std::make_unique<AmendmentSet>(rules, previousTrustedVotes_, lock);
if (vote->trustedValidations() >= vote->threshold()) {
    enableAmendment(amendmentID);
}
```

- Explain the bug and your fix.

---

### 1.3 Conceptual

**Question:**  
Explain the roles of `AmendmentTable`, `AmendmentSet`, and `TrustedVotes` in the amendment process. How do they interact during a typical consensus round?

---

### 1.4 Scenario

**Question:**  
Suppose a new amendment is proposed, but 10% of validators are running in standalone mode. How does this affect the amendment's path to majority and eventual activation? What are the operational risks?

---

## 2. **Amendment Voting and Ledger Application**

### 2.1 Code Writing

**Task:**  
Extend the amendment voting logic to support a "grace period" after an amendment loses majority, during which it cannot be re-proposed for majority status.  
- Implement this in the relevant class and describe how you would persist this state.

---

### 2.2 Debugging

**Task:**  
A bug is reported: after a network partition heals, two conflicting pseudo-transactions for the same amendment (one adding, one removing majority) are present in the ledger.  
- Identify the root cause and propose a fix to ensure amendment state transitions are consistent.

---

### 2.3 Conceptual

**Question:**  
Describe how pseudo-transactions are used to track amendment state in the ledger. Why are they necessary, and how are they constructed and applied?

---

### 2.4 Scenario

**Question:**  
If an amendment is enabled while a significant portion of the network is partitioned, what are the consequences for nodes that do not support the amendment? How does the system ensure safety and liveness?

---

## 3. **Persistence and Recovery**

### 3.1 Code Writing

**Task:**  
Implement logic to persist the set of enabled and vetoed amendments to disk, and to recover this state on startup.  
- Specify the file format and error handling strategy.

---

### 3.2 Debugging

**Task:**  
A student reports that after a crash, the node sometimes forgets which amendments were enabled.  
- Identify likely causes in the persistence logic and suggest robust solutions.

---

### 3.3 Conceptual

**Question:**  
Why is it critical to persist amendment state? What are the risks if this is not done correctly?

---

### 3.4 Scenario

**Question:**  
Describe the recovery process for a node that was offline for a week during which two amendments were enabled. How does it catch up and ensure it is in sync with the network?

---

## 4. **RPC/Admin Interface**

### 4.1 Code Writing

**Task:**  
Add an RPC command `amendment_status` that returns the current status (enabled, majority, vetoed, supported) of all known amendments, including those not supported by the local node.

---

### 4.2 Debugging

**Task:**  
A user reports that the `feature` RPC sometimes returns outdated information about amendment majority status.  
- Trace the code path and identify where caching or state update issues might occur.

---

### 4.3 Conceptual

**Question:**  
Discuss the security and operational considerations for exposing amendment state via the admin interface.

---

### 4.4 Scenario

**Question:**  
How should the admin interface behave if queried about an amendment the node does not recognize (e.g., due to running an old version)?

---

## 5. **Thread Safety and Concurrency**

### 5.1 Code Writing

**Task:**  
Audit the amendment voting and state transition code for thread safety.  
- Identify at least two critical sections and describe how you would protect them.

---

### 5.2 Debugging

**Task:**  
A rare crash occurs when two threads attempt to update the amendment state simultaneously.  
- Propose a fix and explain how you would test for race conditions.

---

### 5.3 Conceptual

**Question:**  
Why is thread safety particularly important in the context of consensus and amendment state? What are the potential consequences of a race condition here?

---

### 5.4 Scenario

**Question:**  
Suppose a node is running with a custom plugin that also modifies amendment state. What architectural safeguards should be in place to prevent corruption or inconsistency?

---

## 6. **Negative UNL and Unsupported Amendments**

### 6.1 Code Writing

**Task:**  
Modify the amendment voting logic to account for validators on the Negative UNL (i.e., temporarily disabled validators) so that their absence does not prevent amendments from reaching majority.

---

### 6.2 Debugging

**Task:**  
A bug is found where an unsupported amendment is enabled, causing the node to crash.  
- Trace the code path and suggest how to prevent this, both in code and operationally.

---

### 6.3 Conceptual

**Question:**  
Explain why there is no mechanism to disable or revoke an amendment once enabled. What are the implications for network upgrades and backward compatibility?

---

### 6.4 Scenario

**Question:**  
Describe the process and risks when a node encounters an enabled amendment it does not support. What should the node do, and what are the network-wide consequences?

---

## 7. **Source Code and Documentation Reference**

### 7.1 Code/Doc Reference

**Task:**  
For each of the following, provide the relevant source file(s) and documentation section(s):
- How amendments are proposed and tracked
- How majority is determined and persisted
- How pseudo-transactions are constructed and applied
- How the admin interface exposes amendment state

---

## Submission Checklist

- [ ] All code is compilable and tested.
- [ ] All debugging questions include a clear explanation and fix.
- [ ] All conceptual and scenario questions are answered in detail.
- [ ] All source code and documentation references are cited.

---

**End of Assignment**