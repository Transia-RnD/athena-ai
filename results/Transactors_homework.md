---

# XRPL Transactor System – Comprehensive Homework Assignment

## Instructions

- Answer all conceptual questions in your own words.
- For code questions, provide well-commented C++ code snippets.
- For testing/debugging questions, describe your approach and provide code where required.
- Submit your answers as a single PDF or markdown file, with code in code blocks.

---

## 1. Class Architecture & Extensibility

**a.** Describe the purpose of the `Transactor` class in the XRPL codebase. How does it facilitate extensibility for new transaction types?

**b.** Given the following partial class definition, explain the role of each method (constructor, `apply`, `preCompute`, `doApply`, static helpers):

```cpp
class Transactor {
protected:
    TER apply();
    explicit Transactor(ApplyContext& ctx);
    virtual void preCompute();
    virtual TER doApply() = 0;
    static XRPAmount minimumFee(Application& app, XRPAmount baseFee, Fees const& fees, ApplyFlags flags);
    // ... other members ...
};
```

**c.** Suppose you want to add a new transaction type `MyCustomTx`. Outline the steps and class structure you would use to implement this, leveraging the `Transactor` system.

---

## 2. Transaction Lifecycle

**a.** List and briefly describe each stage in the lifecycle of a transaction as it passes through the XRPL Transactor system, from submission to ledger application.

**b.** For each stage, identify at least one possible failure scenario and the mechanism by which the system handles it.

---

## 3. Pre-Application Checks

**a.** The Transactor system performs several pre-application checks. For each of the following, explain:
- What is being checked?
- Why is it important?
- What is the consequence of failure?

    - Fee check
    - Sequence check
    - Signature check (single and multi-sign)
    - Permission check

**b.** Write a C++ function that simulates the sequence check logic, including edge cases such as:
- Sequence too low (already used)
- Sequence too high (gaps)
- Sequence exactly correct

---

## 4. Fee, Sequence, Signature, and Permission Logic

**a.** Given the following static helper signatures, describe their purpose and how they are used in the transaction application process:

```cpp
static XRPAmount minimumFee(Application& app, XRPAmount baseFee, Fees const& fees, ApplyFlags flags);
static NotTEC checkSingleSign(AccountID const& idSigner, AccountID const& idAccount, std::shared_ptr<SLE const> sleAccount, Rules const& rules, beast::Journal j);
static NotTEC checkMultiSign(ReadView const& view, AccountID const& idAccount, STArray const& txSigners, ApplyFlags const& flags, beast::Journal j);
static TER checkPermission(ReadView const& view, STTx const& tx);
```

**b.** Write a test case for each of the following edge cases:
- Transaction with insufficient fee
- Transaction with an invalid single signature
- Transaction with a valid multi-signature but missing one required signer
- Transaction from an account lacking permission for the operation

---

## 5. Error Handling

**a.** Explain the difference between `TER`, `NotTEC`, and other error/result codes in the Transactor system. Why is it important to distinguish between them?

**b.** Given a transaction that fails due to an invalid sequence number, describe how the error is propagated and how a client would be informed.

**c.** Write a code snippet that demonstrates robust error handling for a transaction application, ensuring that all error cases are logged and returned appropriately.

---

## 6. Testing and Debugging

**a.** Design a unit test for the `ticketDelete` function, covering at least the following scenarios:
- Deleting a ticket that exists and is owned by the account
- Attempting to delete a ticket that does not exist
- Attempting to delete a ticket owned by another account

**b.** For each scenario, describe the expected result and how you would verify correctness.

**c.** Suppose a bug is reported: "Transactions with valid multi-signatures are sometimes rejected as invalid." Outline a debugging strategy, including which parts of the Transactor system you would inspect and what tests you would write.

---

## 7. Advanced: Extending and Hardening

**a.** Propose an extension to the Transactor system that would allow for transaction rate limiting per account. Describe the changes you would make to the class architecture and transaction lifecycle.

**b.** Write pseudocode for the rate limiting check, and describe how you would test for both normal and edge cases (e.g., just under the limit, at the limit, and exceeding the limit).

---

# Submission Checklist

- [ ] All conceptual questions answered
- [ ] All code questions answered with well-commented code
- [ ] All test and debugging questions answered with clear reasoning and code where required

---

**End of Assignment**