# Consensus_UNL Functionality and Architecture: Comprehensive Lesson Plan

This document provides a detailed, code-based breakdown of the Consensus_UNL (Unique Node List and Negative UNL) functionality in the XRPL (XRP Ledger) source code. It covers every aspect of the Consensus_UNL mechanism, including its architecture, validator scoring, candidate selection, deterministic voting, transaction construction, ledger application, and integration with the consensus process. All explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [Consensus_UNL Overview](#consensus_unl-overview)
- [NegativeUNLVote Class and Responsibilities](#negativeunlvote-class-and-responsibilities)
- [Validator Scoring: buildScoreTable](#validator-scoring-buildscoretable)
- [Candidate Selection: findAllCandidates](#candidate-selection-findallcandidates)
- [Deterministic Candidate Choice: choose](#deterministic-candidate-choice-choose)
- [Negative UNL Transaction Construction: addTx](#negative-unl-transaction-construction-addtx)
- [Voting Process: doVoting](#voting-process-dovoting)
- [Ledger Application: applyUNLModify](#ledger-application-applyunlmodify)
- [Consensus Integration and State Management](#consensus-integration-and-state-management)
- [Supporting Classes and Utilities](#supporting-classes-and-utilities)
- [References to Source Code](#references-to-source-code)

---

## Consensus_UNL Overview

- The Consensus_UNL mechanism in XRPL manages the set of validators that participate in consensus, including the Negative UNL (N-UNL), which temporarily disables unreliable validators without removing them permanently.
- The Negative UNL is updated through a deterministic, protocol-driven voting process, ensuring network reliability and resilience.
- The process involves scoring validator reliability, selecting candidates for disabling or re-enabling, constructing and proposing special transactions, and applying these changes to the ledger.

---

## NegativeUNLVote Class and Responsibilities

**Location:** [src/xrpld/app/misc/NegativeUNLVote.cpp.txt](src/xrpld/app/misc/NegativeUNLVote.cpp.txt), [src/xrpld/app/misc/NegativeUNLVote.h.txt](src/xrpld/app/misc/NegativeUNLVote.h.txt)

- The `NegativeUNLVote` class manages the entire voting process for the Negative UNL.
- **Key responsibilities:**
  1. Collect and score validator performance over a configurable interval using validation history.
  2. Identify candidates for disabling (adding to Negative UNL) or re-enabling (removing from Negative UNL) based on reliability scores and protocol thresholds.
  3. Deterministically select candidates for action using a randomizing pad (e.g., previous ledger hash).
  4. Construct and add transactions to the ledger to modify the Negative UNL.
  5. Track and manage new validators to avoid disabling them prematurely.
  6. Log all relevant actions and errors for debugging and auditability.
- The class interacts with the ledger, validation records, and the transaction set to coordinate Negative UNL changes as part of the consensus process.

---

## Validator Scoring: buildScoreTable

**Location:** [src/xrpld/app/misc/NegativeUNLVote.cpp.txt](src/xrpld/app/misc/NegativeUNLVote.cpp.txt)

### Function: `NegativeUNLVote::buildScoreTable`

- **Purpose:** Constructs a score table mapping each validator NodeID in the current UNL to the number of trusted validations they have issued over a recent interval of ledgers.
- **Inputs:**
  - `prevLedger`: The previous ledger.
  - `unl`: Set of trusted validator NodeIDs.
  - `validations`: Validation records.
- **Process:**
  1. Determines the next ledger sequence and instructs the validations object to keep validations for the relevant interval.
  2. Retrieves the skip list from the previous ledger to get ancestor ledgers.
  3. If there is insufficient history, returns `std::nullopt`.
  4. Initializes a score table for all NodeIDs in the UNL.
  5. For each ledger in the interval, counts trusted validations for each validator.
  6. Checks the local node's own validation count:
     - If too few, returns `std::nullopt` (unreliable measurement).
     - If within expected range, returns the score table.
     - If too many, returns `std::nullopt` (indicates a problem).
- **Output:** Optional hash map of NodeID to validation count.

**Relevant snippet:**
for (int i = 0; i < FLAG_LEDGER_INTERVAL; ++i) {
    for (auto const& v : validations.getTrustedForLedger(
             ledgerAncestors[numAncestors - 1 - i], seq - 2 - i)) {
        if (scoreTable.count(v->getNodeID()))
            ++scoreTable[v->getNodeID()];
    }
}
...
if (myValidationCount < negativeUNLMinLocalValsToVote) {
    // Not enough local validations, reliability may be wrong
    return {};
} else if (myValidationCount > negativeUNLMinLocalValsToVote &&
           myValidationCount <= FLAG_LEDGER_INTERVAL) {
    return scoreTable;
} else {
    // Too many local validations, something is wrong
    return {};
}

---

## Candidate Selection: findAllCandidates

**Location:** [src/xrpld/app/misc/NegativeUNLVote.cpp.txt](src/xrpld/app/misc/NegativeUNLVote.cpp.txt)

### Function: `NegativeUNLVote::findAllCandidates`

- **Purpose:** Identifies which validators are candidates to be disabled (added to Negative UNL) or re-enabled (removed from Negative UNL).
- **Inputs:**
  - `unl`: Set of all validator NodeIDs in the UNL.
  - `negUnl`: Set of NodeIDs currently in the Negative UNL.
  - `scoreTable`: Map of NodeID to reliability score.
- **Process:**
  1. Determines if more validators can be added to the Negative UNL, enforcing the protocol maximum (e.g., 25% of UNL).
  2. For each validator in the score table:
     - If eligible to add and score is below `negativeUNLLowWaterMark`, not already in Negative UNL, and not a new validator, add to `toDisableCandidates`.
     - If score is above `negativeUNLHighWaterMark` and currently in Negative UNL, add to `toReEnableCandidates`.
  3. If no re-enable candidates found, adds any validators in Negative UNL but no longer in the UNL to `toReEnableCandidates`.
- **Output:** Struct with vectors of NodeIDs to disable and to re-enable.

**Relevant snippet:**
auto const canAdd = [&]() -> bool {
    auto const maxNegativeListed = static_cast<std::size_t>(
        std::ceil(unl.size() * negativeUNLMaxListed));
    std::size_t negativeListed = 0;
    for (auto const& n : unl) {
        if (negUnl.count(n))
            ++negativeListed;
    }
    return negativeListed < maxNegativeListed;
}();
...
if (canAdd && score < negativeUNLLowWaterMark && !negUnl.count(nodeId) && !newValidators_.count(nodeId)) {
    candidates.toDisableCandidates.push_back(nodeId);
}
if (score > negativeUNLHighWaterMark && negUnl.count(nodeId)) {
    candidates.toReEnableCandidates.push_back(nodeId);
}
if (candidates.toReEnableCandidates.empty()) {
    for (auto const& n : negUnl) {
        if (!unl.count(n)) {
            candidates.toReEnableCandidates.push_back(n);
        }
    }
}

---

## Deterministic Candidate Choice: choose

**Location:** [src/xrpld/app/misc/NegativeUNLVote.cpp.txt](src/xrpld/app/misc/NegativeUNLVote.cpp.txt)

### Function: `NegativeUNLVote::choose`

- **Purpose:** Deterministically selects a single NodeID from a list of candidates using a randomizing pad (typically the previous ledger hash).
- **Inputs:**
  - `randomPadData`: 256-bit value (e.g., previous ledger hash).
  - `candidates`: Vector of NodeIDs.
- **Process:**
  1. Asserts the candidate list is non-empty.
  2. Converts the random pad data to a NodeID.
  3. Iterates through candidates, XORs each with the random pad, and selects the one with the smallest result.
- **Output:** The selected NodeID.

**Relevant snippet:**
NodeID randomPad = NodeID::fromVoid(randomPadData.data());
NodeID txNodeID = candidates[0];
for (int j = 1; j < candidates.size(); ++j) {
    if ((candidates[j] ^ randomPad) < (txNodeID ^ randomPad)) {
        txNodeID = candidates[j];
    }
}
return txNodeID;

---

## Negative UNL Transaction Construction: addTx

**Location:** [src/xrpld/app/misc/NegativeUNLVote.cpp.txt](src/xrpld/app/misc/NegativeUNLVote.cpp.txt)

### Function: `NegativeUNLVote::addTx`

- **Purpose:** Constructs and adds a Negative UNL modification transaction to the SHAMap of transactions for the next ledger.
- **Inputs:**
  - `seq`: Ledger sequence number.
  - `vp`: Validator public key.
  - `modify`: Action (ToDisable or ToReEnable).
  - `initialSet`: SHAMap of transactions.
- **Process:**
  1. Constructs an `STTx` of type `ttUNL_MODIFY`, setting fields for disabling/enabling, ledger sequence, and validator public key.
  2. Serializes the transaction.
  3. Adds the transaction to the SHAMap.
  4. Logs the outcome.
- **Output:** None (side effect: transaction added to SHAMap).

**Relevant snippet:**
STTx negUnlTx(ttUNL_MODIFY, [&](auto& obj) {
    obj.setFieldU8(sfUNLModifyDisabling, modify == ToDisable ? 1 : 0);
    obj.setFieldU32(sfLedgerSequence, seq);
    obj.setFieldVL(sfUNLModifyValidator, vp.slice());
});
Serializer s;
negUnlTx.add(s);
if (!initialSet->addGiveItem(
        SHAMapNodeType::tnTRANSACTION_NM,
        make_shamapitem(negUnlTx.getTransactionID(), s.slice()))) {
    // log failure
} else {
    // log success
}

---

## Voting Process: doVoting

**Location:** [src/xrpld/app/misc/NegativeUNLVote.cpp.txt](src/xrpld/app/misc/NegativeUNLVote.cpp.txt)

### Function: `NegativeUNLVote::doVoting`

- **Purpose:** Orchestrates the entire Negative UNL voting process for a consensus round.
- **Inputs:**
  - `prevLedger`: Previous ledger.
  - `unlKeys`: Set of validator public keys in the UNL.
  - `validations`: Validation records.
  - `initialSet`: SHAMap of transactions for the next ledger.
- **Process:**
  1. Builds mappings from public keys to NodeIDs for all validators in the UNL.
  2. Calls `buildScoreTable` to compute reliability scores.
  3. Retrieves the current Negative UNL and any pending disables/re-enables from the previous ledger.
  4. Adjusts the Negative UNL set to reflect in-progress changes.
  5. Builds a set of NodeIDs for all validators in the Negative UNL.
  6. Calls `purgeNewValidators` to remove new validators from tracking if present long enough.
  7. Calls `findAllCandidates` to identify candidates for disabling or re-enabling.
  8. If there are candidates to disable, selects one deterministically with `choose` and calls `addTx` to add a disable transaction.
  9. If there are candidates to re-enable, selects one and calls `addTx` to add a re-enable transaction.
- **Output:** None (side effect: transactions added to SHAMap).

**Relevant snippet:**
if (std::optional<hash_map<NodeID, std::uint32_t>> scoreTable = buildScoreTable(prevLedger, unlNodeIDs, validations)) {
    ...
    auto const candidates =
        findAllCandidates(unlNodeIDs, negUnlNodeIDs, scoreTable);
    if (!candidates.toDisableCandidates.empty()) {
        auto n = choose(prevLedger->info().hash, candidates.toDisableCandidates);
        addTx(seq, nidToKeyMap.at(n), ToDisable, initialSet);
    }
    if (!candidates.toReEnableCandidates.empty()) {
        auto n = choose(prevLedger->info().hash, candidates.toReEnableCandidates);
        addTx(seq, nidToKeyMap.at(n), ToReEnable, initialSet);
    }
}

---

## Ledger Application: applyUNLModify

**Location:** [src/xrpld/app/tx/detail/Change.cpp.txt](src/xrpld/app/tx/detail/Change.cpp.txt)

### Function: `Change::applyUNLModify`

- **Purpose:** Processes a UNL_MODIFY transaction to either disable or re-enable a validator in the Negative UNL.
- **Process:**
  1. Checks that the transaction is being applied to a flag ledger; otherwise, fails.
  2. Validates transaction fields and values, including disabling/enabling flag, ledger sequence, and validator public key.
  3. Fetches or creates the Negative UNL ledger object.
  4. Checks whether the validator is already in the Negative UNL.
  5. If disabling:
     - Fails if already pending disable, already in Negative UNL, or conflicting pending re-enable.
     - Otherwise, sets the pending disable field.
  6. If re-enabling:
     - Fails if already pending re-enable, not in Negative UNL, or conflicting pending disable.
     - Otherwise, sets the pending re-enable field.
  7. Updates the Negative UNL object in the ledger and returns success.

**Relevant snippet:**
if (!isFlagLedger(view().seq())) { ... return tefFAILURE; }
if (!ctx_.tx.isFieldPresent(sfUNLModifyDisabling) || ctx_.tx.getFieldU8(sfUNLModifyDisabling) > 1 || !ctx_.tx.isFieldPresent(sfLedgerSequence) || !ctx_.tx.isFieldPresent(sfUNLModifyValidator)) { ... return tefFAILURE; }
...
if (disabling) {
    if (alreadyPendingDisable || alreadyInNegativeUNL || conflictingPendingReEnable) {
        return tefFAILURE;
    }
    negUnlObject->setFieldVL(sfValidatorToDisable, validator);
} else {
    if (alreadyPendingReEnable || !alreadyInNegativeUNL || conflictingPendingDisable) {
        return tefFAILURE;
    }
    negUnlObject->setFieldVL(sfValidatorToReEnable, validator);
}
view().update(negUnlObject);
return tesSUCCESS;

---

## Consensus Integration and State Management

- The Negative UNL voting and transaction process is integrated into the consensus round via the `doVoting` method, which is called during ledger closing and consensus finalization.
- The validator list and Negative UNL are updated in the application state, and the consensus engine ensures that only trusted, non-disabled validators are counted for quorum and proposal processing.
- The Negative UNL is exposed via RPC and internal APIs for monitoring and diagnostics.

---

## Supporting Classes and Utilities

- **ValidatorList** ([src/xrpld/app/misc/detail/ValidatorList.cpp.txt](src/xrpld/app/misc/detail/ValidatorList.cpp.txt)):
  - Manages the trusted validator set, Negative UNL, and quorum calculation.
  - Provides methods for updating, filtering, and exposing the Negative UNL.
- **Ledger** ([src/xrpld/app/ledger/Ledger.cpp.txt](src/xrpld/app/ledger/Ledger.cpp.txt)):
  - Stores the Negative UNL state and provides accessors for current, pending disables, and re-enables.
- **RCLConsensus** ([src/xrpld/app/consensus/RCLConsensus.cpp.txt](src/xrpld/app/consensus/RCLConsensus.cpp.txt)):
  - Integrates Negative UNL voting into the consensus process.
- **SHAMap**:
  - Holds the set of transactions, including Negative UNL modification transactions, for each ledger.

---

## References to Source Code

- [NegativeUNLVote.cpp](src/xrpld/app/misc/NegativeUNLVote.cpp.txt)
- [NegativeUNLVote.h](src/xrpld/app/misc/NegativeUNLVote.h.txt)
- [Change.cpp (applyUNLModify)](src/xrpld/app/tx/detail/Change.cpp.txt)
- [ValidatorList.cpp](src/xrpld/app/misc/detail/ValidatorList.cpp.txt)
- [Ledger.cpp](src/xrpld/app/ledger/Ledger.cpp.txt)
- [RCLConsensus.cpp](src/xrpld/app/consensus/RCLConsensus.cpp.txt)
- [Consensus.h](src/xrpld/consensus/Consensus.h.txt)
- [ConsensusTypes.h](src/xrpld/consensus/ConsensusTypes.h.txt)

---

**All statements and explanations above are strictly grounded in the provided source code and documentation. No extrapolation or assumptions have been made.**