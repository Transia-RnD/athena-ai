- WebSocket subscriptions in XRPL are managed through the RPC methods `subscribe` and `unsubscribe`.
- The `subscribe` RPC handler is registered as follows (from `src/xrpld/rpc/detail/Handler.cpp`):

  {"subscribe", byRef(&doSubscribe), Role::USER, NO_CONDITION},
  {"unsubscribe", byRef(&doUnsubscribe), Role::USER, NO_CONDITION},

- When a client sends a `subscribe` request over WebSocket, the `doSubscribe` function is invoked. This function adds a new subscription for the requested subscription type (such as streams, books, transactions, etc.).
- The subscription system is based on the `InfoSub` interface (`src/xrpld/net/InfoSub.h`), which provides methods for subscribing and unsubscribing to various event types:

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

- The implementation of these methods is found in the `NetworkOPs` class (`src/xrpld/app/misc/NetworkOPs.cpp`), which manages the actual subscription lists and event delivery.
- When a client subscribes, an `InfoSub` object is associated with the WebSocket session (see `WSInfoSub` in the lesson plan). This object is used to track the client's subscriptions and deliver real-time notifications.
- The `unsubscribe` RPC handler (`doUnsubscribe`) removes the subscription for the specified type, using the corresponding `unsub*` method in `InfoSub`/`NetworkOPs`.

**Summary:**  
- The `subscribe` RPC method adds a new subscription for the requested type by calling the appropriate `sub*` method in `NetworkOPs` via the `InfoSub` interface.
- The `unsubscribe` RPC method removes the subscription using the corresponding `unsub*` method.
- These mechanisms allow WebSocket clients to receive real-time updates for ledger, transactions, books, validations, and other event types, as managed by the XRPL server.

All statements above are directly supported by the provided code and documentation.