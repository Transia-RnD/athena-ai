# Consensus_Amendments Functionality and Architecture: Comprehensive Lesson Plan

This document provides a detailed, code-based breakdown of the Consensus_Amendments functionality in the XRPL (XRP Ledger) source code. It covers every aspect of Consensus_Amendments, including its architecture, amendment state management, voting, consensus integration, ledger application, persistence, and interactions with the consensus engine and ledger. All explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [Consensus_Amendments Overview](#consensus_amendments-overview)
- [AmendmentTable Architecture](#amendmenttable-architecture)
  - [AmendmentTable Interface](#amendmenttable-interface)
  - [AmendmentTableImpl Implementation](#amendmenttableimpl-implementation)
  - [AmendmentState Structure](#amendmentstate-structure)
- [Amendment Initialization and Configuration](#amendment-initialization-and-configuration)
  - [Supported Amendments and FeatureInfo](#supported-amendments-and-featureinfo)
  - [Config Sections and Database Votes](#config-sections-and-database-votes)
- [Amendment Voting Process](#amendment-voting-process)
  - [TrustedVotes and AmendmentSet](#trustedvotes-and-amendmentset)
  - [Vote Collection and Threshold Calculation](#vote-collection-and-threshold-calculation)
  - [AmendmentSet::passes](#amendmentsetpasses)
- [Consensus Integration](#consensus-integration)
  - [doVoting: Amendment Voting Logic](#dovoting-amendment-voting-logic)
  - [doValidation and getDesired](#dovalidation-and-getdesired)
- [Ledger Application and Amendment Activation](#ledger-application-and-amendment-activation)
  - [doValidatedLedger: Synchronizing State](#dovalidatedledger-synchronizing-state)
  - [Change::applyAmendment: Ledger Transaction Application](#changeapplyamendment-ledger-transaction-application)
- [Persistence and Database Interaction](#persistence-and-database-interaction)
  - [persistVote and voteAmendment](#persistvote-and-voteamendment)
  - [readAmendments](#readamendments)
- [Amendment State Query and JSON Representation](#amendment-state-query-and-json-representation)
- [Consensus Engine and Amendment Voting](#consensus-engine-and-amendment-voting)
  - [Consensus Class and RCLConsensus Adaptor](#consensus-class-and-rclconsensus-adaptor)
  - [Consensus Parameters and Thresholds](#consensus-parameters-and-thresholds)
- [Thread Safety and Synchronization](#thread-safety-and-synchronization)
- [References to Source Code](#references-to-source-code)

---

## Consensus_Amendments Overview

Consensus_Amendments is the subsystem responsible for managing protocol amendments (features/upgrades) in the XRPL. It tracks supported and enabled amendments, collects validator votes, determines amendment majorities, and coordinates the activation of amendments through the consensus process. Amendments are only enabled if they achieve at least 80% validator support for a two-week period, as enforced by the consensus and ledger logic.

- Amendments are proposed protocol changes that affect transaction processing and consensus ([README](src/xrpld/app/misc/README.md)).
- Amendments must be accepted by a network majority through a consensus process before being utilized.
- An Amendment must receive at least an 80% approval rate from validating nodes for a period of two weeks before being accepted.
- Validators that support an amendment that is not yet enabled announce their support in their validations. If 80% support is achieved, they will introduce a pseudo-transaction to track the amendment's majority status in the ledger. If an amendment holds majority status for two weeks, validators will introduce a pseudo-transaction to enable the amendment ([README](src/xrpld/app/misc/README.md)).

---

## AmendmentTable Architecture

### AmendmentTable Interface

- Defined in [AmendmentTable.h](src/xrpld/app/misc/AmendmentTable.h.txt).
- Provides methods for:
  - Finding, enabling, vetoing, and checking the status of amendments.
  - Handling voting and validation processes related to amendments.
  - Querying amendment information, tracking enabled and supported features.
  - Managing amendment voting based on network validations.
- Key methods:
  - `find`, `veto`, `unVeto`, `enable`, `isEnabled`, `isSupported`, `hasUnsupportedEnabled`, `firstUnsupportedExpected`, `getJson`, `doValidatedLedger`, `trustChanged`, `doVoting`, `doValidation`, `getDesired`.

### AmendmentTableImpl Implementation

- Implements the AmendmentTable interface ([AmendmentTable.cpp](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)).
- Manages:
  - Internal state of all known amendments (`amendmentMap_`).
  - Votes, support status, enabled status, and persistence to the database.
  - TrustedVotes and lastVote_ for tracking validator votes.
  - Thread safety via `mutex_`.
- Key members:
  - `hash_map<uint256, AmendmentState> amendmentMap_`
  - `TrustedVotes previousTrustedVotes_`
  - `std::unique_ptr<AmendmentSet> lastVote_`
  - `bool unsupportedEnabled_`
  - `std::optional<NetClock::time_point> firstUnsupportedExpected_`
  - `DatabaseCon& db_`

### AmendmentState Structure

- Represents the state of a single amendment ([AmendmentTable.cpp](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - `AmendmentVote vote` (up, down, obsolete)
  - `bool enabled`
  - `bool supported`
  - `std::string name`

---

## Amendment Initialization and Configuration

### Supported Amendments and FeatureInfo

- Amendments are registered at startup using the `FeatureInfo` struct ([AmendmentTable.h](src/xrpld/app/misc/AmendmentTable.h.txt)):
  - `std::string const name`
  - `uint256 const feature`
  - `VoteBehavior const vote`
- The list of supported amendments is constructed from the protocol's feature registry ([Feature.cpp](src/libxrpl/protocol/Feature.cpp.txt), [features.macro](include/xrpl/protocol/detail/features.macro)).
- Each supported amendment is added to the internal map with its name, support status, and default vote ([AmendmentTableImpl::AmendmentTableImpl](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - If `VoteBehavior::DefaultYes`, set vote to `AmendmentVote::up`.
  - If `VoteBehavior::DefaultNo`, set vote to `AmendmentVote::down`.
  - If `VoteBehavior::Obsolete`, set vote to `AmendmentVote::obsolete`.

### Config Sections and Database Votes

- The `[amendments]` and `[veto_amendments]` sections in the config file specify amendments to be enabled or vetoed.
- If the `FeatureVotes` table exists in the database, config sections are ignored in favor of persisted votes ([AmendmentTableImpl::AmendmentTableImpl](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)).
- Votes are persisted using `persistVote`, which records the vote in the database ([persistVote](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt), [voteAmendment](src/xrpld/app/rdb/detail/Wallet.cpp.txt)).
- The latest votes are loaded from the database using `readAmendments` ([readAmendments](src/xrpld/app/rdb/detail/Wallet.cpp.txt)).

---

## Amendment Voting Process

### TrustedVotes and AmendmentSet

- `TrustedVotes` tracks votes from trusted validators and manages their timeouts ([AmendmentTable.cpp](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)).
- `AmendmentSet` aggregates votes for each amendment and computes which amendments have enough votes to pass ([AmendmentSet](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - `hash_map<uint256, int> votes_`
  - `int trustedValidations_`
  - `int threshold_`

### Vote Collection and Threshold Calculation

- Votes are collected from trusted validations in each consensus round ([AmendmentSet::AmendmentSet](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - Calls `trustedVotes.getVotes(rules, lock)` to get the number of trusted validations and votes per amendment.
  - Computes the threshold for passing using `computeThreshold`:
    - If `fixAmendmentMajorityCalc` is not enabled, uses `preFixAmendmentMajorityCalcThreshold` (typically 80%).
    - If enabled, uses `postFixAmendmentMajorityCalcThreshold`.
    - Always at least 1.

### AmendmentSet::passes

- Determines if an amendment has enough votes to pass ([AmendmentSet::passes](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - Looks up the amendment in `votes_`.
  - Returns true if the number of votes is greater than or equal to `threshold_`, false otherwise.

---

## Consensus Integration

### doVoting: Amendment Voting Logic

- `AmendmentTableImpl::doVoting` is called each consensus round to determine amendment actions ([AmendmentTableImpl::doVoting](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - Updates trusted votes from current validations.
  - Builds an `AmendmentSet` to aggregate votes.
  - For each amendment:
    - If already enabled, skip.
    - Determine if it has validator majority (`vote->passes`), ledger majority (recorded in the ledger), and the time it achieved majority.
    - Decide actions:
      - If it just achieved majority, signal `tfGotMajority`.
      - If it lost majority, signal `tfLostMajority`.
      - If it has held majority for the required period, signal enablement.
      - Otherwise, log status.
  - Returns a map of amendment hashes to action codes (e.g., `tfGotMajority`, `tfLostMajority`, 0 for enablement).

### doValidation and getDesired

- `doValidation` determines which amendments to advertise as supported in validation messages ([AmendmentTableImpl::doValidation](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - Returns a sorted vector of amendment hashes that are supported, upvoted, and not already enabled.
- `getDesired` calls `doValidation` with an empty set, returning all amendments the node desires to see enabled ([AmendmentTableImpl::getDesired](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)).

---

## Ledger Application and Amendment Activation

### doValidatedLedger: Synchronizing State

- `AmendmentTableImpl::doValidatedLedger` is called after a ledger is validated ([AmendmentTableImpl::doValidatedLedger](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - Enables all amendments marked as enabled in the ledger.
  - Updates internal state for amendments with majority but not yet enabled.
  - Tracks when unsupported amendments are expected to be enabled.
  - Records the last processed ledger sequence.

### Change::applyAmendment: Ledger Transaction Application

- The `Change::applyAmendment` function applies amendment pseudo-transactions to the ledger ([Change.cpp](src/xrpld/app/tx/detail/Change.cpp.txt)):
  - Retrieves the amendment hash from the transaction.
  - Checks if the amendment is already enabled; if so, returns `tefALREADY`.
  - Handles flags for `tfGotMajority` and `tfLostMajority`:
    - Updates the `sfMajorities` field in the amendment object.
    - If `gotMajority`, adds a new majority entry with the amendment and close time.
    - If `lostMajority`, removes the majority entry.
  - If neither flag is set, enables the amendment:
    - Adds the amendment to the `sfAmendments` field.
    - Calls `activateTrustLinesToSelfFix` if the amendment is `fixTrustLinesToSelf`.
    - Calls `ctx_.app.getAmendmentTable().enable(amendment)`.
    - If the amendment is not supported, logs an error and blocks the server (`setAmendmentBlocked`).
  - Updates the amendment object in the ledger and returns `tesSUCCESS`.

---

## Persistence and Database Interaction

### persistVote and voteAmendment

- `AmendmentTableImpl::persistVote` records the current vote for an amendment in the database ([persistVote](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - Asserts the vote is not obsolete.
  - Obtains a database session and calls `voteAmendment`.
- `voteAmendment` inserts a row into the `FeatureVotes` table with the amendment hash, name, and vote ([voteAmendment](src/xrpld/app/rdb/detail/Wallet.cpp.txt)):
  - Begins a transaction.
  - Constructs and executes an SQL `INSERT` statement.
  - Commits the transaction.

### readAmendments

- `readAmendments` reads the latest votes for amendments from the `FeatureVotes` table ([readAmendments](src/xrpld/app/rdb/detail/Wallet.cpp.txt)):
  - Uses a SQL window function to select the most recent entry for each amendment.
  - For each row, invokes a callback with the amendment hash, name, and vote.
  - The caller validates the fields and updates internal state accordingly.

---

## Amendment State Query and JSON Representation

- `getJson` provides a JSON representation of the amendment state ([AmendmentTableImpl::getJson](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)):
  - For each amendment, includes name, support status, enabled status, vote, and (if not enabled) vote counts and thresholds.
  - Used for API responses and monitoring.

---

## Consensus Engine and Amendment Voting

### Consensus Class and RCLConsensus Adaptor

- The consensus process is managed by the generic `Consensus` class ([Consensus.h](src/xrpld/consensus/Consensus.h.txt)), parameterized by an Adaptor.
- The XRPL-specific adaptor is `RCLConsensus` ([RCLConsensus.cpp](src/xrpld/app/consensus/RCLConsensus.cpp.txt), [RCLConsensus.h](src/xrpld/app/consensus/RCLConsensus.h.txt)):
  - Handles acquiring ledgers, sharing proposals, building new ledgers, and applying transactions.
  - Integrates with the amendment voting subsystem by calling `doVoting` and `doValidation` as part of the consensus round.

### Consensus Parameters and Thresholds

- Consensus timing and thresholds are controlled by `ConsensusParms` ([ConsensusParms.h](src/xrpld/consensus/ConsensusParms.h.txt)):
  - `minCONSENSUS_PCT` (typically 80%) is the minimum percentage of agreement required.
  - `ledgerMIN_CONSENSUS`, `ledgerMAX_CONSENSUS` control round durations.
  - The threshold for amendment passage is computed in `AmendmentSet::computeThreshold` based on the number of trusted validations and protocol rules.

---

## Thread Safety and Synchronization

- All amendment state changes are protected by a mutex (`mutex_`) in `AmendmentTableImpl` ([AmendmentTable.cpp](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)).
- Database operations are performed within transactions to ensure atomicity.
- The consensus engine uses its own synchronization mechanisms to manage peer proposals and round progression.

---

## References to Source Code

- [AmendmentTable.h](src/xrpld/app/misc/AmendmentTable.h.txt)
- [AmendmentTable.cpp](src/xrpld/app/misc/detail/AmendmentTable.cpp.txt)
- [Feature.cpp](src/libxrpl/protocol/Feature.cpp.txt)
- [features.macro](include/xrpl/protocol/detail/features.macro)
- [Wallet.cpp](src/xrpld/app/rdb/detail/Wallet.cpp.txt)
- [Wallet.h](src/xrpld/app/rdb/Wallet.h.txt)
- [Change.cpp](src/xrpld/app/tx/detail/Change.cpp.txt)
- [Consensus.h](src/xrpld/consensus/Consensus.h.txt)
- [Consensus.cpp](src/xrpld/consensus/Consensus.cpp.txt)
- [ConsensusParms.h](src/xrpld/consensus/ConsensusParms.h.txt)
- [ConsensusTypes.h](src/xrpld/consensus/ConsensusTypes.h.txt)
- [RCLConsensus.cpp](src/xrpld/app/consensus/RCLConsensus.cpp.txt)
- [RCLConsensus.h](src/xrpld/app/consensus/RCLConsensus.h.txt)
- [README.md (Amendments)](src/xrpld/app/misc/README.md)
- [README.md (Consensus)](src/xrpld/consensus/README.md)

---

**All statements and explanations above are directly supported by the provided code and context. No assumptions or extrapolations have been made.**