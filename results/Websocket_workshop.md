# XRPL WebSocket Functionality Workshop Assignment

## Assignment Overview

This comprehensive workshop assignment will guide you through understanding and implementing WebSocket functionality in the XRPL (XRP Ledger) codebase. You will analyze the existing architecture, create a new WebSocket command, and demonstrate mastery of all WebSocket-related components.

## Learning Objectives

By completing this assignment, you will:
- Understand the complete WebSocket architecture in XRPL
- Master session management and message processing
- Implement subscription systems and RPC integration
- Handle connection lifecycle, flow control, and thread safety
- Create a new WebSocket command with real-time notifications

## Part 1: Architecture Analysis (25 points)

### 1.1 WebSocket Component Mapping (10 points)

Create a detailed architectural diagram showing the relationships between:

```cpp
// Key components to analyze:
- BaseWSPeer (xrpl/server/BaseWSPeer.h)
- WSSession (xrpl/server/WSSession.h) 
- WSInfoSub (xrpld/rpc/WSInfoSub.h)
- ServerHandler
- Port configuration
- Writer interface
```

**Deliverable**: A comprehensive diagram with explanations of:
- Data flow between components
- Inheritance hierarchies
- Template specializations
- Boost.Beast integration points

### 1.2 Session Lifecycle Documentation (15 points)

Document the complete lifecycle of a WebSocket session by tracing through the code:

```cpp
// Trace these key phases:
1. TCP connection acceptance
2. HTTP request processing
3. WebSocket upgrade negotiation
4. Session establishment
5. Message processing loop
6. Subscription management
7. Clean shutdown/error handling
```

**Required Analysis**:
- Identify all state transitions
- Document error handling paths
- Explain resource cleanup mechanisms
- Detail thread safety measures

## Part 2: Message Processing Deep Dive (30 points)

### 2.1 Request/Response Flow (15 points)

Analyze the message processing pipeline:

```cpp
// Key areas to examine:
class BaseWSPeer {
    // Message reception and parsing
    void on_read_msg(boost::system::error_code const& ec, std::size_t bytes_transferred);
    
    // Message dispatch
    void handle_message(std::shared_ptr<Message> const& message);
    
    // Response generation
    void send(std::shared_ptr<Message> const& message);
};
```

**Tasks**:
1. Document the complete message flow from reception to response
2. Explain JSON parsing and validation
3. Analyze error handling and response formatting
4. Detail the role of the Writer interface

### 2.2 Subscription System Analysis (15 points)

Examine the WSInfoSub implementation:

```cpp
class WSInfoSub : public InfoSub {
    // Subscription management
    void send(Json::Value const& jvObj, bool broadcast);
    
    // Connection state tracking
    std::weak_ptr<WSSession> ws_;
    
    // Role-based access control
    Role role_;
};
```

**Deliverables**:
- Explain the InfoSub base class functionality
- Document subscription lifecycle management
- Analyze role-based filtering
- Detail memory management with weak_ptr usage

## Part 3: Implementation - Account Change Monitor (35 points)

### 3.1 Command Implementation (20 points)

Create a new WebSocket command called `account_monitor` that provides real-time notifications when specified accounts change.

**File Structure**:
```
src/ripple/rpc/handlers/AccountMonitor.cpp
src/ripple/rpc/impl/AccountMonitor.h
```

**Implementation Requirements**:

```cpp
// AccountMonitor.cpp
#include <xrpld/rpc/handlers/AccountMonitor.h>
#include <xrpld/rpc/WSInfoSub.h>
#include <xrpl/app/ledger/LedgerMaster.h>
#include <xrpl/protocol/jss.h>

namespace ripple {

// Command handler
Json::Value doAccountMonitor(RPC::JsonContext& context) {
    // Parse request parameters
    if (!context.params.isMember(jss::account)) {
        return RPC::missing_field_error(jss::account);
    }
    
    // Validate account format
    AccountID accountID;
    if (!parseBase58<AccountID>(
        context.params[jss::account].asString(), accountID)) {
        return RPC::invalid_field_error(jss::account);
    }
    
    // Set up subscription
    if (auto infoSub = context.infoSub.lock()) {
        // Register for account notifications
        context.app.getOPs().subAccount(
            infoSub, accountID, true);
            
        Json::Value result;
        result[jss::status] = "success";
        result[jss::account] = context.params[jss::account];
        result[jss::type] = "response";
        return result;
    }
    
    return RPC::internal_error();
}

} // ripple
```

### 3.2 Integration with Subscription System (15 points)

Extend the existing subscription infrastructure:

