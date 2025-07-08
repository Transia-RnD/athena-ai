# XRPL NodeStore Functionality: Comprehensive Lesson Plan

This document provides a detailed, code-driven breakdown of the XRPL NodeStore subsystem, focusing on every aspect of its functionality, architecture, and component interactions. All statements and explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [NodeStore Overview](#nodestore-overview)
- [NodeObject: Structure and Creation](#nodeobject-structure-and-creation)
- [Backend Interface and Implementations](#backend-interface-and-implementations)
  - [Backend::store](#backendstore)
  - [Backend::fetch](#backendfetch)
  - [Backend Implementations](#backend-implementations)
- [Database Abstraction](#database-abstraction)
  - [Database::fetchNodeObject](#databasefetchnodeobject)
  - [Database::importInternal](#databaseimportinternal)
- [DatabaseNodeImp: Standard NodeStore Database](#databasenodeimp-standard-nodestore-database)
  - [DatabaseNodeImp::store](#databasenodeimpstore)
  - [DatabaseNodeImp::fetchNodeObject](#databasenodeimpfetchnodeobject)
  - [DatabaseNodeImp::fetchBatch](#databasenodeimpfetchbatch)
- [DatabaseRotatingImp: Rotating NodeStore Database](#databaserotatingimp-rotating-nodestore-database)
- [Manager and Factory: Backend/Database Creation](#manager-and-factory-backenddatabase-creation)
- [NodeObject Encoding/Decoding](#nodeobject-encodingdecoding)
  - [EncodedBlob](#encodedblob)
  - [DecodedBlob](#decodedblob)
- [NodeStore Data Format](#nodestore-data-format)
- [Cache Layer: TaggedCache](#cache-layer-taggedcache)
- [NodeStore in Application Context](#nodestore-in-application-context)
- [References](#references)

---

## NodeStore Overview

The NodeStore subsystem provides a persistent storage interface for `NodeObject`s, which are the primary representation of ledger entries in XRPL. All ledger entries are stored as `NodeObject`s, which must be persisted between launches. If a `NodeObject` is not in memory, it is retrieved from the database.

Source: [/src/xrpld/nodestore/README.md]

---

## NodeObject: Structure and Creation

A `NodeObject` encapsulates:

- `mType`: An enumeration (`NodeObjectType`) indicating the object type:
  - `hotLEDGER`: Ledger header
  - `hotTRANSACTION`: Signed transaction
  - `hotACCOUNT_NODE`: Node in the account state tree
  - `hotTRANSACTION_NODE`: Node in the transaction tree
  - `hotDUMMY`: Dummy marker
- `mHash`: 256-bit hash of the blob (unique identifier)
- `mData`: Variable-length blob containing the serialized payload

Creation is controlled via a private constructor and a static factory method:

Source: [/src/xrpld/nodestore/NodeObject.h.txt], [/src/xrpld/nodestore/detail/NodeObject.cpp.txt]

Example:
static std::shared_ptr<NodeObject> createObject(
    NodeObjectType type,
    Blob&& data,
    uint256 const& hash);

This ensures all `NodeObject`s are heap-allocated and managed by `std::shared_ptr`.

---

## Backend Interface and Implementations

### Backend::store

The `Backend` class is an abstract interface for all storage backends. The `store` method is pure virtual and must be implemented by all backends.

Source: [/src/xrpld/nodestore/Backend.h.txt]

virtual void store(std::shared_ptr<NodeObject> const& object) = 0;

- Stores a single `NodeObject` in the backend.

#### Implementations

- **MemoryBackend**: Inserts into an in-memory map, keyed by hash, with thread safety.
- **NuDBBackend**: Encodes and compresses the object, then inserts into NuDB, reporting write metrics.
- **RocksDBBackend**: Delegates to a batch writer for RocksDB.
- **NullBackend**: No operation (used for testing or when no storage is required).

Source: 
- [/src/xrpld/nodestore/backend/MemoryFactory.cpp.txt]
- [/src/xrpld/nodestore/backend/NuDBFactory.cpp.txt]
- [/src/xrpld/nodestore/backend/RocksDBFactory.cpp.txt]
- [/src/xrpld/nodestore/backend/NullFactory.cpp.txt]

### Backend::fetch

Source: [/src/xrpld/nodestore/Backend.h.txt]

virtual Status fetch(void const* key, std::shared_ptr<NodeObject>* pObject) = 0;

- Retrieves a `NodeObject` by key (hash).
- Sets `*pObject` to the result or leaves it null if not found.
- Returns a `Status` enum: `ok`, `notFound`, `dataCorrupt`, etc.

Implementations are backend-specific and handle deserialization, error handling, and status codes.

---

## Backend Implementations

Each backend implements the `Backend` interface:

- **MemoryBackend**: In-memory map, thread-safe.
- **NuDBBackend**: Persistent key-value store using NuDB, with compression.
- **RocksDBBackend**: Persistent key-value store using RocksDB, with batch writing.
- **NullBackend**: No-op, for testing or disabled storage.

See:
- [/src/xrpld/nodestore/backend/MemoryFactory.cpp.txt]
- [/src/xrpld/nodestore/backend/NuDBFactory.cpp.txt]
- [/src/xrpld/nodestore/backend/RocksDBFactory.cpp.txt]
- [/src/xrpld/nodestore/backend/NullFactory.cpp.txt]

---

## Database Abstraction

The `Database` class is an abstract interface for managing storage and retrieval of `NodeObject`s, providing methods for:

- Storing objects
- Fetching objects (sync/async)
- Importing data from another database
- Iterating over all objects
- Managing statistics and metrics

Source: [/src/xrpld/nodestore/Database.h.txt]

### Database::fetchNodeObject

Source: [/src/xrpld/nodestore/detail/Database.cpp.txt]

std::shared_ptr<NodeObject>
Database::fetchNodeObject(
    uint256 const& hash,
    std::uint32_t ledgerSeq,
    FetchType fetchType,
    bool duplicate)

- Prepares a `FetchReport` and starts a timer.
- Calls the backend-specific `fetchNodeObject` (virtual).
- Measures duration, updates statistics, and notifies the scheduler.
- Returns the found object or null.

### Database::importInternal

Source: [/src/xrpld/nodestore/detail/Database.cpp.txt]

void Database::importInternal(Backend& dstBackend, Database& srcDB)

- Iterates over all `NodeObject`s in `srcDB` using `for_each`.
- Batches objects (size 256) and writes them to `dstBackend` using `storeBatch`.
- Updates statistics and handles exceptions.

---

## DatabaseNodeImp: Standard NodeStore Database

`DatabaseNodeImp` is the standard implementation of `Database`, using a single backend and an optional cache.

Source: [/src/xrpld/nodestore/detail/DatabaseNodeImp.h.txt], [/src/xrpld/nodestore/detail/DatabaseNodeImp.cpp.txt]

### DatabaseNodeImp::store

void DatabaseNodeImp::store(
    NodeObjectType type,
    Blob&& data,
    uint256 const& hash,
    std::uint32_t)

- Updates store statistics.
- Creates a `NodeObject` via `NodeObject::createObject`.
- Stores the object in the backend.
- If a cache is present, canonicalizes the object in the cache (unless it's a dummy).

### DatabaseNodeImp::fetchNodeObject

std::shared_ptr<NodeObject>
DatabaseNodeImp::fetchNodeObject(
    uint256 const& hash,
    std::uint32_t,
    FetchReport& fetchReport,
    bool duplicate)

- Attempts to fetch from cache.
- If not found, fetches from backend and handles status:
  - If found, caches the object.
  - If not found, caches a dummy marker.
  - If data is corrupt, logs a fatal error.
- Updates the fetch report and returns the object or null.

### DatabaseNodeImp::fetchBatch

std::vector<std::shared_ptr<NodeObject>>
DatabaseNodeImp::fetchBatch(std::vector<uint256> const& hashes)

- Checks cache for each hash.
- Collects cache misses and fetches them in batch from the backend.
- Updates cache and logs errors for missing objects.
- Updates fetch metrics and returns the results.

---

## DatabaseRotatingImp: Rotating NodeStore Database

`DatabaseRotatingImp` manages two backends: a writable backend for current data and an archive backend for older data. It supports rotation between them.

Source: [/src/xrpld/nodestore/detail/DatabaseRotatingImp.h.txt], [/src/xrpld/nodestore/detail/DatabaseRotatingImp.cpp.txt]

Key methods:

- `rotate`: Switches the writable backend and moves the old one to archive.
- `store`: Stores objects in the writable backend.
- `fetchNodeObject`: Tries the writable backend first, then the archive. Optionally duplicates found objects back to the writable backend.
- Thread safety is ensured via mutexes.

---

## Manager and Factory: Backend/Database Creation

The `Manager` and `Factory` classes manage the registration and creation of backends and databases.

Source: [/src/xrpld/nodestore/Manager.h.txt], [/src/xrpld/nodestore/Factory.h.txt], [/src/xrpld/nodestore/detail/ManagerImp.cpp.txt]

- `ManagerImp` is a singleton managing backend factories.
- `make_Backend`: Looks up the backend type in the config, finds the factory, and creates a backend instance.
- `make_Database`: Creates a backend, opens it, and constructs a `DatabaseNodeImp` (or `DatabaseRotatingImp` if rotation is enabled).

---

## NodeObject Encoding/Decoding

### EncodedBlob

Source: [/src/xrpld/nodestore/detail/EncodedBlob.h.txt]

- Encodes a `NodeObject` for storage.
- Format:
  - Bytes 0-7: unused (set to zero)
  - Byte 8: type (`NodeObjectType`)
  - Bytes 9...end: data blob
- Uses a stack-allocated buffer for small objects, heap allocation for large ones.
- Provides accessors for key, size, and data.

### DecodedBlob

Source: [/src/xrpld/nodestore/detail/DecodedBlob.h.txt], [/src/xrpld/nodestore/detail/DecodedBlob.cpp.txt]

- Decodes a binary blob from storage into a `NodeObject`.
- Parses the type and data from the value blob.
- Only recognized types (`hotLEDGER`, `hotACCOUNT_NODE`, `hotTRANSACTION_NODE`, `hotUNKNOWN`) are considered valid.
- `createObject` constructs a `NodeObject` from the decoded data.

---

## NodeStore Data Format

Source: [/src/xrpld/nodestore/README.md]

| Byte   | Field | Description                  |
|--------|-------|-----------------------------|
| 0...7  | unused|                             |
| 8      | type  | NodeObjectType enumeration  |
| 9...end| data  | body of the object data     |

- The key (hash) is stored separately and used as the lookup key in the backend.

---

## Cache Layer: TaggedCache

`DatabaseNodeImp` and other database implementations may use a `TaggedCache` to cache recently accessed `NodeObject`s.

- Configurable via `cache_size` and `cache_age` in the config section.
- Caches objects for fast retrieval and reduces backend load.
- Dummy objects (`hotDUMMY`) are used to mark missing entries.

Source: [/src/xrpld/nodestore/detail/DatabaseNodeImp.h.txt]

---

## NodeStore in Application Context

- The `SHAMapStore` and `SHAMapStoreImp` classes manage the lifecycle of the NodeStore, including online deletion, rotation, and cache management.
- The `Application` class initializes the NodeStore and may import data from another database at startup.
- The `NodeFamily` class provides access to the NodeStore database and caches for SHAMap operations.

Source: 
- [/src/xrpld/app/misc/SHAMapStore.h.txt]
- [/src/xrpld/app/misc/SHAMapStoreImp.h.txt]
- [/src/xrpld/app/misc/SHAMapStoreImp.cpp.txt]
- [/src/xrpld/app/main/Application.cpp.txt]
- [/src/xrpld/shamap/NodeFamily.h.txt]

---

## References

- [NodeObject.h](src/xrpld/nodestore/NodeObject.h.txt)
- [NodeObject.cpp](src/xrpld/nodestore/detail/NodeObject.cpp.txt)
- [Backend.h](src/xrpld/nodestore/Backend.h.txt)
- [Database.h](src/xrpld/nodestore/Database.h.txt)
- [DatabaseNodeImp.h](src/xrpld/nodestore/detail/DatabaseNodeImp.h.txt)
- [DatabaseNodeImp.cpp](src/xrpld/nodestore/detail/DatabaseNodeImp.cpp.txt)
- [DatabaseRotatingImp.h](src/xrpld/nodestore/detail/DatabaseRotatingImp.h.txt)
- [DatabaseRotatingImp.cpp](src/xrpld/nodestore/detail/DatabaseRotatingImp.cpp.txt)
- [Manager.h](src/xrpld/nodestore/Manager.h.txt)
- [Factory.h](src/xrpld/nodestore/Factory.h.txt)
- [EncodedBlob.h](src/xrpld/nodestore/detail/EncodedBlob.h.txt)
- [DecodedBlob.h](src/xrpld/nodestore/detail/DecodedBlob.h.txt)
- [DecodedBlob.cpp](src/xrpld/nodestore/detail/DecodedBlob.cpp.txt)
- [README.md](src/xrpld/nodestore/README.md)

---

**All statements above are directly supported by the provided code and context. No assumptions or extrapolations have been made.**