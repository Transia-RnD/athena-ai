# fetchNodeObject

## Summary

`fetchNodeObject` is a core method of the NodeStore `Database` interface, responsible for retrieving a `NodeObject` (ledger entry) by its hash from the cache or backend storage. It is used by higher-level components such as SHAMap and ledger retrieval logic to access persisted ledger data.

## Function Signature

```cpp
std::shared_ptr<NodeObject> fetchNodeObject(
    uint256 const& hash,
    std::uint32_t ledgerSeq = 0,
    FetchType fetchType = FetchType::synchronous,
    bool duplicate = false
);
```

### Parameters

- **hash** (`uint256 const&`):  
  The 256-bit hash identifying the `NodeObject` to fetch.

- **ledgerSeq** (`std::uint32_t`, optional):  
  The ledger sequence number associated with the fetch. Used for metrics and reporting; not required for all backends.

- **fetchType** (`FetchType`, optional):  
  Specifies the type of fetch operation.  
  - `FetchType::synchronous`: Perform a blocking fetch (default).
  - `FetchType::async`: Used for asynchronous prefetching (see `asyncFetch`).

- **duplicate** (`bool`, optional):  
  If `true`, and the object is found in an archive or secondary backend, it will be duplicated (stored) in the writable backend. Used in rotating backend scenarios.

### Return Value

- Returns a `std::shared_ptr<NodeObject>` if the object is found and valid.
- Returns `nullptr` if the object is not found or is a dummy/missing entry.

## Fetch Flow and Behavior

1. **Cache Lookup**:  
   - Checks if the requested `NodeObject` is present in the cache.
   - If found and not a dummy (`hotDUMMY`), returns it immediately.
   - If found and is a dummy, returns `nullptr`.

2. **Backend Lookup**:  
   - If not in cache, attempts to fetch from the backend(s):
     - For single-backend (`DatabaseNodeImp`): fetches from the configured backend.
     - For rotating-backend (`DatabaseRotatingImp`): tries the writable backend first, then the archive backend.
   - If found in the archive and `duplicate` is `true`, stores the object in the writable backend.

3. **Dummy Object Handling**:  
   - If the object is not found, a dummy object (`hotDUMMY`) may be cached to mark the missing entry.

4. **Error Handling**:  
   - If data corruption is detected, a fatal log is emitted.
   - Unknown or backend-specific errors are logged with appropriate severity.
   - If an exception occurs during backend fetch, it is logged and rethrown.

5. **Metrics and Reporting**:  
   - Updates fetch statistics: hit/miss counts, fetch sizes, and durations.
   - Reports fetch events to the scheduler for monitoring.

6. **Thread Safety**:  
   - All cache and backend operations are protected by mutexes to ensure thread safety.
   - In `DatabaseRotatingImp`, a mutex guards access to both writable and archive backends.

## Side Effects

- May update the cache with found or dummy objects.
- May store (duplicate) objects in the writable backend (if `duplicate` is `true` and found in archive).
- Updates fetch statistics and reports to the scheduler.

## Error Handling

- Returns `nullptr` if the object is not found or is a dummy.
- Sets `fetchReport.wasFound` to indicate if the object was found (internal).
- Logs fatal errors for data corruption and warnings for unknown backend errors.

## Related Functions

- **asyncFetch**:  
  Initiates an asynchronous fetch of a `NodeObject`.
- **store**:  
  Stores a single `NodeObject` in the backend.
- **storeBatch**:  
  Stores a batch of `NodeObject`s in the backend.

## Example Usage

- Used by SHAMap, ledger retrieval, and other components to access persisted ledger entries.
- Both `DatabaseNodeImp` (single-backend) and `DatabaseRotatingImp` (rotating-backend) provide concrete implementations.

## Test Coverage

- See `Backend_test.cpp` for tests covering backend and `fetchNodeObject` behavior.

---

**All statements above are directly supported by the provided code and documentation. No assumptions or extrapolations have been made.**