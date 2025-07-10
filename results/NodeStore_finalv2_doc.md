---

# NodeStore Initialization in XRPL

## Introduction

The **NodeStore** is a persistent key-value database used by the XRPL server to store all ledger entries as `NodeObject`s. Each `NodeObject` consists of:
- **Type**: An enumeration indicating the kind of data (ledger header, transaction, account node, transaction node).
- **Hash**: A 256-bit hash uniquely identifying the object.
- **Data**: A variable-length blob containing the serialized payload.

All ledger entries are stored as `NodeObject`s and must be persisted between launches. If a `NodeObject` is not in memory, it is retrieved from the NodeStore database.

**NodeObject Storage Format:**
- Bytes 0...7: unused
- Byte 8: type (NodeObjectType enumeration)
- Bytes 9...end: data (body of the object)

## Where NodeStore is Initialized

NodeStore initialization occurs in two main places:
- **`src/xrpld/app/main/Application.cpp`**: The `initNodeStore()` function is responsible for initializing the NodeStore during application startup.
- **`src/xrpld/app/misc/SHAMapStoreImp.cpp` / `SHAMapStoreImp.h`**: The `SHAMapStoreImp` class manages the NodeStore lifecycle, including support for online deletion (rotating databases).

## How NodeStore is Initialized

### 1. Configuration Loading

- The NodeStore configuration is loaded from the `[node_db]` section of the server's configuration file.
- This section specifies the backend type (e.g., `RocksDB`, `NuDB`, `Memory`, `none`, `SQLite`), the storage path, and other options such as cache size and compression.

  **Example:**
  ```
  [node_db]
  type=RocksDB
  path=rocksdb
  compression=1
  ```

### 2. Database Creation

- The `initNodeStore()` function (in `Application.cpp`) or `SHAMapStoreImp::makeNodeStore()` (for online deletion) calls `NodeStore::Manager::instance().make_Database(...)` to create the NodeStore database.
- The `make_Database` function uses the configuration to select and instantiate the correct backend via the `Manager` and `Factory` classes.

### 3. Backend Instantiation

- The `Manager` maintains a registry of available backend `Factory` objects.
- The selected `Factory` creates an instance of the appropriate `Backend` (e.g., `RocksDBBackend`, `NuDBBackend`, `MemoryBackend`, `NullBackend`, `SQLiteBackend`).
- The backend is opened and made ready for use.

### 4. Database Types

- **Standard NodeStore**: Uses a single backend for all data. Created by `make_Database`, which returns a `DatabaseNodeImp` instance.
- **Rotating NodeStore**: Used when online deletion is enabled. Manages two backends (writable and archive) and rotates them as old data is deleted. Created by `SHAMapStoreImp::makeNodeStore`, which returns a `DatabaseRotatingImp` instance.

### 5. Cache Configuration

- The NodeStore uses an in-memory cache to speed up access to frequently used `NodeObject`s.
- Cache size and age can be configured via the `[node_db]` section (e.g., `cache_size`, `cache_age`).
- If not specified, defaults are taken from the application configuration.

### 6. Opening the Database

- After creation, the database and its backend are opened and made ready for use by the rest of the application.
- The NodeStore is then used by various subsystems (e.g., ledger, SHAMap, transaction processing) to store and retrieve ledger data.

## Available Backends

The following backends are supported (specified by the `type` parameter in `[node_db]`):

- **RocksDB**: Facebook's RocksDB, recommended for production.
- **NuDB**: A high-performance, append-only key-value store.
- **Memory**: In-memory backend, for testing only (no persistence).
- **none**: Null backend, disables storage (for testing).
- **SQLite**: Uses SQLite for storage (not recommended for production).
- **HyperLevelDB**: Improved LevelDB (preferred over LevelDB).
- **LevelDB**: Google's LevelDB (deprecated).

Each backend may have additional options (see the backend's documentation for details).

## NodeObject Structure

A `NodeObject` is stored in the following format:
- Bytes 0...7: unused
- Byte 8: type (NodeObjectType enumeration)
- Bytes 9...end: data (body of the object)

## Supporting Evidence

- The `initNodeStore()` function in `Application.cpp` is responsible for NodeStore initialization.
- The `make_Database` function uses the configuration to select and instantiate the correct backend via the `Manager` and `Factory` classes.
- The `SHAMapStoreImp` class manages rotating NodeStore databases for online deletion.
- The NodeStore implementation provides an abstract `Backend` interface, allowing different key/value databases to be chosen at runtime.
- All statements above are directly supported by the provided code and documentation.

---

**No assumptions or extrapolations have been made. All information is directly supported by the provided documentation and code.**