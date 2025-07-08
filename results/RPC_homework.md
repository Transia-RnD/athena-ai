---

# XRPL RPC Subsystem: Comprehensive Homework Assignment

## Overview

This assignment is designed to test your understanding of the XRPL RPC subsystem, including handler registration, lookup and dispatch, role and permission management, precondition checks, error handling, handler lifecycle, concurrency, and best practices. You will demonstrate your knowledge through short answer questions, code writing, code review/debugging, and test writing. You are required to reference and use the relevant XRPL source files and documentation throughout.

---

## Part 1: Short Answer (20 points)

**Answer the following questions concisely. Reference specific XRPL source files and documentation where appropriate.**

1. **Handler Registration and Discovery**
   - a. Describe the structure and purpose of the handler table in the XRPL RPC subsystem. How are versioning and beta flags managed for handlers?  
   - b. Where and how are new handlers registered for JSON/WebSocket and gRPC endpoints?  
   - c. What is the purpose of the `getHandler` and `getHandlerNames` functions? Where are they used?

2. **Role and Permission Management**
   - a. Explain how roles (e.g., ADMIN, GUEST) are determined for incoming RPC requests.  
   - b. How does the system propagate permission errors, and what is the expected error response format for both JSON and gRPC?

3. **Handler Lifecycle and Concurrency**
   - a. Describe the lifecycle of an RPC handler from request receipt to response delivery.  
   - b. How does the system handle long-running or multi-part RPC commands? Reference the coroutine and suspension mechanism.

4. **Precondition Checks and Command Validation**
   - a. What are precondition checks in the context of an RPC handler?  
   - b. Where should command validation logic be placed, and how should errors be reported?

---

## Part 2: Code Writing (40 points)

**Implement a new RPC handler called `GetServerStatus` that returns basic server status information (e.g., server state, load, and uptime). You must implement both JSON/WebSocket and gRPC versions.**

### Requirements:

- **Handler Registration:**  
  - Register the handler in the appropriate handler table(s) with versioning and beta flags as needed.
- **Request/Response Types:**  
  - For gRPC, define the request and response types in a new `.proto` file as per the conventions (see `xrp_ledger.proto`).
- **Handler Implementation:**  
  - Implement the handler logic in the appropriate file under `src/ripple/rpc/handlers/`.
  - Include precondition checks (e.g., role/permission checks).
  - Format responses according to JSON and gRPC conventions.
  - Handle and propagate errors appropriately.
- **gRPC Server Integration:**  
  - Add the handler to `GRPCServerImpl::setupListeners()` using the `CallData` template.
- **Code Organization:**  
  - Abstract common logic into helper functions if possible.
  - Follow best practices for code organization and documentation.

---

## Part 3: Test Writing (20 points)

**Write comprehensive unit tests for your new handler.**

- Implement tests for both JSON and gRPC endpoints.
- Cover normal operation, edge cases (e.g., server under heavy load, invalid request), and permission errors (e.g., insufficient role).
- For gRPC, implement a test client class derived from `GRPCTestClientBase` (see `GrpcTxClient` in `Tx_test.cpp`).
- Ensure your tests mirror the structure and thoroughness of existing handler tests.

---

## Part 4: Code Review and Debugging (20 points)

**You are given the following buggy handler implementation (see below). Analyze and fix all issues related to handler registration, permission checks, error handling, and response formatting.**

```cpp
// BuggyHandler.cpp
#include <xrpld/rpc/handlers/BuggyHandler.h>

Json::Value
doBuggyHandler(RPC::JsonContext& context)
{
    if (context.role != Role::ADMIN)
        return RPC::make_error(rpcNO_PERMISSION);

    // Missing precondition checks
    // Incorrect response formatting
    Json::Value result;
    result["status"] = "ok";
    result["server_state"] = context.app.getOPs().getServerState();
    return result;
}
```

**Tasks:**
- Identify and explain all issues in the above code.
- Provide a corrected version that follows best practices for handler registration, permission checks, precondition validation, and response formatting.

---

## Part 5: Best Practices and Code Organization (Short Answer, 10 points)

**Answer the following:**

- a. What are the best practices for organizing handler code and tests in the XRPL codebase?
- b. How should common logic be shared between JSON/WebSocket and gRPC handlers?
- c. Why is it important to mirror JSON and gRPC tests, and how does this benefit maintainability?

---

## Rubric

| Section                        | Points | Criteria                                                                                   |
|--------------------------------|--------|--------------------------------------------------------------------------------------------|
| Part 1: Short Answer           | 20     | Accuracy, completeness, references to source files and docs                                |
| Part 2: Code Writing           | 40     | Correctness, completeness, adherence to conventions, error handling, code organization     |
| Part 3: Test Writing           | 20     | Coverage (normal, edge, error cases), structure, use of test utilities, clarity            |
| Part 4: Code Review/Debugging  | 20     | Identification of issues, quality of fixes, explanations, adherence to best practices      |
| Part 5: Best Practices         | 10     | Clarity, completeness, understanding of maintainability and code organization              |
| **Total**                      | 110    |                                                                                            |

---

## Submission Instructions

- Submit your code, tests, and written answers as a single archive.
- Clearly indicate file names and locations for all code and tests.
- Reference relevant XRPL source files and documentation in your answers.
- Ensure your code compiles and all tests pass.

---

**End of Assignment**