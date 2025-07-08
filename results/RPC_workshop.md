# XRPL RPC System Workshop Assignment

## Overview

This comprehensive workshop assignment will test your understanding of the XRPL RPC system by having you implement a new RPC command from scratch. You'll need to demonstrate knowledge of handler registration, lifecycle management, error handling, testing, and best practices.

## Assignment: Implement `GetAccountBalance` RPC Command

You will create a new RPC command called `GetAccountBalance` that returns detailed balance information for an XRPL account, including XRP balance, trust lines, and reserve requirements.

---

## Part 1: RPC System Architecture Understanding (20 points)

### 1.1 System Overview Questions (10 points)

Answer the following questions in detail:

1. **Handler Discovery**: Explain how RPC handlers are registered and discovered in the XRPL system. What role does the `Handler` struct play?

2. **Request Lifecycle**: Describe the complete lifecycle of an RPC request from receipt to response, including all major stages.

3. **Role-Based Access**: Explain the different user roles (`GUEST`, `USER`, `ADMIN`, `FORBID`) and how they affect RPC command access.

### 1.2 Architecture Diagram (10 points)

Create a detailed diagram showing:
- RPC request flow through the system
- Key classes and their relationships
- Handler registration and lookup process
- Error handling pathways

---

## Part 2: Handler Implementation (40 points)

### 2.1 Handler Registration (10 points)

**Task**: Add your `GetAccountBalance` handler to the system.

1. **File Location**: Identify where to add the handler registration
2. **Handler Structure**: Define the complete `Handler` struct for your command
3. **Registration Code**: Write the code to register your handler

```cpp
// Your handler registration code here
// Include: name, handler function, role requirements, resource costs
```

**Requirements**:
- Command name: `"account_balance"`
- Required role: `USER` or higher
- Resource cost: `MEDIUM` (since it may query multiple objects)
- Condition: Available when server is synced

### 2.2 Request/Response Types (10 points)

**Task**: Define the JSON request and response structures.

**Request Parameters**:
```json
{
    "command": "account_balance",
    "account": "rAccount...",
    "ledger_index": "validated", // optional
    "include_reserves": true,    // optional, default false
    "include_trustlines": true   // optional, default false
}
```

**Response Structure**:
```json
{
    "account": "rAccount...",
    "ledger_index": 12345,
    "xrp_balance": "1000000000",
    "available_balance": "980000000",
    "reserves": {
        "base_reserve": "10000000",
        "owner_reserve": "2000000",
        "total_reserve": "20000000"
    },
    "trustlines": [...], // if requested
    "validated": true
}
```

### 2.3 Handler Implementation (20 points)

**Task**: Implement the complete handler function.

```cpp
Json::Value doGetAccountBalance(RPC::JsonContext& context)
{
    // Your implementation here
}
```

**Requirements**:
1. **Parameter Validation**: Validate all input parameters
2. **Account Validation**: Verify account format and existence
3. **Ledger Access**: Handle ledger selection (current, validated, specific)
4. **Balance Calculation**: Calculate XRP balance and available balance
5. **Reserve Calculation**: Calculate base and owner reserves
6. **Trust Line Handling**: Optionally include trust line balances
7. **Error Handling**: Proper error responses for all failure cases

**Key Implementation Points**:
- Use `RPC::accountFromString()` for account validation
- Use `context.ledgerMaster` for ledger access
- Handle both current and historical ledger queries
- Implement proper resource management
- Follow existing patterns from similar handlers

---

## Part 3: Error Handling and Validation (25 points)

### 3.1 Comprehensive Error Handling (15 points)

**Task**: Implement complete error handling for all possible failure scenarios.

**Required Error Cases**:
1. **Invalid Parameters**:
   - Missing account parameter
   - Invalid account format
   - Invalid ledger_index format

2. **System Errors**:
   - Ledger not available
   - Account not found
   - Network/database errors

