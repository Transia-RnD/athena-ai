---

# XRPL Overlay Peering Functionality – Homework Assignment

## Overview

This assignment covers the architecture, implementation, and monitoring of the XRPL Overlay network and its peering logic. You will write code, debug and test, answer conceptual questions, and interpret monitoring output. Reference the following source files and documentation sections as needed:

- `xrpld/overlay/Overlay.h`
- `xrpld/overlay/Peer.h`
- `xrpld/overlay/PeerImp.h`
- `xrpld/overlay/PeerSet.h`
- [XRPL Overlay Network Documentation](https://xrpl.org/peer-protocol.html)

---

## 1. Code Writing Tasks

### 1.1. Implementing Edge Case Handling in Peer Connections

**Task:**  
Modify the peer connection logic in `xrpld/overlay/PeerImp.h` to handle the following edge case:

- If a peer attempts to establish a connection but is already connected (duplicate connection), ensure that only one connection is maintained and the duplicate is cleanly closed.  
- Write a function `handleDuplicateConnection()` that is called during the handshake phase.

**Requirements:**
- Reference the handshake logic in `xrpld/overlay/Overlay.h` and `xrpld/overlay/Peer.h`.
- Ensure proper logging using the logging utilities in `xrpl/basics/Log.h`.
- Write a unit test for this function.

---

### 1.2. Protocol Version Negotiation

**Task:**  
Extend the protocol version negotiation logic in `xrpld/overlay/detail/ProtocolVersion.h` to support a new protocol feature (e.g., `LedgerReplay`).  
- Add the new feature to the `ProtocolFeature` enum in `xrpld/overlay/Peer.h`.
- Update the negotiation logic to ensure both peers support the feature before enabling it.

**Requirements:**
- Document your changes with comments.
- Write a test case that simulates negotiation between two peers with mismatched feature support.

---

## 2. Debugging and Testing Exercises

### 2.1. Debugging Peer Message Handling

**Task:**  
Given the following code snippet from `xrpld/overlay/PeerImp.h`, identify and fix the bug that could cause a peer to process the same message multiple times:

```cpp
void
onMessageReceived(Message::pointer const& msg)
{
    // TODO: Prevent duplicate message processing
    processMessage(msg);
    // ... other logic
}
```

**Requirements:**
- Explain the bug and your fix.
- Implement a mechanism to track and ignore duplicate messages using a suitable data structure.

---

### 2.2. Testing Peer Squelching

**Task:**  
The squelching mechanism in `xrpld/overlay/Squelch.h` is intended to prevent message flooding.  
- Write a test that simulates a peer sending messages at a high rate.
- Verify that the squelch logic correctly limits the number of messages processed.

**Requirements:**
- Reference the squelch logic in `xrpld/overlay/Squelch.h`.
- Provide assertions to validate correct behavior.

---

## 3. Conceptual and Architectural Questions

### 3.1. Overlay Network Topology

**Question:**  
Describe the overlay network topology formed by XRPL peers.  
- How are connections established and maintained?
- What is the role of the `PeerSet` class (`xrpld/overlay/PeerSet.h`)?
- How does the overlay network ensure resilience and message propagation?

**Requirements:**
- Provide a detailed written explanation (200-300 words).
- Reference relevant classes and documentation.

---

### 3.2. Peer Protocol and Security

**Question:**  
Explain the handshake process and the security measures in place during peer connection establishment.  
- How are public keys and protocol versions exchanged?
- What mechanisms prevent unauthorized or malicious peers from joining the network?

**Requirements:**
- Reference the handshake logic in `xrpld/overlay/Peer.h` and `xrpld/overlay/PeerImp.h`.
- Discuss the use of public keys and protocol negotiation.

---

## 4. Monitoring Output and JSON Structure Interpretation

### 4.1. Interpreting Peer Monitoring Output

**Task:**  
Given the following JSON output from the peer monitoring endpoint, answer the questions below:

```json
{
  "peers": [
    {
      "public_key": "n9KHn...3Jp",
      "ip": "192.0.2.1",
      "protocol_version": "0020",
      "features": ["ValidatorListPropagation"],
      "squelched": false,
      "messages_sent": 1200,
      "messages_received": 1180
    },
    {
      "public_key": "n9LQh...7Xz",
      "ip": "198.51.100.2",
      "protocol_version": "0020",
      "features": ["LedgerReplay"],
      "squelched": true,
      "messages_sent": 5000,
      "messages_received": 200
    }
  ]
}
```

**Questions:**
- Which peer is currently squelched and why might this be the case?
- What does the `features` field indicate about each peer?
- How would you use this output to identify potential network issues?

---

### 4.2. Validating Peer JSON Structures

**Task:**  
Write a function in C++ that validates the structure of a peer JSON object as shown above.  
- The function should check for required fields and correct data types.
- Return an error message if validation fails.

**Requirements:**
- Use the JSON utilities in `xrpl/json/json_value.h`.
- Provide example input and output.

---

## Submission Instructions

- Submit your code files, test cases, and written answers in a single archive.
- Include a README describing how to build and run your tests.
- Cite all references to source files and documentation.

---

**End of Assignment**