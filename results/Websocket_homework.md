# XRPL WebSocket Subsystem: Comprehensive Homework Assignment

**Objective:**  
Demonstrate a deep understanding of the XRPL WebSocket subsystem by analyzing, extending, and testing its codebase. You will cover connection acceptance, protocol detection, session management, message processing, upgrades, message sending, queueing, closing, integration with RPC and subscription systems, thread safety, and asynchrony.

---

## Part 1: Code Analysis (Short Answer & Code Reading)

**1.1. Connection Acceptance & Protocol Detection**  
a) Explain how the XRPL server distinguishes between a standard HTTP request and a WebSocket upgrade request.  
b) In the provided code, identify where protocol-specific parameters are validated during the upgrade process.  
c) What HTTP response is sent if the upgrade request is malformed or the protocol is unsupported? Provide the relevant code snippet.

**1.2. Session Management**  
a) Describe how a WebSocket session is represented in the codebase.  
b) What resources are associated with a session, and how are they cleaned up on close?

**1.3. Message Processing**  
a) Outline the flow of an incoming WebSocket message from receipt to dispatch to the appropriate handler.  
b) How does the system handle malformed or unexpected messages?

---

## Part 2: Code Writing (Implementation & Edge Cases)

**2.1. Implementing Edge Cases**  
a) **Connection Flooding:**  
   - Modify the WebSocket session code to detect and reject connections if the number of active sessions exceeds a configurable limit.  
   - Return an HTTP 503 response with a JSON body listing alternative peer IPs (see context for example).

b) **Protocol Version Negotiation:**  
   - Extend the protocol detection logic to reject upgrade requests that specify an unsupported protocol version (e.g., "XRPL/3.0").  
   - Ensure the server responds with HTTP 400 and a clear error message.

c) **Message Queue Overflow:**  
   - Implement logic to detect when a session's outgoing message queue exceeds a safe threshold.  
   - When this occurs, close the session gracefully and log the event.

**2.2. Asynchronous Message Sending**  
- Refactor the message sending logic to ensure that messages are sent asynchronously and in order, even if the underlying socket is temporarily blocked.  
- Ensure that no two threads can send on the same socket simultaneously (demonstrate thread safety).

---

## Part 3: Integration & Subscription

**3.1. RPC Integration**  
- Add a new gRPC method (e.g., `GetWebSocketSessionInfo`) that returns information about all active WebSocket sessions.  
- Implement the handler, request/response types, and integrate with the WebSocket session management code.

**3.2. Subscription System**  
- Modify the WebSocket session code to allow clients to subscribe/unsubscribe to ledger updates.  
- Ensure that only subscribed sessions receive relevant notifications, and that unsubscribing works as expected.

---

## Part 4: Testing & Debugging

**4.1. Test Design**  
a) Design unit tests for the following scenarios:  
   - Successful and failed WebSocket upgrades (including malformed requests and unsupported protocols).  
   - Message queue overflow and graceful session closure.  
   - Subscription and unsubscription to ledger updates.

b) Design integration tests for:  
   - Simultaneous connections from multiple clients, including exceeding the session limit.  
   - Asynchronous message delivery under high load.

**4.2. Debugging**  
- Given a log excerpt showing a session being closed unexpectedly, outline a step-by-step debugging approach to determine the root cause (e.g., queue overflow, protocol error, thread safety violation).

---

## Part 5: Reflection

**5.1. Thread Safety & Asynchrony**  
- In a short essay (200-300 words), discuss the challenges of ensuring thread safety and asynchrony in a high-performance WebSocket server.  
- Suggest best practices and potential pitfalls, referencing your code changes and test results.

---

# Submission Guidelines

- Submit your code changes as a patch or forked repository.
- Include all test code and a README describing how to run the tests.
- Provide written answers and explanations in a separate document.
- Ensure your code is well-commented and follows project style guidelines.

---

**Grading Rubric:**  
- Code Analysis: 20%  
- Code Writing (including edge cases): 30%  
- Integration & Subscription: 15%  
- Testing & Debugging: 20%  
- Reflection: 15%

---

**End of Assignment**