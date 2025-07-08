# XRPL Test Environment, Helpers, Suite Setup, and Test Life Cycle

## Organization of jtx Helpers and Transaction Groups

When a new transaction type is introduced in the XRPL codebase, a corresponding helper is always added to the `jtx` helpers directory (`src/test/jtx/`). This is done to ensure that tests for the new transaction are concise, expressive, and maintainable.

- **jtx Helper Files:**  
  For each transaction group, a new pair of files (`<Transaction>_h.cpp` and `<Transaction>_h.h`) is created in `src/test/jtx/`. For example, if a new transaction type called "DID" is added, the files `DID.cpp` and `DID.h` are created in the `jtx` directory.
- **Purpose:**  
  These helpers encapsulate the logic for constructing, submitting, and asserting the results of the new transaction type within tests. This organization allows all helper functions related to a specific transaction group to be grouped together, making the codebase easier to navigate and maintain.
- **Usage in Tests:**  
  Test files for the new transaction will include the relevant jtx helper header and use its functions to create and manipulate transactions in the test environment.

**Example Directory Structure:**
```
src/test/jtx/
  ├── Account.cpp
  ├── Account.h
  ├── fund.cpp
  ├── fund.h
  ├── pay.cpp
  ├── pay.h
  ├── trust.cpp
  ├── trust.h
  ├── DID.cpp         # New helper for DID transaction group
  ├── DID.h
  └── ...
```

**Example Usage in a Test:**
```cpp
#include <test/jtx/DID.h>

void testDIDTransaction()
{
    Env env{*this, features};
    Account alice{"alice"};
    env.fund(XRP(1000), alice);

    // Use the DID jtx helper to create a DID transaction
    env(DID(alice, /* parameters */));
    env.close();

    // Assertions using jtx helpers
    env.require(/* ... */);
}
```

**Summary:**  
- Every new transaction group gets its own jtx helper files.
- This approach organizes helper functions by transaction type, making it easy to find and update helpers as the protocol evolves.
- Tests for new transactions always leverage these helpers for clarity and maintainability.