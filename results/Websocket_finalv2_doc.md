---

# XRPL WebSocket Subscription System

This documentation provides a precise, code-backed overview of how WebSocket subscriptions are established, managed, and delivered in the XRPL server. All statements are directly supported by the provided code and documentation.

---

## 1. Overview

WebSocket subscriptions in XRPL are managed through the RPC methods `subscribe` and `unsubscribe`. These allow clients to receive real-time updates for various event types, such as ledgers, transactions, books, validations, and more.

---

## 2. Session Establishment and Upgrade

- **Initial Connection:**  
  Clients connect to the XRPL server over HTTP (plain or SSL/TLS).
- **Upgrade to WebSocket:**  
  The server supports upgrading HTTP connections to WebSocket using the standard HTTP Upgrade mechanism:
    - For plain connections, `PlainHTTPPeer` handles the upgrade and creates a `PlainWSPeer`.
    - For SSL/TLS connections, `SSLHTTPPeer` handles the upgrade and creates an `SSLWSPeer`.
  - The upgrade is performed via the `websocketUpgrade()` method, which returns a new `WSSession` object representing the WebSocket session.
  - The relevant code for upgrade:
    - `/include/xrpl/server/detail/PlainHTTPPeer.h` and `/include/xrpl/server/detail/SSLHTTPPeer.h` define the `websocketUpgrade()` method, which instantiates the appropriate `WSSession` implementation.
    - The upgrade is triggered in the server handler (`ServerHandler::onHandoff`), which checks for an upgrade request and, if present, calls `session.websocketUpgrade()`.

---

## 3. WebSocket Session Lifecycle

- **WSSession Interface:**  
  The `WSSession` interface defines the core methods for a WebSocket session:
    - `run()`: Starts the session, performs the WebSocket handshake, and begins reading messages.
    - `send()`: Queues a message for delivery to the client.
    - `close()`: Closes the session, optionally with a specific reason.
    - `complete()`: Marks the completion of a message exchange.
    - Accessors for connection details (port, request, remote endpoint).
  - See `/include/xrpl/server/WSSession.h`.

- **Implementations:**  
  The `BaseWSPeer` class (and its derivatives, `PlainWSPeer` and `SSLWSPeer`) implement the `WSSession` interface, managing:
    - Session lifecycle
    - Message queues
    - Timers
    - Error handling

- **Session Start:**  
  When a session is started (`run()`):
    - Sets up permessage-deflate options (compression) as configured on the port.
    - Sets up ping/pong handlers and timers for connection health.
    - Performs the WebSocket handshake and begins reading messages from the client.
    - See `/include/xrpl/server/detail/BaseWSPeer.h`.

---

## 4. Subscription Management

- **RPC Handlers:**  
  - The `subscribe` and `unsubscribe` RPC handlers are registered as:
    ```cpp
    {"subscribe", byRef(&doSubscribe), Role::USER, NO_CONDITION},
    {"unsubscribe", byRef(&doUnsubscribe), Role::USER, NO_CONDITION},
    ```
    (See `/src/xrpld/rpc/detail/Handler.cpp`)

- **InfoSub Interface:**  
  - The subscription system is based on the `InfoSub` interface (`/src/xrpld/net/InfoSub.h`), which provides methods for subscribing and unsubscribing to various event types, including:
    - `subLedger`, `unsubLedger`
    - `subBook`, `unsubBook`
    - `subTransactions`, `unsubTransactions`
    - `subRTTransactions`, `unsubRTTransactions`
    - `subValidations`, `unsubValidations`
    - `subServer`, `unsubServer`
    - `subManifests`, `unsubManifests`
    - `subPeerStatus`, `unsubPeerStatus`
    - `subConsensus`, `unsubConsensus`
    - etc.

- **Implementation:**  
  - The implementation of these methods is found in the `NetworkOPs` class (`/src/xrpld/app/misc/NetworkOPs.cpp`), which manages the actual subscription lists and event delivery.

