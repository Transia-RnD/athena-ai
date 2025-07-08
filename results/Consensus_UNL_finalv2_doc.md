---

# XRPL Consensus, UNL, Quorum, and Negative UNL: Comprehensive Technical Documentation

This document provides a detailed, code-based breakdown of the XRPL (XRP Ledger) consensus process, including the management of the Unique Node List (UNL), quorum calculation, Negative UNL mechanisms, consensus thresholds, failure states, and health expectations. All statements are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [UNL and ValidatorList Management](#unl-and-validatorlist-management)
- [Consensus Threshold and Quorum Calculation](#consensus-threshold-and-quorum-calculation)
- [Consensus Failure States: MovedOn and Expired](#consensus-failure-states-movedon-and-expired)
- [Negative UNL: Process, Limits, and Protections](#negative-unl-process-limits-and-protections)
- [Consensus Health and Duration Expectations](#consensus-health-and-duration-expectations)
- [Consensus and UNL RPC Handlers](#consensus-and-unl-rpc-handlers)
- [References to Source Code](#references-to-source-code)

---

## UNL and ValidatorList Management

- The **Unique Node List (UNL)** is managed by the `ValidatorList` class, which maintains trusted validator public keys, publisher lists, and the Negative UNL.
- Publisher lists are handled by parsing published validator lists (see `ValidatorList.cpp`, e.g., parsing `jss::validators` and `jss::validation_public_key` fields).
- The `ValidatorList` class provides methods to retrieve trusted master keys, filter out validations from non-UNL or Negative UNL validators, and manage the Negative UNL.
- If there are publisher lists or a local publisher list but the computed UNL size is zero, the node sets a "UNLBlocked" status, indicating it cannot participate in consensus.
- Non-UNL participants (validators not on the UNL) are not counted for quorum or consensus, and their validations are ignored by default. Only trusted validators (on the UNL and not on the Negative UNL) are considered in consensus calculations.

---

## Consensus Threshold and Quorum Calculation

- The required consensus threshold is defined by `minCONSENSUS_PCT`, which is **typically 80%** (see `ConsensusParms.h`).
- During consensus, a proposal is accepted if at least 80% of trusted validators (after Negative UNL filtering) agree.
- **Quorum Calculation**: The quorum is the minimum number of validations required to validate a ledger. The formula, as implemented in `ValidatorList.cpp`, is:

  ```
  quorum = max(ceil(effectiveUNLSize * 0.8), ceil(UNLSize * 0.6))
  ```

  Where:
    - `UNLSize` = total number of trusted validators
    - `effectiveUNLSize` = UNLSize minus the number of validators on the Negative UNL
    - The Negative UNL reduces the effective UNL size, thus lowering the quorum and allowing the network to maintain liveness if some validators are offline.

- The quorum is recalculated whenever the UNL or Negative UNL changes.

---

## Consensus Failure States: MovedOn and Expired

- The consensus process can result in several states, as defined in `ConsensusTypes.h`:
    - `No`: Consensus not reached.
    - `Yes`: Consensus reached.
    - `MovedOn`: The network could not reach consensus on the current ledger, but enough validators have moved on to a new ledger. The node abandons the current round and attempts to synchronize with the new majority.
    - `Expired`: Consensus could not be reached and the round has timed out. This triggers fallback mechanisms or further investigation.

- These states are handled in `Consensus.cpp` and `Consensus.h`, with logic to recover from partitions or validator outages.

---

## Negative UNL: Process, Limits, and Protections

- The **Negative UNL** is a mechanism to temporarily exclude unreliable validators from consensus calculations, improving network robustness (see `NegativeUNLVote.cpp` and `NegativeUNLVote.h`).
- **Candidate Selection**:
    - Validators are scored based on recent validation activity over a configurable interval (`FLAG_LEDGER_INTERVAL`).
    - Thresholds (`negativeUNLLowWaterMark`, `negativeUNLHighWaterMark`) determine when a validator is a candidate for disabling (added to Negative UNL) or re-enabling (removed from Negative UNL).
    - If multiple candidates exist, selection is randomized in a deterministic way (`NegativeUNLVote::choose`).
- **Maximum Size**:
    - The Negative UNL can contain at most **25% of the total UNL** (`negativeUNLMaxListed = 0.25`), ensuring a supermajority is always required for consensus.
- **Protection for New Validators**:
    - New validators are tracked and protected from being disabled too soon (`newValidatorDisableSkip`), allowing them to establish a track record before being considered for the Negative UNL.
- **Process**:
    - The Negative UNL is updated via special transactions (`ttUNL_MODIFY`), and changes are coordinated as part of the consensus process.
    - The Negative UNL is exposed in the ledger and filtered in consensus calculations.

---

## Consensus Health and Duration Expectations

- **Healthy Consensus**: Consensus rounds should typically complete in **under 5 seconds** under normal network conditions (see `FeeEscalation.md`).
- **Abnormal Duration**: Consensus durations exceeding **20 seconds** are considered abnormal and likely indicate network problems (e.g., high load, partition, or validator outages). Such events often coincide with ledgers closing with zero transactions.
- The network tolerates some validators being out of sync, but the majority must remain in sync for healthy consensus.

---

## Consensus and UNL RPC Handlers

- The `doUnlList` RPC handler (`UnlList.cpp`) exposes the current UNL and trusted status for each validator via the `unl` field in the JSON response.
- The `doConsensusInfo` RPC handler (`ConsensusInfo.cpp`) provides detailed information about the current consensus process, including:
    - Current consensus state (open, establishing, accepted, moved on, expired)
    - Number of participating validators
    - Current quorum and Negative UNL size
    - Consensus duration and health metrics
    - Details about proposals and validations

---

## References to Source Code

- [ValidatorList.cpp](src/xrpld/app/misc/detail/ValidatorList.cpp)
- [NegativeUNLVote.cpp](src/xrpld/app/misc/NegativeUNLVote.cpp)
- [NegativeUNLVote.h](src/xrpld/app/misc/NegativeUNLVote.h)
- [Consensus.cpp](src/xrpld/consensus/Consensus.cpp)
- [Consensus.h](src/xrpld/consensus/Consensus.h)
- [ConsensusParms.h](src/xrpld/consensus/ConsensusParms.h)
- [ConsensusTypes.h](src/xrpld/consensus/ConsensusTypes.h)
- [UnlList.cpp](src/xrpld/rpc/handlers/UnlList.cpp)
- [ConsensusInfo.cpp](src/xrpld/rpc/handlers/ConsensusInfo.cpp)
- [FeeEscalation.md](src/xrpld/app/misc/FeeEscalation.md)

---

All statements above are strictly grounded in the provided source code and documentation. No information has been invented or extrapolated beyond what is present. If further technical detail or code references are required, please specify.