```cpp
// Modify NetworkOPs or equivalent to support account monitoring
class NetworkOPs {
public:
    void subAccount(
        std::shared_ptr<InfoSub> const& subscriber,
        AccountID const& account,
        bool realTime);
        
    void unsubAccount(
        std::shared_ptr<InfoSub> const& subscriber,
        AccountID const& account);
        
private:
    // Account subscription tracking
    hash_map<AccountID, std::set<std::weak_ptr<InfoSub>>> accountSubs_;
    std::mutex accountSubsMutex_;
    
    // Notification dispatch
    void notifyAccountChange(
        AccountID const& account,
        std::shared_ptr<ReadView const> const& ledger);
};
```

**Implementation Details**:
- Thread-safe subscription management
- Efficient account change detection
- Proper cleanup of expired subscriptions
- Integration with ledger close events

## Part 4: Advanced Features (10 points)

### 4.1 Flow Control and Backpressure

Implement proper flow control for your account monitor:

```cpp
class AccountMonitorSub : public WSInfoSub {
private:
    std::queue<Json::Value> pendingNotifications_;
    std::atomic<size_t> queueSize_{0};
    static constexpr size_t MAX_QUEUE_SIZE = 1000;
    
public:
    bool shouldQueue() const override {
        return queueSize_ < MAX_QUEUE_SIZE;
    }
    
    void handleBackpressure() {
        // Implement rate limiting or selective dropping
    }
};
```

### 4.2 Error Handling and Recovery

Implement comprehensive error handling:

```cpp
// Error scenarios to handle:
- Network disconnections
- Invalid account formats
- Subscription limits exceeded
- Memory pressure
- Ledger unavailability
```

## Testing Requirements

### Unit Tests
Create comprehensive unit tests covering:

```cpp
// Test file: src/test/rpc/AccountMonitor_test.cpp
class AccountMonitor_test : public beast::unit_test::suite {
public:
    void testBasicSubscription();
    void testInvalidAccount();
    void testMultipleAccounts();
    void testUnsubscription();
    void testErrorHandling();
    void testFlowControl();
    void testThreadSafety();
};
```

### Integration Tests
Test the complete WebSocket flow:

```cpp
// Integration test scenarios:
1. WebSocket connection establishment
2. Account monitor command execution
3. Real-time notification delivery
4. Connection cleanup
5. Stress testing with multiple clients
```

## Submission Requirements

### Code Deliverables
1. Complete implementation of AccountMonitor command
2. Integration with existing WebSocket infrastructure
3. Comprehensive unit and integration tests
4. Documentation and code comments

### Written Analysis (5-10 pages)
1. **Architecture Overview**: Detailed explanation of XRPL WebSocket architecture
2. **Implementation Details**: Your design decisions and rationale
3. **Performance Considerations**: Analysis of scalability and efficiency
4. **Security Analysis**: Potential vulnerabilities and mitigations
5. **Future Enhancements**: Proposed improvements and extensions

### Demonstration
Prepare a live demonstration showing:
1. WebSocket connection establishment
2. Account monitor subscription
3. Real-time notifications
4. Error handling scenarios
5. Performance under load

## Evaluation Criteria

| Component | Weight | Criteria |
|-----------|--------|----------|
| Architecture Analysis | 25% | Completeness, accuracy, depth of understanding |
| Message Processing | 30% | Correct implementation, error handling |
| Account Monitor | 35% | Functionality, integration, code quality |
| Testing & Documentation | 10% | Test coverage, documentation quality |

## Advanced Challenges (Bonus Points)

### Challenge 1: Multi-Account Monitoring (5 points)
Extend your implementation to monitor multiple accounts efficiently with a single subscription.

### Challenge 2: Historical Data Integration (5 points)
Add support for retrieving historical account changes since a specific ledger.

### Challenge 3: Performance Optimization (5 points)
Implement advanced optimizations like:
- Subscription batching
- Differential updates
- Compression for large responses

## Resources and References

### Key Source Files to Study
```
xrpl/server/BaseWSPeer.h
xrpl/server/WSSession.h
xrpld/rpc/WSInfoSub.h
src/ripple/rpc/handlers/AccountInfo.cpp
src/ripple/rpc/handlers/Subscribe.cpp
src/ripple/app/misc/NetworkOPs.cpp
```

### Documentation References
- Boost.Beast WebSocket documentation
- XRPL WebSocket API specification
- JSON-RPC 2.0 specification
- C++ concurrency and thread safety best practices

## Submission Timeline

- **Week 1**: Architecture analysis and documentation
- **Week 2**: Basic AccountMonitor implementation
- **Week 3**: Integration and testing
- **Week 4**: Advanced features and final submission

This comprehensive assignment will provide deep understanding of WebSocket functionality in XRPL while creating practical, production-ready code that extends the system's capabilities.