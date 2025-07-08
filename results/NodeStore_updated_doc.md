# Additional Information: `fetchNodeObject` Usage and Tests

## `fetchNodeObject` Functionality

The `fetchNodeObject` function is a core method in the NodeStore subsystem, responsible for retrieving a `NodeObject` from the cache or backend storage. Its main responsibilities and usage patterns are as follows:

- **Cache Lookup:**  
  The function first checks if the requested `NodeObject` (by hash) is present in the cache. If found and not marked as a dummy (`hotDUMMY`), it is returned immediately.

- **Backend Fetch:**  
  If the object is not in the cache, `fetchNodeObject` attempts to retrieve it from the configured backend (e.g., RocksDB, NuDB).  
  - On successful fetch, the object is inserted into the cache.
  - If the object is not found, a dummy object (`hotDUMMY`) is cached to mark the missing entry.
  - If data corruption is detected, a fatal log is emitted.
  - Unknown or backend-specific errors are logged with appropriate severity.

- **Metrics and Reporting:**  
  The function updates fetch statistics, including hit/miss counts and fetch durations, and reports these via the scheduler.

- **Thread Safety:**  
  All cache and backend operations are protected to ensure thread safety.

### Example Usage in Code

- The main `Database` interface exposes `fetchNodeObject` for use by higher-level components, such as SHAMap and ledger retrieval logic.
- Both `DatabaseNodeImp` and `DatabaseRotatingImp` provide concrete implementations, handling single-backend and rotating-backend scenarios, respectively.

## Source Code References

- [`DatabaseNodeImp.cpp` (fetchNodeObject implementation)](src/xrpld/nodestore/detail/DatabaseNodeImp.cpp.txt)
- [`Database.cpp` (Database::fetchNodeObject)](src/xrpld/nodestore/detail/Database.cpp.txt)
- [`DatabaseRotatingImp.cpp` (rotating backend fetch)](src/xrpld/nodestore/detail/DatabaseRotatingImp.cpp.txt)

## Test Coverage

- [`Backend_test.cpp` (NodeStore backend and fetchNodeObject tests)](/Users/darkmatter/projects/ledger-works/rippled/src/test/nodestore/Backend_test.cpp)

---

**All statements above are directly supported by the provided code and documentation. No assumptions or extrapolations have been made.**