3. **Permission Errors**:
   - Insufficient role permissions
   - Resource limit exceeded

**Implementation Requirements**:
```cpp
// Example error handling structure
if (/* validation fails */)
{
    return RPC::make_error(rpcINVALID_PARAMS, "Invalid account format");
}

if (/* account not found */)
{
    return RPC::make_error(rpcACT_NOT_FOUND, "Account not found");
}

// Add comprehensive error handling for all scenarios
```

### 3.2 Input Validation (10 points)

**Task**: Implement robust input validation.

**Validation Requirements**:
1. **Account Parameter**: Must be present and valid XRPL address
2. **Ledger Index**: Must be valid (number, "validated", "current", "closed")
3. **Boolean Flags**: Validate include_reserves and include_trustlines
4. **Parameter Types**: Ensure correct JSON types for all parameters

---

## Part 4: Testing Implementation (30 points)

### 4.1 Unit Tests (15 points)

**Task**: Write comprehensive unit tests for your handler.

**Required Test Cases**:
```cpp
// Test file: src/test/rpc/GetAccountBalance_test.cpp

class GetAccountBalance_test : public beast::unit_test::suite
{
public:
    void testValidRequest()
    {
        // Test normal operation with valid account
    }
    
    void testInvalidAccount()
    {
        // Test various invalid account formats
    }
    
    void testLedgerSelection()
    {
        // Test different ledger_index values
    }
    
    void testPermissions()
    {
        // Test role-based access control
    }
    
    void testErrorConditions()
    {
        // Test all error scenarios
    }
    
    void testOptionalParameters()
    {
        // Test include_reserves and include_trustlines flags
    }
    
    void run() override
    {
        testValidRequest();
        testInvalidAccount();
        testLedgerSelection();
        testPermissions();
        testErrorConditions();
        testOptionalParameters();
    }
};

BEAST_DEFINE_TESTSUITE(GetAccountBalance, rpc, ripple);
```

### 4.2 Integration Tests (15 points)

**Task**: Write integration tests that test the complete RPC pipeline.

**Test Scenarios**:
1. **End-to-End Testing**: Full RPC request through HTTP/WebSocket
2. **Performance Testing**: Response time under load
3. **Resource Management**: Verify resource consumption tracking
4. **Concurrent Access**: Multiple simultaneous requests

---

## Part 5: gRPC Implementation (25 points)

### 5.1 Protocol Buffer Definition (10 points)

**Task**: Add gRPC support for your command.

**File**: `src/ripple/proto/xrp_ledger.proto`

```protobuf
// Add to the service definition
rpc GetAccountBalance(GetAccountBalanceRequest) returns (GetAccountBalanceResponse);
```

**Message Definitions**:
```protobuf
message GetAccountBalanceRequest {
    string account = 1;
    string ledger_index = 2;
    bool include_reserves = 3;
    bool include_trustlines = 4;
}

message GetAccountBalanceResponse {
    string account = 1;
    uint32 ledger_index = 2;
    string xrp_balance = 3;
    string available_balance = 4;
    ReserveInfo reserves = 5;
    repeated TrustLine trustlines = 6;
    bool validated = 7;
}

message ReserveInfo {
    string base_reserve = 1;
    string owner_reserve = 2;
    string total_reserve = 3;
}
```

### 5.2 gRPC Handler Implementation (15 points)

**Task**: Implement the gRPC handler.

**Requirements**:
1. Add `CallData` instantiation in `GRPCServerImpl::setupListeners()`
2. Implement conversion between protobuf and JSON formats
3. Reuse logic from JSON handler
4. Handle gRPC-specific error responses

---

## Part 6: Documentation and Best Practices (20 points)

### 6.1 Code Documentation (10 points)

**Task**: Provide comprehensive documentation.

**Requirements**:
1. **Function Documentation**: Doxygen-style comments for all functions
2. **Parameter Documentation**: Document all parameters and return values
3. **Error Documentation**: Document all possible error conditions
4. **Usage Examples**: Provide example requests and responses

