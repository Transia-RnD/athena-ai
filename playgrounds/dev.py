#!/usr/bin/env python
# coding: utf-8

AGENT_MODEL = "claude-4-sonnet-20250514"
ATHENAH_CLIENT_NAME: str = "rippled-ai-core"


def main():
    # from athenah_ai.indexer import AthenahIndexer

    # path: str = "/Users/darkmatter/projects/ledger-works/rippled"
    # indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-core", "v1")
    # indexer.build_from_dirs(path, ["include", "src/libxrpl", "src/xrpld"], False, False)

    from athenah_ai.client import AthenahClient

    ai_source: AthenahClient = AthenahClient(
        "id",
        # provider="anthropic",
        provider="openai",
        # provider="xai",
        model_group="dist",
        custom_model=ATHENAH_CLIENT_NAME,
        version="v1",
        # model_name="claude-4-sonnet-20250514",
        model_name="gpt-4.1",
        # model_name="grok-4",
        temperature=0,
        best_of=3,
    )
    system_prompt: str = """
## Full Consensus Process Summary

**Consensus in the system begins in `Application.cpp`:**

```cpp
// start first consensus round
if (!m_networkOPs->beginConsensus(
        m_ledgerMaster->getClosedLedger()->info().hash, {}))
{
    JLOG(m_journal.fatal()) << "Unable to start consensus";
    return false;
}
```

- Here, the application starts the first consensus round by calling `beginConsensus` on the `NetworkOPs` object, passing the hash of the last closed ledger.
- If consensus cannot be started, a fatal log is written and the process returns false.

[NetworkOPsImp::beginConsensus](#325-networkopsimpbeginconsensus)

---

### 1. RCLConsensus::Adaptor::preStartRound: PreStart

**Summary:**  
This is the preparatory phase before a new consensus round begins. The system ensures all necessary preconditions are met, such as synchronizing with the network, checking the state of the previous ledger, and preparing internal data structures.

**Details:**  
- Ensures the node is ready to participate in consensus.
- May involve cleaning up state from the previous round.
- Prepares to receive and process proposals from peers.

---

### 2. Consensus<Adaptor>::startRound: Start New Consensus Round

**Summary:**  
Initiates a new round of consensus. This involves setting up the round's parameters, such as the ledger to be closed, the set of transactions to consider, and the initial state.

**Details:**  
- Marks the beginning of a new consensus round.
- Sets up timers and state machines for the round.
- Notifies other components that a new round has started.

---

### 3. Consensus<Adaptor>::startRoundInternal: ConsensusPhase::open

**Summary:**  
Enters the "open" phase of consensus, where the ledger is open for new transactions and proposals from peers are collected.

**Details:**  
- The ledger is open; transactions can be submitted.
- Nodes collect proposals from peers about which transactions to include.
- The system prepares to play back proposals for further processing.

---

#### 3.1 playbackProposals: Start Playing Back Peer Proposals

**Summary:**  
Processes proposals received from peers, replaying them to ensure all nodes are considering the same set of transactions.

**Details:**  
- Ensures all valid proposals are considered.
- May involve deduplication and validation of proposals.

---

#### 3.2 Consensus<Adaptor>::timerEntry

**Summary:**  
Handles periodic timer events during the consensus round, triggering checks and transitions between phases.

**Details:**  
- Regularly checks the state of the consensus process.
- Triggers actions such as checking the ledger or moving to the next phase.

---

##### 3.2.1 Consensus<Adaptor>::checkLedger: get previous ledger, handle wrong ledger

**Summary:**  
Verifies the previous ledger's state and handles any discrepancies (e.g., if the wrong ledger is detected).

**Details:**  
- Calls `adaptor_.getPrevLedger` to fetch the previous ledger.
- If the previous ledger is not as expected, calls `handleWrongLedger` to resolve the issue.
- Ensures the node is synchronized with the network.

---

##### 3.2.2 Consensus<Adaptor>::phaseOpen: Determines if we should close the ledger based on last ledger time

**Summary:**  
Decides whether to close the current ledger based on timing and network conditions.

**Details:**  
- Uses `shouldCloseLedger` to determine if enough time has passed or if other conditions are met to close the ledger.
- If so, transitions to the next phase.

---

###### 3.2.2.1 shouldCloseLedger: Should we close the consensus round?

**Summary:**  
Evaluates whether the consensus round should be closed, based on factors like elapsed time, transaction volume, and peer agreement.

**Details:**  
- If conditions are met, proceeds to close the ledger.

---

####### 3.2.2.1.1 Consensus<Adaptor>::closeLedger: Closes the ledger

**Summary:**  
Closes the current ledger, preventing further transactions from being added, and moves to the next phase of consensus.

**Details:**  
- Finalizes the set of transactions to be included.
- Notifies peers that the ledger is closed.

---

##### 3.2.3 Consensus<Adaptor>::phaseEstablish

**Summary:**  
The "establish" phase, where nodes work to reach agreement on the set of transactions to include in the closed ledger.

**Details:**  
- Nodes exchange positions and proposals.
- Disputed transactions are identified and resolved.

---

###### 3.2.3.1 Consensus<Adaptor>::updateOurPositions

**Summary:**  
Updates the node's position based on received proposals and local state.

**Details:**  
- Adjusts the set of transactions the node supports.
- May change votes on disputed transactions.

---

###### shouldPause: Should the node pause consensus?

**Summary:**  
Determines if the node should pause the consensus process, typically due to too many lagging peers or other network issues.

**Details:**  
- If too many peers are behind or not participating, the node may pause to allow the network to catch up.
- Prevents premature advancement in the consensus process.

---

###### Consensus<Adaptor>::haveConsensus: Has consensus been reached?

**Summary:**  
Checks whether sufficient agreement has been reached among participating nodes to finalize the consensus round.

**Details:**  
- Evaluates peer proposals and agreement thresholds.
- If consensus is not yet achieved, the process waits or continues gathering proposals.

**Elaboration on checkConsensus and checkConsensusReached:**

- During the "establish" phase, the system repeatedly checks if consensus has been reached by calling haveConsensus (or similar logic).
- This function calls checkConsensus, passing in the number of proposers, number of agreements, timing information, and other relevant parameters.
- checkConsensus performs several checks, such as:
    - Has the minimum consensus time elapsed?
    - Are there enough proposers?
    - Has the maximum allowed time elapsed?
    - Are enough nodes in agreement?
- As part of these checks, checkConsensus calls checkConsensusReached, which evaluates if the percentage of agreeing nodes meets the required threshold (e.g., 80%).
- If checkConsensusReached returns true, consensus is considered reached and the process advances to the next phase (accepting and building the ledger).
- If not, the process continues gathering proposals and re-evaluates on the next timer tick.

---

#### 3.2.3.2 RCLConsensus::Adaptor::onAccept

**Summary:**  
Handles the acceptance of the consensus result, building the new ledger and applying any remaining transactions.

**Details:**  
- Calls `buildLCL` to construct the Last Closed Ledger (LCL).
- Notifies `LedgerMaster` that consensus is built.
- Applies disputed transactions that were not included in the consensus set.

---

####### 3.2.3.2.1 RCLConsensus::Adaptor::buildLCL

**Summary:**  
Builds the Last Closed Ledger from the agreed-upon set of transactions.

**Details:**  
- Applies transactions in the agreed order.
- Ensures ledger consistency.

---

####### 3.2.3.2.2 LedgerMaster::consensusBuilt

**Summary:**  
Notifies the ledger management component that a new consensus ledger has been built.

**Details:**  
- Updates the system's view of the current ledger.
- May trigger further processing or notifications.

---

####### 3.2.3.2.3 Apply disputed transactions that didn't get in

**Summary:**  
Attempts to apply transactions that were disputed and not included in the consensus set, if possible.

**Details:**  
- Ensures no valid transaction is lost.
- May queue transactions for the next round.

---

###### 3.2.3.3 RCLConsensus::Adaptor::doAccept

**Summary:**  
Finalizes acceptance of the consensus result, building the ledger and processing the transaction queue.

**Details:**  
- Calls `buildLCL` again for redundancy or finalization.
- Calls `BuildLedger::buildLedger` to construct the ledger object.
- Processes the closed ledger's transaction queue via `app_.getTxQ().processClosedLedger`.

---

####### 3.2.3.3.1 BuildLedger::buildLedger

**Summary:**  
Constructs the ledger object from the agreed set of transactions.

**Details:**  
- Applies transactions to the ledger state.
- Ensures all state changes are recorded.

---

####### 3.2.3.3.2 app_.getTxQ().processClosedLedger

**Summary:**  
Processes the transaction queue for the closed ledger, handling any remaining or deferred transactions.

**Details:**  
- Ensures pending transactions are handled appropriately.
- Prepares for the next consensus round.

---

##### 3.2.4 NetworkOPsImp::endConsensus

**Summary:**  
Marks the end of the consensus process for the current round and transitions the system to the next state.  
After consensus is reached and the new ledger is built, `endConsensus` performs several important steps to ensure the node is synchronized and ready for the next round:

- **checkLastClosedLedger:**  
  This function determines if the node's last closed ledger (LCL) matches the preferred LCL as seen by the network. It compares the local LCL with those reported by peers and validations. If the local LCL is not the preferred one, it may trigger a ledger switch to synchronize with the network.

- **switchLastClosedLedger:**  
  If a switch is needed, this function updates the node's last closed ledger to the new preferred ledger. It logs the change, clears any flags indicating the need for a network ledger, and performs several key actions to update the node's state:
    - **clearNeedNetworkLedger:**  
      Clears any internal flags or state indicating that the node needs to acquire a new ledger from the network. This signals that the node is now in sync.
    - **app_.getTxQ().processClosedLedger:**  
      Processes the transaction queue in the context of the new closed ledger. This updates fee metrics, removes transactions that are now included in the ledger, and manages any transactions that need to be retried or deferred.
    - **app_.openLedger().accept:**  
      Accepts the new open ledger, applying any local transactions that were not included in the closed ledger. This ensures the open ledger is up-to-date and ready to accept new transactions for the next consensus round.

- **m_ledgerMaster.switchLCL:**  
  Updates the ledger master to point to the new last closed ledger, ensuring all components reference the correct ledger.

- **setMode:**  
  Sets the operational mode of the node based on the outcome of consensus and the ledger switch. The node may enter modes such as tracking, proposing, or observing, depending on its synchronization state.

- **Prepares for the next round:**  
  After these steps, the system is ready to begin the next consensus round, ensuring all state is consistent and up-to-date.

---

###### 3.2.4.1 setMode

**Summary:**  
Sets the operational mode of the node based on the outcome of consensus.

**Details:**  
- May switch between modes such as tracking, proposing, or observing.

---

##### 3.2.5 NetworkOPsImp::beginConsensus

**Summary:**  
Begins the next consensus round, resetting state and preparing for new proposals.

**Details:**  
- Notifies the system that a new round is starting.
- Resets timers and state machines.

---

###### 3.2.5.1 NetworkOPsImp::reportConsensusStateChange

**Summary:**  
Reports changes in the consensus state to monitoring or logging systems.

**Details:**  
- Provides visibility into consensus progress.
- May trigger alerts or logs.

---

###### 3.2.5.2 RCLConsensus::startRound

**Summary:**  
Loops back to the start of the consensus process for the next round.

**Details:**  
- Ensures continuous operation of the consensus mechanism.
"""
    user_input: str = """
app_.openLedger().accept is also called in RCLConsensus::Adaptor::doAccept. Add more details about this process to the doAccept

- return the full summary.

"""
    system_prompt = system_prompt + "\n" + user_input
    response = ai_source.agent_prompt("Developer", "Developer Coder", system_prompt)
    # write to a file
    with open("response.txt", "w") as f:
        f.write(response)


main()
