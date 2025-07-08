---

# Homework Assignment: XRPL Consensus_Validations Subsystem

**Instructions:**  
This assignment covers all major aspects of the `Consensus_Validations` subsystem. You will be required to write code, analyze and debug provided snippets, answer conceptual questions, and reason about the XRPL source code. Reference the relevant files (e.g., `RCLValidations.h/cpp`, `Validations.h/cpp`, `LedgerTrie.h`, etc.) as needed.

---

## Part 1: Core Functionality Implementation

### 1.1 Validation Timing Checks

**Task:**  
Implement a function in C++ that determines if a given validation is "fresh" based on the `validationFRESHNESS` parameter in `ValidationParms`. The function should take the validation's timestamp and the current time as arguments.

```cpp
// In Validations.h
bool isValidationFresh(
    std::chrono::system_clock::time_point validationTime,
    std::chrono::system_clock::time_point now,
    const ValidationParms& parms);
```

- Write the implementation.
- Write a unit test that checks the function for fresh, stale, and borderline cases.

---

### 1.2 Sequence Enforcement

**Task:**  
Extend the validation logic to ensure that sequence numbers never regress for a given validator. If a validation arrives with a sequence number less than or equal to the last seen from that validator, it should be ignored.

- Implement this logic in a function.
- Write a test that simulates a validator sending sequence numbers: 10, 11, 9, 12. Ensure only the correct ones are accepted.

---

### 1.3 Trust Management

**Task:**  
Implement a function that checks if a given public key is in the current trusted validator list. Assume you have access to a `ValidatorList` object.

```cpp
bool isTrustedValidator(
    ripple::PublicKey const& pubKey,
    ValidatorList const& validatorList);
```

- Write the implementation.
- Write a test that checks both trusted and untrusted keys.

---

### 1.4 Negative UNL Scoring

**Task:**  
Write a function that, given a set of validations and the current Negative UNL, returns the number of trusted validators that are currently on the Negative UNL.

- Implement the function.
- Write a test that covers the case where some, all, or none of the trusted validators are on the Negative UNL.

---

## Part 2: Edge Case Handling

### 2.1 Clock Skew

**Scenario:**  
A validator's clock is 2 minutes ahead of the network. Write a test that simulates receiving a validation with a future timestamp. Modify your `isValidationFresh` logic to handle this edge case gracefully.

- Should the validation be accepted, rejected, or flagged? Justify your answer.

---

### 2.2 Sequence Number Regressions

**Scenario:**  
A validator restarts and replays old validations. Write a test that simulates this and ensure your sequence enforcement logic from 1.2 handles it.

---

### 2.3 Conflicting Validations

**Scenario:**  
A trusted validator sends two validations for the same ledger sequence but with different ledger hashes.

- Write a function that detects this conflict.
- Write a test that simulates this scenario.

---

### 2.4 Thread Safety Issues

**Scenario:**  
Multiple threads are adding validations simultaneously. Identify potential thread safety issues in the validation storage code (e.g., use of `std::mutex`). Propose and implement a fix.

---

### 2.5 Error Handling

**Scenario:**  
A validation arrives with a malformed signature or missing fields.

- Write code that detects and handles these errors.
- Write a test that covers these cases.

---

## Part 3: Debugging Exercises

### 3.1 Bug Hunt

**Given Code Snippet:**

```cpp
// Provided code
std::unordered_map<PublicKey, uint32_t> lastSeq;
void addValidation(PublicKey const& pk, uint32_t seq) {
    if (lastSeq[pk] < seq) {
        lastSeq[pk] = seq;
        // process validation
    }
}
```

**Task:**  
Identify and fix any bugs in the above code, especially regarding default-initialized values and sequence enforcement.

---

### 3.2 Deadlock Diagnosis

**Scenario:**  
A deadlock occurs when two threads try to add validations and update the trusted list at the same time.

- Identify the cause based on the use of mutexes in the codebase.
- Propose a solution to avoid deadlocks.

---

## Part 4: Conceptual and Code-Based Questions

### 4.1 Enums and Flags

- List and explain any enums or flags used in the validation process (e.g., validation types, trust flags).
- How are these used to control validation logic?

---

### 4.2 Data Structures

- Describe the main data structures used to store validations (e.g., `aged_unordered_map`, `LedgerTrie`).
- Why are these structures chosen? What are their advantages?

---

### 4.3 Inter-Module Relationships

- Explain how the `Consensus_Validations` subsystem interacts with other modules such as `LedgerMaster`, `ValidatorList`, and `NetworkOPs`.
- Give an example of a function call or data flow between these modules.

---

### 4.4 Negative UNL Process

- Describe the Negative UNL process and its purpose.
- How does the system ensure that validators on the Negative UNL do not affect consensus?
- Reference the relevant code files and functions.

---

## Part 5: Source Code Reference

For each of your answers above, **cite the relevant source code files and functions** (e.g., `RCLValidations.cpp`, `Validations.cpp`, `LedgerTrie.h`, etc.) where the logic is implemented or should be implemented.

---

**Submission:**  
- Submit your code files, test cases, and written answers.
- Clearly indicate which part of the assignment each file or answer corresponds to.
- Ensure your code compiles and tests pass.

---

**Grading Rubric:**  
- Correctness and completeness of code (40%)
- Thoroughness in edge case handling (20%)
- Quality of debugging and explanations (15%)
- Depth of conceptual answers (15%)
- Proper referencing of source code (10%)

---

**End of Assignment**