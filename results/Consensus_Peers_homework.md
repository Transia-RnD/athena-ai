# Homework Assignment: Consensus_Peers Deep Dive

## Section 1: Code Writing Tasks

### 1.1 Proposal Handling

**Task:**  
Implement a function `void handlePeerProposal(NodeID_t peerId, Proposal_t const& proposal)` that updates the internal state when a new proposal is received from a peer. Your implementation must:

- Correctly update the peer's position in the `currPeerPositions_` map.
- Handle the case where a peer sends a duplicate proposal (same position as before).
- Handle the case where a peer changes its proposal mid-round.
- Reference: See the loop over `currPeerPositions_` in the consensus logic.

**Edge Cases to Cover:**
- Peer sends multiple proposals with the same position.
- Peer changes its proposal after consensus is reached.
- Peer sends a proposal for an unknown ledger.

---

### 1.2 Peer State Tracking

**Task:**  
Write a function `std::vector<NodeID_t> getPeersInState(ConsensusState state)` that returns all peer IDs currently in a given consensus state (`No`, `MovedOn`, `Expired`, `Yes`).  
- Reference: Use the `currPeerPositions_` and the `ConsensusState` enum.

**Edge Cases to Cover:**
- No peers in the requested state.
- All peers in the same state.
- Peers transitioning between states during the call.

---

### 1.3 Dispute Management

**Task:**  
Implement a method `void resolveDisputes()` that iterates over all disputes in `result_->disputes` and calls a hypothetical `resolve()` method on each, passing in the current consensus parameters and peer states.  
- Reference: See the use of `result_->disputes` and the `stalled` calculation.

**Edge Cases to Cover:**
- Dispute set is empty.
- All disputes are already resolved.
- Disputes with conflicting peer votes.

---

### 1.4 Consensus State Transitions

**Task:**  
Write a function `ConsensusState checkConsensusState()` that determines the current consensus state based on the number of agreeing/disagreeing peers, finished proposers, and round time.  
- Reference: See the call to `checkConsensus()` and the use of `ConsensusState`.

**Edge Cases to Cover:**
- No proposers finished.
- All peers agree but round time is not sufficient.
- Disagreement persists past the expected round time.

---

### 1.5 Peer Communication

**Task:**  
Implement a function `void broadcastProposal(Proposal_t const& proposal)` that sends the given proposal to all connected peers, ensuring that proposals are not sent to peers who have already agreed with the current position.  
- Reference: Use the `currPeerPositions_` and proposal comparison logic.

**Edge Cases to Cover:**
- No connected peers.
- All peers already agree.
- Network failure during broadcast.

---

### 1.6 Supporting Data Structures/Utilities

**Task:**  
Write a utility function `void resetConsensusTimer(ConsensusTimer& timer)` that resets the consensus timer to the current time point.  
- Reference: See `ConsensusTimer::reset()`.

**Edge Cases to Cover:**
- Timer is already at zero.
- Timer is reset multiple times in quick succession.

---

## Section 2: Debugging and Testing Exercises

### 2.1 Subtle Bug: Proposal Disagreement Counting

**Task:**  
Given the following code snippet (from the proposal agreement loop):

```cpp
for (auto const& [nodeId, peerPos] : currPeerPositions_) {
    Proposal_t const& peerProp = peerPos.proposal();
    if (peerProp.position() == ourPosition) {
        ++agree;
    } else {
        JLOG(j_.debug()) << "Proposal disagreement: Peer " << nodeId << " has " << peerProp.position();
        ++disagree;
    }
}
```

**Exercise:**  
- Identify a subtle bug that could occur if a peer sends multiple proposals in a single round.
- Propose and implement a fix.
- Write a test case that would have failed before your fix.

---

### 2.2 Logic Error: Stalled Dispute Detection

**Task:**  
Examine the following code for detecting stalled disputes:

```cpp
bool const stalled = haveCloseTimeConsensus_ && std::ranges::all_of(result_->disputes, [this, &parms](auto const& dispute) {
    return dispute.second.stalled(parms, mode_.get() == ConsensusMode::proposing, peerUnchangedCounter_);
});
```

**Exercise:**  
- Explain a scenario where this logic could incorrectly report that consensus is stalled.
- Modify the code to handle this scenario correctly.
- Write a test to verify your fix.

---

### 2.3 Timer Utility: Incorrect Duration Calculation

**Task:**  
Given the `ConsensusTimer` class, suppose a bug is reported where the timer sometimes returns negative durations.

**Exercise:**  
- Identify how this could happen based on the `tick(time_point tp)` method.
- Propose a fix.
- Write a unit test that demonstrates the bug and verifies the fix.

---

## Section 3: Conceptual Questions

### 3.1 Architecture and Flow

**Question:**  
Describe the overall flow of the consensus process as implemented in this module. In your answer, explain:

- How proposals are collected and tracked.
- How peer states are updated and used.
- How disputes are managed and resolved.
- How consensus state transitions are determined.
- How peer communication is handled.

Reference specific data structures and methods from the code.

---

### 3.2 Proposal Handling

**Question:**  
Explain how the system ensures that only the latest proposal from each peer is considered during consensus. What could go wrong if this was not enforced?

---

### 3.3 Dispute Management

**Question:**  
Discuss the role of the `disputes` data structure in the consensus process. How does it interact with peer proposals and what is its impact on the final consensus decision?

---

### 3.4 Consensus State Transitions

**Question:**  
What are the possible values of `ConsensusState` and what does each represent? Describe a scenario for each state.

---

### 3.5 Peer Communication

**Question:**  
How does the system ensure reliable communication of proposals and consensus state among peers? What mechanisms are in place to handle network failures or unresponsive peers?

---

### 3.6 Supporting Utilities

**Question:**  
Describe the purpose of the `ConsensusTimer` utility. How does it contribute to the robustness of the consensus process?

---

## Submission Instructions

- For code writing tasks, submit your code files with clear function implementations and comments.
- For debugging/testing, submit both your code changes and test cases, along with a brief explanation.
- For conceptual questions, submit written answers (1-2 paragraphs each).
- Reference relevant code locations in your answers.

---

**End of Assignment**