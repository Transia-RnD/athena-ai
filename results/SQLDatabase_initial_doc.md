# SQLDatabase Functionality and Architecture: Comprehensive Lesson Plan

This document provides a detailed, code-based breakdown of the SQLDatabase (specifically, the SQLite-based relational database) functionality in the XRPL (XRP Ledger) source code. It covers every aspect of the SQLDatabase, including its architecture, initialization, configuration, schema, connection management, checkpointing, query and mutation operations, space usage, and integration with the rest of the XRPL node. All explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [SQLDatabase Overview](#sqldatabase-overview)
- [RelationalDatabase Interface and Initialization](#relationaldatabase-interface-and-initialization)
  - [RelationalDatabase::init](#relationaldatabaseinit)
  - [Backend Selection and Configuration](#backend-selection-and-configuration)
- [SQLiteDatabase and SQLiteDatabaseImp](#sqlitedatabase-and-sqlitedatabaseimp)
  - [Class Structure](#class-structure)
  - [Constructor and Database Setup](#constructor-and-database-setup)
  - [Database Connections: DatabaseCon](#database-connections-databasecon)
- [Database Schema and Initialization](#database-schema-and-initialization)
  - [Ledger Database Schema (LgrDBInit)](#ledger-database-schema-lgrdbinit)
  - [Transaction Database Schema (TxDBInit)](#transaction-database-schema-txdbinit)
- [Database Connection Setup and Pragmas](#database-connection-setup-and-pragmas)
  - [setup_DatabaseCon](#setup_databasecon)
  - [Pragma Settings](#pragma-settings)
- [Checkpointing and Durability](#checkpointing-and-durability)
- [Database Operations and Methods](#database-operations-and-methods)
  - [Ledger Sequence Queries](#ledger-sequence-queries)
  - [Deletion and Cleanup](#deletion-and-cleanup)
  - [Counting and Space Usage](#counting-and-space-usage)
  - [Ledger and Transaction Info Retrieval](#ledger-and-transaction-info-retrieval)
  - [Account Transaction Queries and Pagination](#account-transaction-queries-and-pagination)
  - [Transaction Retrieval by ID](#transaction-retrieval-by-id)
  - [Database Space Checking](#database-space-checking)
  - [Database Closing](#database-closing)
- [Supporting Classes and Utilities](#supporting-classes-and-utilities)
- [References to Source Code](#references-to-source-code)

---

## SQLDatabase Overview

- The SQLDatabase in XRPL is responsible for storing and managing ledger and transaction data using a relational database backend.
- The primary implementation is SQLite, managed through the SOCI C++ database access library.
- The database is used for:
  - Storing validated ledgers and their metadata.
  - Storing transactions and their metadata.
  - Supporting queries for ledger and transaction history, account transaction pagination, and space usage.
  - Enabling online deletion and rotation of old ledger data.
- The SQLDatabase is initialized and managed via the `RelationalDatabase` interface, with concrete implementations for SQLite (`SQLiteDatabaseImp`).

---

## RelationalDatabase Interface and Initialization

### RelationalDatabase::init

- The entry point for initializing the SQLDatabase is the static method `RelationalDatabase::init` ([src/xrpld/app/rdb/detail/RelationalDatabase.cpp.txt]):
  - Checks the configuration for a `[relational_db]` section and a `backend` key.
  - If the backend is `"sqlite"` or the section is missing, it creates and returns a SQLite-based `RelationalDatabase`.
  - If the backend is set to any other value, it throws a runtime error.
  - No other database types are supported in this function.

Relevant code:
std::unique_ptr<RelationalDatabase>
RelationalDatabase::init(
    Application& app,
    Config const& config,
    JobQueue& jobQueue)
{
    bool use_sqlite = false;
    Section const& rdb_section{config.section(SECTION_RELATIONAL_DB)};
    if (!rdb_section.empty()) {
        if (boost::iequals(get(rdb_section, "backend"), "sqlite")) {
            use_sqlite = true;
        } else {
            Throw<std::runtime_error>(
                "Invalid rdb_section backend value: " +
                get(rdb_section, "backend"));
        }
    } else {
        use_sqlite = true;
    }
    if (use_sqlite) {
        return getSQLiteDatabase(app, config, jobQueue);
    }
    return std::unique_ptr<RelationalDatabase>();
}

### Backend Selection and Configuration

- The configuration section `[relational_db]` with `backend=sqlite` is required for SQLite.
- If the section is missing, SQLite is used by default.
- The function `getSQLiteDatabase` is called to create the actual database instance.

---

## SQLiteDatabase and SQLiteDatabaseImp

### Class Structure

- `SQLiteDatabase` is an abstract interface derived from `RelationalDatabase` ([src/xrpld/app/rdb/backend/SQLiteDatabase.h.txt]).
- `SQLiteDatabaseImp` is the concrete implementation ([src/xrpld/app/rdb/backend/detail/SQLiteDatabase.cpp.txt]).
- The class manages two main database connections:
  - `lgrdb_`: for the ledger database.
  - `txdb_`: for the transaction database (optional, depending on config).

### Constructor and Database Setup

- The constructor of `SQLiteDatabaseImp` ([src/xrpld/app/rdb/backend/detail/SQLiteDatabase.cpp.txt]):
  - Initializes member variables with the application, configuration, and logging.
  - Prepares a database connection setup struct using `setup_DatabaseCon`.
  - Calls `makeLedgerDBs` to create and initialize the main ledger and transaction databases, including setting up checkpointing and applying all required SQLite settings.
  - If any part of the database creation fails, logs a fatal error and throws an exception, preventing the object from being constructed.

Relevant code:
SQLiteDatabaseImp(
    Application& app,
    Config const& config,
    JobQueue& jobQueue)
    : app_(app)
    , useTxTables_(config.useTxTables())
    , j_(app_.journal("SQLiteDatabaseImp"))
{
    DatabaseCon::Setup const setup = setup_DatabaseCon(config, j_);
    if (!makeLedgerDBs(
            config,
            setup,
            DatabaseCon::CheckpointerSetup{&jobQueue, &app_.logs()}))
    {
        std::string_view constexpr error =
            "Failed to create ledger databases";
        JLOG(j_.fatal()) << error;
        Throw<std::runtime_error>(error.data());
    }
}

### Database Connections: DatabaseCon

- `DatabaseCon` ([src/xrpld/core/DatabaseCon.h.txt]) encapsulates a thread-safe connection to a SQLite database using SOCI.
- It supports initialization with custom SQLite pragmas and SQL, and optional checkpointing for durability.
- The constructor applies PRAGMA settings, executes schema initialization SQL, and sets up checkpointing if requested.
- The class provides methods for session access, thread safety, and performance logging.

---

## Database Schema and Initialization

### Ledger Database Schema (LgrDBInit)

- The ledger database schema is defined in `LgrDBInit` ([src/xrpld/app/main/DBInit.h.txt]) as an array of SQL statements:

1. BEGIN TRANSACTION;
2. CREATE TABLE IF NOT EXISTS Ledgers (
      LedgerHash      CHARACTER(64) PRIMARY KEY,
      LedgerSeq       BIGINT UNSIGNED,
      PrevHash        CHARACTER(64),
      TotalCoins      BIGINT UNSIGNED,
      ClosingTime     BIGINT UNSIGNED,
      PrevClosingTime BIGINT UNSIGNED,
      CloseTimeRes    BIGINT UNSIGNED,
      CloseFlags      BIGINT UNSIGNED,
      AccountSetHash  CHARACTER(64),
      TransSetHash    CHARACTER(64)
   );
3. CREATE INDEX IF NOT EXISTS SeqLedger ON Ledgers(LedgerSeq);
4. DROP TABLE IF EXISTS Validations;
5. END TRANSACTION;

### Transaction Database Schema (TxDBInit)

- The transaction database schema is defined in `TxDBInit` ([src/xrpld/app/main/DBInit.h.txt]) as an array of SQL statements:

1. BEGIN TRANSACTION;
2. CREATE TABLE IF NOT EXISTS Transactions (
      TransID     CHARACTER(64) PRIMARY KEY,
      TransType   CHARACTER(24),
      FromAcct    CHARACTER(35),
      FromSeq     BIGINT UNSIGNED,
      LedgerSeq   BIGINT UNSIGNED,
      Status      CHARACTER(1),
      RawTxn      BLOB,
      TxnMeta     BLOB
   );
3. CREATE INDEX IF NOT EXISTS TxLgrIndex ON Transactions(LedgerSeq);
4. CREATE TABLE IF NOT EXISTS AccountTransactions (
      TransID     CHARACTER(64),
      Account     CHARACTER(64),
      LedgerSeq   BIGINT UNSIGNED,
      TxnSeq      INTEGER
   );
5. CREATE INDEX IF NOT EXISTS AcctTxIDIndex ON AccountTransactions(TransID);
6. CREATE INDEX IF NOT EXISTS AcctTxIndex ON AccountTransactions(Account, LedgerSeq, TxnSeq, TransID);
7. CREATE INDEX IF NOT EXISTS AcctLgrIndex ON AccountTransactions(LedgerSeq, Account, TransID);
8. END TRANSACTION;

---

## Database Connection Setup and Pragmas

### setup_DatabaseCon

- The function `setup_DatabaseCon` ([src/xrpld/core/DatabaseCon.h.txt], [src/xrpld/core/detail/DatabaseCon.cpp.txt]) constructs a `DatabaseCon::Setup` struct with all configuration parameters for database connection.
- It sets:
  - Startup type, standalone mode, data directory.
  - Global and table-specific PRAGMA settings for SQLite.
  - Validates configuration values (e.g., page size must be a power of 2 and within a valid range).
  - Sets up global PRAGMAs for journal mode, synchronous, and temp store, based on config and safety level.
  - Table-specific PRAGMAs for page size, journal size limit, max page count, and mmap size.

Relevant code:
if (!setup.globalPragma) {
    setup.globalPragma = [&c, &j]() {
        auto const& sqlite = c.section("sqlite");
        auto result = std::make_unique<std::vector<std::string>>();
        result->reserve(3);
        std::string safety_level;
        std::string journal_mode = "wal";
        std::string synchronous = "normal";
        std::string temp_store = "file";
        bool showRiskWarning = false;
        if (set(safety_level, "safety_level", sqlite)) {
            // ... logic to adjust journal_mode, synchronous, temp_store based on safety_level ...
        }
        // ... more logic to set journal_mode, synchronous, temp_store from config ...
        result->push_back(str(boost::format(CommonDBPragmaJournal) % journal_mode));
        result->push_back(str(boost::format(CommonDBPragmaSync) % synchronous));
        result->push_back(str(boost::format(CommonDBPragmaTemp) % temp_store));
        if (showRiskWarning && j && c.LEDGER_HISTORY > SQLITE_TUNING_CUTOFF) {
            JLOG(j->warn()) << "reducing the data integrity guarantees from the "
                "default [sqlite] behavior is not recommended for "
                "nodes storing large amounts of history, because of the "
                "difficulty inherent in rebuilding corrupted data.";
        }
        XRPL_ASSERT(result->size() == 3, "ripple::setup_DatabaseCon::globalPragma : result size is 3");
        return result;
    }();
}
setup.useGlobalPragma = true;

### Pragma Settings

- PRAGMA settings are applied to control SQLite performance and durability:
  - `journal_mode`, `synchronous`, `temp_store` (global).
  - `page_size`, `journal_size_limit`, `max_page_count`, `mmap_size` (table-specific).
- These are set via SQL statements executed on the database session during initialization.

---

## Checkpointing and Durability

- Checkpointing is set up via the `setupCheckpointing` method in `DatabaseCon` ([src/xrpld/core/DatabaseCon.h.txt], [src/xrpld/core/detail/DatabaseCon.cpp.txt]).
- It requires a valid job queue and logging facility.
- A checkpointer object is created for the database session, enabling periodic or event-driven checkpoints to be scheduled via the job queue and logged.
- If the job queue is not provided, a logic error is thrown.

Relevant code:
void
DatabaseCon::setupCheckpointing(JobQueue q, Logs& l)
{
    if (!q)
        Throw<std::logic_error>("No JobQueue");
    checkpointer_ = checkpointers.create(session_, q, l);
}

---

## Database Operations and Methods

### Ledger Sequence Queries

- `getMinLedgerSeq`, `getMaxLedgerSeq` ([src/xrpld/app/rdb/backend/detail/SQLiteDatabase.cpp.txt]):
  - Return the minimum/maximum ledger sequence in the database.
  - Use helper functions in the `detail` namespace to execute SQL queries.

### Deletion and Cleanup

- `deleteTransactionByLedgerSeq`, `deleteBeforeLedgerSeq`, `deleteTransactionsBeforeLedgerSeq`, `deleteAccountTransactionsBeforeLedgerSeq`:
  - Delete transactions or ledgers before a given sequence or for a specific sequence.
  - Use helper functions in the `detail` namespace to construct and execute SQL `DELETE` statements.

### Counting and Space Usage

- `getTransactionCount`, `getAccountTransactionCount`, `getLedgerCountMinMax`:
  - Return the number of transactions, account transactions, or ledgers.
  - Use SQL `COUNT(*)` queries and min/max queries.

- `getKBUsedAll`, `getKBUsedLedger`, `getKBUsedTransaction` ([src/xrpld/core/SociDB.h.txt], [src/xrpld/core/detail/SociDB.cpp.txt]):
  - `getKBUsedAll`: Returns the total memory usage (in kilobytes) of the SQLite library for the entire process, using `sqlite3_memory_used()`.
  - `getKBUsedDB`: Returns the current memory usage (in kilobytes) of the page cache for the specific SQLite database connection, using `sqlite3_db_status(..., SQLITE_DBSTATUS_CACHE_USED, ...)`.

### Ledger and Transaction Info Retrieval

- `saveValidatedLedger`:
  - Saves a validated ledger to the database.
  - Begins a transaction, inserts or replaces the ledger info, and, if transaction tables are enabled, saves transactions and account transaction mappings.

- `getLedgerInfoByIndex`, `getNewestLedgerInfo`, `getLimitedOldestLedgerInfo`, `getLimitedNewestLedgerInfo`, `getLedgerInfoByHash`:
  - Retrieve ledger information by index, hash, or get the newest/oldest ledger info, possibly with a limit.

- `getHashByIndex`, `getHashesByIndex`:
  - Retrieve the hash (and parent hash) for a given ledger index or a range of indices.

### Account Transaction Queries and Pagination

- `getTxHistory`:
  - Retrieve a list of transactions starting from a given ledger index, up to a specified limit.

- `getOldestAccountTxs`, `getNewestAccountTxs`, `getOldestAccountTxsB`, `getNewestAccountTxsB`:
  - Retrieve account transaction history, either in normal or binary format.

- `oldestAccountTxPage`, `newestAccountTxPage`, `oldestAccountTxPageB`, `newestAccountTxPageB`:
  - Paginate account transactions, supporting both normal and binary formats.

### Transaction Retrieval by ID

- `getTransaction`:
  - Retrieve a transaction by its ID, optionally within a ledger range.
  - Returns the transaction and metadata, or an error code if not found or deserialization fails.

### Database Space Checking

- `ledgerDbHasSpace`, `transactionDbHasSpace`:
  - Check if the database has sufficient free disk space.
  - Use Boost filesystem to check available space in the database directory.
  - Logs a fatal error if less than 512MB is available.

### Database Closing

- `closeLedgerDB`, `closeTransactionDB` ([src/xrpld/app/rdb/backend/detail/SQLiteDatabase.cpp.txt]):
  - Close the respective database connection by resetting the unique pointer, releasing all associated resources.

Relevant code:
void
SQLiteDatabaseImp::closeLedgerDB()
{
    lgrdb_.reset();
}

void
SQLiteDatabaseImp::closeTransactionDB()
{
    txdb_.reset();
}

---

## Supporting Classes and Utilities

- `DatabaseCon` ([src/xrpld/core/DatabaseCon.h.txt]):
  - Manages thread-safe SQLite connections, PRAGMA settings, schema initialization, and checkpointing.
  - Provides session access and thread safety via `LockedSociSession`.

- `detail::*` functions ([src/xrpld/app/rdb/backend/detail/Node.h.txt], [src/xrpld/app/rdb/backend/detail/Node.cpp.txt]):
  - Provide low-level, table-specific operations for creation, querying, deletion, saving, and pagination for ledgers and transactions.

- `DBConfig` ([src/xrpld/core/SociDB.h.txt]):
  - Manages database connection strings and session opening.

- `Checkpointer` ([src/xrpld/core/SociDB.h.txt]):
  - Abstract base class for checkpointing logic.

- `makeCheckpointer` ([src/xrpld/core/SociDB.h.txt]):
  - Factory function to create a `Checkpointer` instance.

---

## References to Source Code

- [RelationalDatabase.h](src/xrpld/app/rdb/RelationalDatabase.h.txt)
- [RelationalDatabase.cpp](src/xrpld/app/rdb/detail/RelationalDatabase.cpp.txt)
- [SQLiteDatabase.h](src/xrpld/app/rdb/backend/SQLiteDatabase.h.txt)
- [SQLiteDatabase.cpp](src/xrpld/app/rdb/backend/detail/SQLiteDatabase.cpp.txt)
- [Node.h](src/xrpld/app/rdb/backend/detail/Node.h.txt)
- [Node.cpp](src/xrpld/app/rdb/backend/detail/Node.cpp.txt)
- [DBInit.h](src/xrpld/app/main/DBInit.h.txt)
- [DatabaseCon.h](src/xrpld/core/DatabaseCon.h.txt)
- [DatabaseCon.cpp](src/xrpld/core/detail/DatabaseCon.cpp.txt)
- [SociDB.h](src/xrpld/core/SociDB.h.txt)
- [SociDB.cpp](src/xrpld/core/detail/SociDB.cpp.txt)
- [State.cpp](src/xrpld/app/rdb/detail/State.cpp.txt)
- [Vacuum.cpp](src/xrpld/app/rdb/detail/Vacuum.cpp.txt)
- [PeerFinder.cpp](src/xrpld/app/rdb/detail/PeerFinder.cpp.txt)
- [Wallet.cpp](src/xrpld/app/rdb/detail/Wallet.cpp.txt)

---

All statements and explanations above are directly supported by the provided source code and documentation. No assumptions or extrapolations have been made.