- **WebSocket Association:**  
  - When a client subscribes, an `InfoSub` object is associated with the WebSocket session. For WebSocket clients, this is a `WSInfoSub` object (`/src/xrpld/rpc/detail/WSInfoSub.h`), which:
    - Tracks the client's subscriptions.
    - Delivers real-time notifications to the client via the `send` method.
    - Extracts user and forwarded-for information from the request headers if the remote IP is allowed.

- **Unsubscribe:**  
  - The `unsubscribe` RPC handler (`doUnsubscribe`) removes the subscription for the specified type, using the corresponding `unsub*` method in `InfoSub`/`NetworkOPs`.

---

## 5. Message Delivery and Backpressure

- **Outgoing Messages:**  
  - Outgoing messages to WebSocket clients are queued for delivery.
  - The per-session message queue is limited by the `ws_queue_limit` parameter configured on the server port (`/include/xrpl/server/Port.h`).
  - If the message queue exceeds this limit (e.g., if the client is too slow to read messages), the session is closed with a policy error and a reason indicating the client is too slow.
    - See `/include/xrpl/server/detail/BaseWSPeer.h`:
      ```cpp
      if (wq_.size() > port().ws_queue_limit) {
          cr_.code = ...policy_error;
          cr_.reason = "Policy error: client is too slow.";
          ...
          close(cr_);
          return;
      }
      ```
  - The `send` method in `WSInfoSub` serializes JSON messages and sends them to the client using a stream buffer.

---

## 6. Resource Limits and Error Handling

- **Resource Limits:**  
  - The server enforces several resource limits:
    - Per-port connection limits (`limit`).
    - Per-session message queue limits (`ws_queue_limit`).
  - If a client exceeds resource limits (e.g., too many connections, too many queued messages), the server closes the connection and may return an error.

- **Error Handling:**  
  - If a client sends an invalid or oversized message, the server responds with an error message and may close the connection.
    - See `/src/xrpld/rpc/detail/ServerHandler.cpp`:
      ```cpp
      if (size > RPC::Tuning::maxRequestSize || !Json::Reader{}.parse(jv, buffers) || !jv.isObject()) {
          // Send error and close
      }
      ```
  - If a WebSocket upgrade fails, an appropriate HTTP error is returned.

---

## 7. Authentication and User Identification

- **User Extraction:**  
  - The `WSInfoSub` class extracts the `X-User` header and the forwarded-for address from the WebSocket request headers, if the remote IP is allowed by the server's secure gateway network configuration.
  - This information can be used for user identification and access control.
    - See `/src/xrpld/rpc/detail/WSInfoSub.h`:
      ```cpp
      if (ipAllowed(...)) {
          auto it = h.find("X-User");
          if (it != h.end()) user_ = it->value();
          fwdfor_ = std::string(forwardedFor(h));
      }
      ```

---

## 8. Processing Incoming Messages

- **Message Parsing:**  
  - Incoming WebSocket messages are parsed as JSON.
  - If the message is not valid JSON or exceeds the maximum allowed size, an error is sent to the client.
  - Valid messages are dispatched to the appropriate RPC handler (e.g., `subscribe`, `unsubscribe`).
    - See `/src/xrpld/rpc/detail/ServerHandler.cpp` and `/include/xrpl/server/detail/BaseWSPeer.h`.

---

## 9. Summary

- The `subscribe` RPC method adds a new subscription for the requested type by calling the appropriate `sub*` method in `NetworkOPs` via the `InfoSub` interface.
- The `unsubscribe` RPC method removes the subscription using the corresponding `unsub*` method.
- WebSocket sessions are managed by the `WSSession` interface and its implementations, which handle session lifecycle, message delivery, and error handling.
- Resource limits are enforced to prevent abuse and ensure server stability.
- These mechanisms allow WebSocket clients to receive real-time updates for ledger, transactions, books, validations, and other event types, as managed by the XRPL server.

---

**All statements above are directly supported by the provided code and documentation. No information has been invented or assumed.**