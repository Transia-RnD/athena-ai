# XRPL Ledger Functionality and Architecture: Comprehensive Lesson Plan

This document provides a detailed, code-based breakdown of the Ledger functionality in the XRPL (XRP Ledger) source code. It covers every aspect of the ledger system, including its architecture, acquisition, assembly, validation, storage, publication, and the interaction between all relevant components. All explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [Ledger Overview](#ledger-overview)
- [Ledger Data Structures](#ledger-data-structures)
  - [Ledger Class](#ledger-class)
  - [LedgerInfo](#ledgerinfo)
  - [LedgerHolder](#ledgerholder)
  - [LedgerHistory](#ledgerhistory)
- [Ledger Acquisition and Assembly](#ledger-acquisition-and-assembly)
  - [LedgerMaster](#ledgermaster)
  - [InboundLedgers and InboundLedger](#inboundledgers-and-inboundledger)
  - [Ledger Acquisition Process](#ledger-acquisition-process)
- [Ledger Validation and Acceptance](#ledger-validation-and-acceptance)
  - [Validation Quorum and Trusted Validations](#validation-quorum-and-trusted-validations)
  - [LedgerMaster::checkAccept](#ledgermastercheckaccept)
  - [LedgerMaster::tryAdvance](#ledgermastertryadvance)
- [Ledger Storage and Caching](#ledger-storage-and-caching)
  - [LedgerHistory::insert](#ledgerhistoryinsert)
  - [Database Storage](#database-storage)
- [Ledger Publication and Streaming](#ledger-publication-and-streaming)
  - [LedgerMaster::findNewLedgersToPublish](#ledgermasterfindnewledgerstopublish)
- [Ledger Entry Types](#ledger-entry-types)
- [Ledger RPC and Query Handlers](#ledger-rpc-and-query-handlers)
- [Ledger Immutability and State Management](#ledger-immutability-and-state-management)
- [Ledger Cleaning and Repair](#ledger-cleaning-and-repair)
- [References to Source Code](#references-to-source-code)

---

## Ledger Overview

- The XRPL ledger is the authoritative record of the network's state at a given point in time. It contains all account balances, offers, escrows, and other objects, as well as a record of all transactions included in that ledger.
- Every server always has an open ledger. All received new transactions are applied to the open ledger. The open ledger can't close until consensus is reached on the previous ledger and either there is at least one transaction or the ledger's close time has been reached ([README](src/xrpld/app/ledger/README.md)).
- The ledger header contains the sequence number, parent hash, hash of the previous ledger, hash of the root node of the state tree, and other metadata ([README](src/xrpld/app/ledger/README.md)).

---

## Ledger Data Structures

### Ledger Class

- Defined in [Ledger.h](src/xrpld/app/ledger/Ledger.h.txt) and implemented in [Ledger.cpp](src/xrpld/app/ledger/Ledger.cpp.txt).
- Represents a single ledger instance, managing state and transaction data.
- Key members:
  - `LedgerInfo info_`: Metadata about the ledger (sequence, hash, parent hash, close time, etc.).
  - `SHAMap stateMap_`: The state tree (account state).
  - `SHAMap txMap_`: The transaction tree.
  - `bool mImmutable`: Indicates if the ledger is immutable.
  - `Rules rules_`: Protocol rules and amendments.
- Construction:
  - Can be created from genesis, from a previous ledger, from serialized data, or loaded from storage.
  - Example constructor for genesis:
    Ledger::Ledger(create_genesis_t, Config const& config, std::vector<uint256> const& amendments, Family& family)
  - When constructed, the ledger's hash is calculated and stored in `info_.hash`.
- Immutability:
  - Once a ledger is finalized, `setImmutable()` is called, which sets `mImmutable = true` and marks the SHAMaps as immutable.
  - Only immutable ledgers can be set in a `LedgerHolder` ([LedgerHolder.h](src/xrpld/app/ledger/LedgerHolder.h.txt)).

### LedgerInfo

- Holds metadata for a ledger, including:
  - `seq`: Sequence number.
  - `hash`: Ledger hash.
  - `parentHash`: Hash of the previous ledger.
  - `accountHash`: Hash of the state tree root.
  - `txHash`: Hash of the transaction tree root.
  - `closeTime`, `closeTimeResolution`, `closeFlags`, etc.
- Used throughout the codebase for ledger identification and validation.

### LedgerHolder

- Defined in [LedgerHolder.h](src/xrpld/app/ledger/LedgerHolder.h.txt).
- Manages a thread-safe, immutable shared pointer to a Ledger object.
- Methods:
  - `set(std::shared_ptr<Ledger const> ledger)`: Sets a new immutable ledger.
  - `get()`: Retrieves the current ledger.
  - `empty()`: Checks if a ledger is held.

### LedgerHistory

- Defined in [LedgerHistory.h](src/xrpld/app/ledger/LedgerHistory.h.txt) and implemented in [LedgerHistory.cpp](src/xrpld/app/ledger/LedgerHistory.cpp.txt).
- Manages the storage, retrieval, and validation of ledger objects.
- Maintains:
  - `m_ledgers_by_hash`: Cache of ledgers by hash.
  - `mLedgersByIndex`: Map of sequence number to hash.
- Key methods:
  - `insert(std::shared_ptr<Ledger const> const& ledger, bool validated)`: Inserts a ledger into the cache.
  - `getLedgerBySeq(LedgerIndex ledgerIndex)`: Retrieves a ledger by sequence.
  - `getLedgerByHash(LedgerHash const& ledgerHash)`: Retrieves a ledger by hash.
  - `fixIndex(LedgerIndex ledgerIndex, LedgerHash const& ledgerHash)`: Fixes index-to-hash mapping.

---

## Ledger Acquisition and Assembly

### LedgerMaster

- Defined in [LedgerMaster.h](src/xrpld/app/ledger/LedgerMaster.h.txt) and implemented in [LedgerMaster.cpp](src/xrpld/app/ledger/detail/LedgerMaster.cpp.txt).
- Central manager for ledger state, acquisition, validation, and publication.
- Tracks:
  - Last published ledger (`mPubLedger`).
  - Last validated ledger (`mValidLedger`).
  - Ledger history (`mLedgerHistory`).
- Orchestrates the acquisition of missing historical ledgers via `doAdvance()` and `fetchForHistory()` ([README](src/xrpld/app/ledger/README.md)).
- Example: When a gap is detected (e.g., ledgers 603 and 600 are present, but 601 and 602 are missing), `LedgerMaster` requests ledger 602 first, then back-fills 601 ([README](src/xrpld/app/ledger/README.md)).

### InboundLedgers and InboundLedger

- [InboundLedgers.h](src/xrpld/app/ledger/InboundLedgers.h.txt) defines the abstract interface for managing inbound ledger acquisitions.
- [InboundLedgers.cpp](src/xrpld/app/ledger/detail/InboundLedgers.cpp.txt) implements `InboundLedgersImp`, which manages ongoing acquisitions, tracks failures, and processes incoming data.
- [InboundLedger.cpp](src/xrpld/app/ledger/detail/InboundLedger.cpp.txt) implements `InboundLedger`, which handles the acquisition and assembly of a specific ledger.
- Acquisition process:
  - `InboundLedgers::acquire(hash, seq, reason)` is called to acquire a ledger.
  - If already in progress, returns the existing `InboundLedger`.
  - Otherwise, creates a new `InboundLedger`, adds it to the map, and calls `init()` to start acquisition.
  - `InboundLedger::init()` checks local storage, fetch packs, and requests missing data from peers.
  - Incoming data is handled by `InboundLedger::gotData()`, which queues data for processing.
  - When complete, `InboundLedger::done()` finalizes the acquisition, marks the ledger immutable, and schedules a job for post-acquisition processing.

### Ledger Acquisition Process

**Step-by-step process:**

1. **Triggering Acquisition**
   - `LedgerMaster::doAdvance()` detects missing ledgers and calls `fetchForHistory()` for each missing sequence.
   - `fetchForHistory()` tries to get the hash for the missing ledger, then attempts to retrieve it from local storage.
   - If not found, calls `InboundLedgers::acquire()` to start network acquisition.

2. **Managing Ongoing Acquisitions**
   - `InboundLedgers::acquire()` checks if the acquisition is already in progress.
   - If not, creates a new `InboundLedger` and calls `init()`.

3. **Fetching and Assembling**
   - `InboundLedger::init()` checks local storage and fetch packs.
   - If not complete, requests missing data from peers.
   - Incoming data is queued by `gotData()` and processed in batches.
   - When all required data is present, the ledger is assembled and validated.

4. **Completion and Finalization**
   - `InboundLedger::done()` is called when acquisition is complete or failed.
   - If successful, marks the ledger immutable and stores it via `LedgerMaster::storeLedger()`.
   - Schedules a job on the job queue to call `LedgerMaster::checkAccept()` and `tryAdvance()`.

5. **Job Queue**
   - The job queue ensures that finalization and acceptance are performed asynchronously and safely.

**Relevant code snippets:**

- `InboundLedgersImp::acquire` ([InboundLedgers.cpp.txt]):
  if (inbound->isFailed())
      return {};
  if (!isNew)
      inbound->update(seq);
  if (!inbound->isComplete())
      return {};
  return inbound->getLedger();

- `InboundLedger::done` ([InboundLedger.cpp.txt]):
  if (complete_ && !failed_ && mLedger) {
      mLedger->setImmutable();
      switch (mReason) {
          case Reason::HISTORY:
              app_.getInboundLedgers().onLedgerFetched();
              break;
          default:
              app_.getLedgerMaster().storeLedger(mLedger);
              break;
      }
  }
  app_.getJobQueue().addJob(
      jtLEDGER_DATA, "AcquisitionDone", [self = shared_from_this()]() {
          if (self->complete_ && !self->failed_) {
              self->app_.getLedgerMaster().checkAccept(self->getLedger());
              self->app_.getLedgerMaster().tryAdvance();
          } else
              self->app_.getInboundLedgers().logFailure(
                  self->hash_, self->mSeq);
      });

---

## Ledger Validation and Acceptance

### Validation Quorum and Trusted Validations

- The system requires a minimum number of trusted validations (`minVal`) for a ledger to be accepted as validated.
- Trusted validations are collected for the ledger's hash and sequence, filtered by the negative UNL (Unique Node List).
- If the number of trusted validations is less than `minVal`, the ledger is not accepted.

### LedgerMaster::checkAccept

- [LedgerMaster.cpp.txt]:
  if (!canBeCurrent(ledger))
      return;
  std::lock_guard ml(m_mutex);
  if (ledger->info().seq <= mValidLedgerSeq)
      return;
  auto const minVal = getNeededValidations();
  auto validations = app_.validators().negativeUNLFilter(
      app_.getValidations().getTrustedForLedger(
          ledger->info().hash, ledger->info().seq));
  auto const tvc = validations.size();
  if (tvc < minVal) {
      JLOG(m_journal.trace()) << "Only " << tvc << " validations for " << ledger->info().hash;
      return;
  }
  JLOG(m_journal.info()) << "Advancing accepted ledger to " << ledger->info().seq << " with >= " << minVal << " validations";
  ledger->setValidated();
  ledger->setFull();
  setValidLedger(ledger);

- If the ledger is accepted:
  - Marks the ledger as validated and full.
  - Updates the internal state to reflect the new validated ledger.
  - If this is the first published ledger, sets it as the published ledger and sets up the order book database.
  - Handles fee voting and amendment warnings as needed.
  - Calls `tryAdvance()` to continue advancing the ledger state.

### LedgerMaster::tryAdvance

- Attempts to advance the ledger state machine, possibly triggering further acquisitions if more ledgers are missing.
- Ensures that the server maintains a continuous stream of consecutive ledgers.

---

## Ledger Storage and Caching

### LedgerHistory::insert

- [LedgerHistory.cpp.txt]:
  bool
  insert(std::shared_ptr<Ledger const> const& ledger, bool validated)
  {
      // Extract hash and sequence
      // Insert into m_ledgers_by_hash
      // Update mLedgersByIndex
      // Handle validated ledgers
      // Return true if newly inserted, false if already present
  }
- Ensures that the ledger is available in the server's internal caches for fast lookup by both hash and sequence number.

### Database Storage

- Ledgers are persisted to the database using functions in [Node.cpp.txt] and [SQLiteDatabase.cpp.txt].
- Before saving, the code checks that the account hash and transaction hash match the SHAMap roots.
- Example ([Node.cpp.txt]):
  if (ledger->info().accountHash != ledger->stateMap().getHash().as_uint256()) {
      // Fatal error: mismatched account hash
  }
  XRPL_ASSERT(
      ledger->info().txHash == ledger->txMap().getHash().as_uint256(),
      "ripple::detail::saveValidatedLedger : transaction hash match");

- The ledger header and SHAMap roots are serialized and stored in the database for future retrieval.

---

## Ledger Publication and Streaming

### LedgerMaster::findNewLedgersToPublish

- [LedgerMaster.cpp.txt]:
  int acqCount = 0;
  auto pubSeq = mPubLedgerSeq + 1;
  auto valLedger = mValidLedger.get();
  std::uint32_t valSeq = valLedger->info().seq;
  for (std::uint32_t seq = pubSeq; seq <= valSeq; ++seq) {
      // Try to fetch/publish valid ledger seq
      std::shared_ptr<Ledger const> ledger;
      auto hash = hashOfSeq(valLedger, seq, m_journal);
      if (!hash)
          hash = beast::zero;
      if (seq == valSeq) {
          ledger = valLedger;
      } else if (hash->isZero()) {
          // Fatal: ledger does not have hash for seq
      } else {
          ledger = mLedgerHistory.getLedgerByHash(*hash);
      }
      if (!app_.config().LEDGER_REPLAY) {
          if (!ledger && (++acqCount < ledger_fetch_size_))
              ledger = app_.getInboundLedgers().acquire(*hash, seq, InboundLedger::Reason::GENERIC);
      }
      if (ledger && (ledger->info().seq == pubSeq)) {
          ledger->setValidated();
          ret.push_back(ledger);
          ++pubSeq;
      }
  }
  JLOG(m_journal.trace()) << "ready to publish " << ret.size() << " ledgers.";
- Publishes a stream of consecutive validated ledgers to clients, ensuring all validated ledgers are published in order as they become available.

---

## Ledger Entry Types

- Ledger entries are defined using the `LEDGER_ENTRY` macro in [ledger_entries.macro](include/xrpl/protocol/detail/ledger_entries.macro).
- Each entry type has a unique type ID, name, and a set of required/optional fields.
- Examples:
  - `ltACCOUNT_ROOT`: Account root object.
  - `ltOFFER`: Offer on the DEX.
  - `ltESCROW`: Escrow object.
  - `ltAMM`: Automated Market Maker pool.
  - `ltNFTOKEN_PAGE`: NFT page.
  - `ltPAYCHAN`: Payment channel.
  - `ltBRIDGE`: Cross-chain bridge.
  - `ltCHECK`: Check object.
  - `ltSIGNER_LIST`: Signer list for multi-signature.
  - `ltDIR_NODE`: Directory node.
  - `ltLEDGER_HASHES`: Skip list for efficient ledger traversal.
  - Many others, including custom and singleton types.

- Each entry type specifies its fields and their required/optional status.

---

## Ledger RPC and Query Handlers

- The RPC layer provides handlers for querying ledger data.
- [LedgerHandler.h](src/xrpld/rpc/handlers/LedgerHandler.h.txt) defines the handler for the `ledger` RPC command.
- [LedgerEntry.cpp.txt] implements the handler for the `ledger_entry` RPC command, supporting all entry types.
- [RPCHelpers.cpp.txt] provides helper functions for resolving ledgers by hash, index, or shortcut (current, closed, validated), and for injecting ledger entry data into JSON responses.
- The handlers support both JSON and binary output formats, and provide detailed error handling for malformed requests or missing data.

---

## Ledger Immutability and State Management

- Once a ledger is finalized, it is marked as immutable using `Ledger::setImmutable()`.
- Only immutable ledgers can be set in a `LedgerHolder`.
- Immutability ensures that the ledger's state cannot be changed after it is validated and published.
- The system enforces this invariant throughout the codebase.

---

## Ledger Cleaning and Repair

- [LedgerCleaner.cpp.txt] implements the `LedgerCleaner` component, which can check for missing or inconsistent ledger nodes and transactions, and attempts to fix them by reacquiring or saving ledgers as needed.
- The cleaning process is careful to avoid running during high server load and tracks failures, retrying as necessary.
- The process can be configured to check nodes, fix transactions, and operate over a specified ledger range.

---

## References to Source Code

- [Ledger.h](src/xrpld/app/ledger/Ledger.h.txt)
- [Ledger.cpp](src/xrpld/app/ledger/Ledger.cpp.txt)
- [LedgerHolder.h](src/xrpld/app/ledger/LedgerHolder.h.txt)
- [LedgerHistory.h](src/xrpld/app/ledger/LedgerHistory.h.txt)
- [LedgerHistory.cpp](src/xrpld/app/ledger/LedgerHistory.cpp.txt)
- [LedgerMaster.h](src/xrpld/app/ledger/LedgerMaster.h.txt)
- [LedgerMaster.cpp](src/xrpld/app/ledger/detail/LedgerMaster.cpp.txt)
- [InboundLedgers.h](src/xrpld/app/ledger/InboundLedgers.h.txt)
- [InboundLedgers.cpp](src/xrpld/app/ledger/detail/InboundLedgers.cpp.txt)
- [InboundLedger.cpp](src/xrpld/app/ledger/detail/InboundLedger.cpp.txt)
- [ledger_entries.macro](include/xrpl/protocol/detail/ledger_entries.macro)
- [LedgerHandler.h](src/xrpld/rpc/handlers/LedgerHandler.h.txt)
- [LedgerEntry.cpp](src/xrpld/rpc/handlers/LedgerEntry.cpp.txt)
- [RPCHelpers.cpp](src/xrpld/rpc/detail/RPCHelpers.cpp.txt)
- [LedgerCleaner.cpp](src/xrpld/app/ledger/detail/LedgerCleaner.cpp.txt)
- [Node.cpp](src/xrpld/app/rdb/backend/detail/Node.cpp.txt)
- [SQLiteDatabase.cpp](src/xrpld/app/rdb/backend/detail/SQLiteDatabase.cpp.txt)

---

**All statements and explanations above are strictly grounded in the provided source code and documentation. No assumptions or extrapolations have been made.**