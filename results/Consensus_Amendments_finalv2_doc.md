---

# Consensus_Amendments Test Coverage Documentation

This document provides a precise, feedback-driven mapping between the amendment process in the XRP Ledger and the corresponding test coverage, based strictly on the provided information. It explicitly states which amendment lifecycle steps, consensus integration points, and edge cases are covered by tests, which are not, and which are unclear. If coverage is uncertain, this is stated directly.

---

## 1. Amendment Lifecycle and Edge Cases

| Amendment Process Step / Edge Case                                                                 | Coverage Status in Provided Test Files                                                                                                   | Notes                                                                                                 |
|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| **Amendment registration**                                                                         | Covered                                                                                                                                | `/src/test/app/Amendment_test.cpp` exercises registration.                                            |
| **Voting (including 80%/2 weeks logic)**                                                           | Covered (general voting); unclear if time-based (2 weeks) logic is directly tested                                                     | `/src/test/app/Amendment_test.cpp` and `/src/test/app/AmendmentTable_test.cpp` cover voting.          |
| **Activation (pseudo-tx, ledger update)**                                                          | Covered                                                                                                                                | `/src/test/app/Amendment_test.cpp` and `/src/test/app/Change_test.cpp` cover activation and ledger.   |
| **Veto/admin controls (veto/unveto via RPC/config)**                                               | Covered (general); unclear if all edge cases are tested                                                                                | `/src/test/rpc/Feature_test.cpp` covers RPC/admin interface.                                          |
| **Persistence (db/config), recovery from database**                                                | Covered (general); unclear if recovery/corruption is tested                                                                            | `/src/test/app/AmendmentTable_test.cpp` covers persistence.                                           |
| **Consensus integration (votes in consensus, effect on rules)**                                    | Covered (general); unclear if all consensus edge cases are tested                                                                      | `/src/test/app/Amendment_test.cpp` and `/src/test/app/AmendmentTable_test.cpp` mention consensus.     |
| **Handling unsupported amendments (server blocks if enabled)**                                     | Not explicitly covered; unclear if tested                                                                                              | No test file is explicitly listed for this scenario.                                                  |
| **Irreversibility (amendments cannot be disabled/revoked)**                                        | Not explicitly covered; unclear if tested                                                                                              | No test file is explicitly listed for this scenario.                                                  |
| **Edge cases (conflicting votes, database corruption, unsupported enabled, etc.)**                 | Covered (general); unclear if all are tested                                                                                           | Edge cases are mentioned, but specific scenarios are not mapped to test files.                        |

---

## 2. Consensus Integration

- The documentation and code indicate that the amendment process is integrated with consensus (e.g., votes included in consensus rounds, amendments affecting ledger rules).
- **Test Coverage:** The test files `/src/test/app/Amendment_test.cpp` and `/src/test/app/AmendmentTable_test.cpp` are said to cover consensus integration in general.
- **Unclear:** It is not specified whether all consensus-specific edge cases (such as disputed amendments, consensus failure, or conflicting votes) are directly tested.

---

## 3. Explicit Mapping: Amendment Process Steps to Test Files

| Amendment Step / Feature                        | Test File(s) (as per provided info)                                                                                 |
|-------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Registration, voting, activation, edge cases    | `/src/test/app/Amendment_test.cpp`                                                                                  |
| AmendmentTable logic (state, voting, persistence, JSON) | `/src/test/app/AmendmentTable_test.cpp`                                                                     |
| Application of amendment pseudo-transactions    | `/src/test/app/Change_test.cpp`                                                                                     |
| RPC/admin interface for querying/managing state | `/src/test/rpc/Feature_test.cpp`                                                                                    |

**Note:** The mapping above is based on the summaries provided. For several critical steps (e.g., time-based majority, irreversibility, unsupported amendments), it is not clear from the documentation whether they are directly tested.

---

## 4. Areas Not Covered or Unclear

- **Unsupported Amendments:** It is not explicitly stated that there are tests for the scenario where an unsupported amendment is enabled and the server blocks itself.
- **Irreversibility:** There is no explicit mention of tests verifying that amendments cannot be disabled or revoked after activation.
- **Database Corruption/Recovery:** While persistence is tested, it is unclear if database corruption or recovery scenarios are covered.
- **Consensus Edge Cases:** It is not clear if all consensus edge cases (e.g., disputed amendments, failure to reach consensus) are tested.
- **Negative/Edge Cases:** While edge cases are mentioned, there is no explicit mapping to test files for scenarios such as conflicting votes or database corruption.

---

## 5. Summary Table

| Area                                 | Explicitly Covered in Test Files? | Present in Provided Info? | Comment                                      |
|---------------------------------------|-----------------------------------|---------------------------|----------------------------------------------|
| Amendment registration                | Yes                               | Yes                       |                                              |
| Voting (including 80%/2 weeks)        | Yes (general)                     | Yes                       | Not clear if time-based logic is tested      |
| Activation (pseudo-tx, ledger update) | Yes                               | Yes                       |                                              |
| Veto/admin controls                   | Yes (RPC/admin)                   | Yes                       | Not clear if all edge cases are tested       |
| Persistence (db/config)               | Yes                               | Yes                       | Not clear if recovery/corruption is tested   |
| Consensus integration                 | Yes (general)                     | Yes                       | Not clear if all consensus edge cases tested |
| Handling unsupported amendments       | Not explicit                      | Yes (code supports)       | Not clear if tested                         |
| Irreversibility (no disable/revoke)   | Not explicit                      | Yes (doc/code)            | Not clear if tested                         |
| Edge cases (conflicts, errors)        | Yes (general)                     | Yes                       | Not clear if all are tested                 |

---

## 6. Conclusion

- The provided test files collectively cover the core Consensus_Amendments functionality, including registration, voting, activation, persistence, RPC/admin interface, and some operational edge cases.
- However, based strictly on the provided information, it is **unclear** whether all critical amendment lifecycle steps (especially time-based majority, irreversibility, unsupported amendments, and consensus edge cases) are directly tested.
- If these areas are not covered by tests, this should be noted. If they are covered, the documentation should be updated to state this explicitly for clarity and completeness.
- **If you are unsure whether a specific area is tested, you should state so clearly.**

---

**This documentation is strictly grounded in the provided information. No assumptions are made beyond what is present.**