### 6.2 Best Practices Analysis (10 points)

**Task**: Write a detailed analysis of best practices demonstrated in your implementation.

**Topics to Cover**:
1. **Resource Management**: How you handle resource allocation and cleanup
2. **Error Handling Patterns**: Consistent error handling approach
3. **Code Reuse**: How you avoid duplication and promote maintainability
4. **Performance Considerations**: Optimizations and efficiency measures
5. **Security Considerations**: Input validation and access control

---

## Part 7: Advanced Features (Bonus - 20 points)

### 7.1 Coroutine Implementation (10 points)

**Task**: Implement your handler using RPC coroutines for better resource management.

**Requirements**:
- Use `Suspend` and `Continuation` for long-running operations
- Implement proper suspension points
- Handle coroutine lifecycle correctly

### 7.2 Streaming Support (10 points)

**Task**: Add streaming support for accounts with many trust lines.

**Requirements**:
- Implement pagination for large result sets
- Add streaming markers and continuation tokens
- Handle client disconnection gracefully

---

## Submission Requirements

### Code Submission
1. **Handler Implementation**: Complete source code files
2. **Test Files**: All unit and integration tests
3. **Protocol Buffers**: gRPC definitions and implementations
4. **Build Integration**: Updated CMakeLists.txt or build files

### Documentation Submission
1. **Implementation Report**: Detailed explanation of your approach
2. **Architecture Analysis**: How your handler fits into the overall system
3. **Testing Report**: Test coverage and results
4. **Performance Analysis**: Benchmarking results and optimizations

### Demonstration
1. **Live Demo**: Working demonstration of your RPC command
2. **Error Scenarios**: Show various error conditions and responses
3. **Performance Testing**: Demonstrate performance under load
4. **Code Walkthrough**: Explain key implementation decisions

---

## Evaluation Criteria

| Component | Weight | Criteria |
|-----------|--------|----------|
| Architecture Understanding | 20% | Depth of RPC system knowledge |
| Implementation Quality | 30% | Code quality, correctness, efficiency |
| Error Handling | 15% | Comprehensive error coverage |
| Testing | 20% | Test coverage and quality |
| Documentation | 10% | Clarity and completeness |
| Best Practices | 5% | Following established patterns |

### Grading Scale
- **A (90-100%)**: Exceptional implementation with advanced features
- **B (80-89%)**: Complete implementation meeting all requirements
- **C (70-79%)**: Basic implementation with minor issues
- **D (60-69%)**: Incomplete implementation with significant issues
- **F (<60%)**: Non-functional or severely incomplete

---

## Resources and References

### Key Files to Study
- `src/ripple/rpc/handlers/AccountInfo.cpp` - Similar account-based handler
- `src/ripple/rpc/handlers/AccountLines.cpp` - Trust line handling
- `src/ripple/rpc/impl/Handler.h` - Handler registration
- `src/ripple/rpc/impl/RPCHelpers.cpp` - Common RPC utilities

### Documentation
- XRPL RPC API Documentation
- gRPC Protocol Buffer Guide
- XRPL Ledger Format Documentation
- C++ Best Practices Guide

### Testing Framework
- Beast Unit Test Framework
- RPC Test Utilities
- Integration Test Examples

---

## Submission Deadline

**Due Date**: [Insert appropriate deadline]

**Submission Method**: 
- GitHub repository with complete implementation
- Documentation in markdown format
- Video demonstration (optional but recommended)

**Late Policy**: [Insert policy]

---

## Getting Help

- **Office Hours**: [Insert schedule]
- **Discussion Forum**: [Insert link]
- **Code Review Sessions**: [Insert schedule]
- **Technical Support**: [Insert contact information]

Good luck with your implementation! This assignment will give you deep hands-on experience with the XRPL RPC system and prepare you for contributing to the XRPL codebase.