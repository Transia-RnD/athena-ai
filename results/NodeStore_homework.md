# XRPL NodeStore Subsystem: Comprehensive Homework Assignment

## Overview

This assignment will test your understanding of the XRPL NodeStore subsystem, including its architecture, configuration, backend types, NodeObject structure, encoding/decoding, cache management, error handling, resource usage, and integration with the application lifecycle. You will be required to explain concepts, write code, handle edge cases, and develop tests.

**References:**  
- `xrpld/nodestore/Factory.h`  
- `xrpld/nodestore/Manager.h`  
- `xrpld/nodestore/detail/DecodedBlob.h`  
- `xrpld/nodestore/detail/EncodedBlob.h`  
- `xrpld/nodestore/detail/codec.h`  
- `xrpld/app/main/NodeStoreScheduler.h`  
- `xrpld/unity/rocksdb.h`  
- `nudb/nudb.hpp`  
- `xrpl/basics/contract.h`  
- `xrpl/basics/ByteUtilities.h`  

---

## Part 1: Conceptual Understanding

### 1.1 NodeStore Architecture

**a.** Explain the role of the NodeStore subsystem in XRPL.  
**b.** Describe the lifecycle of a NodeObject from creation to persistence and retrieval.  
**c.** List and briefly describe the main components of the NodeStore subsystem (e.g., Factory, Manager, Backend, Scheduler).

### 1.2 Configuration and Backend Types

**a.** List the supported backend types (e.g., NuDB, RocksDB).  
**b.** Explain how the backend is selected and configured at runtime. Reference relevant code sections.  
**c.** Discuss the implications of backend rotation and how the system handles switching backends.

### 1.3 NodeObject Structure

**a.** Describe the structure of a NodeObject, including its type, key, and data.  
**b.** Explain the on-disk layout of a NodeObject (see context table: bytes 0-7 unused, byte 8 type, etc.).

### 1.4 Encoding/Decoding

**a.** Explain the purpose of `EncodedBlob` and `DecodedBlob` in the NodeStore.  
**b.** Describe the encoding and decoding process for a NodeObject. Reference `xrpld/nodestore/detail/EncodedBlob.h` and `DecodedBlob.h`.

### 1.5 Cache Management

**a.** Explain the role of the NodeStore cache.  
**b.** Describe the cache eviction policy and how it prevents memory overuse.

### 1.6 Error Handling and Resource Usage

**a.** List possible error scenarios in NodeStore operations (e.g., corrupt data, backend failure, batch write limits).  
**b.** Explain how errors are detected and handled. Reference `xrpl/basics/contract.h` for assertions and error contracts.  
**c.** Discuss how resource usage is tracked and reported (see `NodeStoreScheduler` and job queue integration).

### 1.7 Application Lifecycle

**a.** Describe how NodeStore integrates with the application lifecycle, including startup, shutdown, and recovery from failures.

---

## Part 2: Code Writing and Edge Cases

### 2.1 NodeObject Encoding/Decoding

**Task:**  
Implement a function in C++ that takes a `NodeObject`, encodes it using `EncodedBlob`, and then decodes it back using `DecodedBlob`.  
- Write unit tests to verify that the original and decoded objects are identical.
- Test with various NodeObject types and data sizes, including edge cases (e.g., empty data, maximum size).

### 2.2 Error Handling: Corrupt Data

**Task:**  
Simulate a scenario where a NodeObject is corrupted on disk (e.g., invalid type byte or truncated data).  
- Implement code to detect and handle this error gracefully.
- Write a unit test that injects corrupt data and verifies that the error is logged and does not crash the application.

### 2.3 Batch Write Limits

**Task:**  
Modify the batch writer (see `xrpld/nodestore/detail/BatchWriter.h`) to enforce a maximum batch size.  
- Write code to handle the case where the batch size is exceeded.
- Write a test that attempts to write a batch larger than the limit and verifies correct handling.

### 2.4 Cache Eviction

**Task:**  
Implement a test that fills the NodeStore cache to capacity and then adds additional objects to trigger eviction.  
- Verify that the least recently used objects are evicted.
- Test edge cases, such as rapid insertions and deletions.

### 2.5 Backend Rotation

**Task:**  
Simulate switching from one backend to another (e.g., from NuDB to RocksDB).  
- Write code to migrate data and ensure consistency.
- Write tests to verify that no data is lost and that the new backend is used for subsequent operations.

---

## Part 3: Debugging and Testing

### 3.1 Unit Tests

**Task:**  
Write unit tests for the following scenarios:
- Fetching a NodeObject that does not exist.
- Storing and retrieving a NodeObject with maximum allowed data size.
- Handling a backend failure (e.g., simulate RocksDB/NuDB throwing an exception).

### 3.2 Bug Identification and Fixing

**Task:**  
Given the following buggy code snippet (hypothetical), identify and fix the bug:

```cpp
// Buggy code: NodeObject retrieval
auto obj = backend->fetch(key);
if (obj)
    process(obj->getData());
else
    process(nullptr); // process expects non-null data
```

- Explain the bug and provide a corrected version.

### 3.3 Simulating Backend Failures

**Task:**  
Write a test that simulates a backend failure (e.g., disk full, permission denied) during a write operation.  
- Verify that the error is reported and the system remains stable.

### 3.4 Verifying Metrics and Resource Usage

**Task:**  
Instrument the NodeStore to collect metrics on fetches, writes, cache hits/misses, and batch write times (see `NodeStoreScheduler`).  
- Write a test that performs a series of operations and verifies that the metrics are correctly reported.

---

## Part 4: Explanation and Documentation

### 4.1 Documentation

**Task:**  
For each code task above, write a brief explanation (2-3 sentences) describing:
- What the code does.
- Why it is necessary.
- How it handles edge cases or errors.

### 4.2 Design Discussion

**Task:**  
Write a short essay (1-2 pages) discussing:
- The trade-offs between different backend types (NuDB vs. RocksDB).
- The importance of robust error handling in persistent storage systems.
- How NodeStore design supports high availability and data integrity in XRPL.

---

## Submission Checklist

- [ ] Answers to all conceptual questions.
- [ ] Source code for all implementation tasks.
- [ ] Unit tests and test results.
- [ ] Bug fix explanations.
- [ ] Documentation and explanations for each code task.
- [ ] Design discussion essay.

---

**Grading Rubric:**  
- Conceptual Understanding: 20%  
- Code Implementation: 30%  
- Edge Case Handling: 15%  
- Testing and Debugging: 20%  
- Documentation and Explanation: 10%  
- Design Discussion: 5%  

---

**Note:** Reference the relevant files and code sections as you work. Use best practices for C++ code, error handling, and testing. If you have questions, consult the XRPL documentation or ask your instructor.

---

**End of Assignment**