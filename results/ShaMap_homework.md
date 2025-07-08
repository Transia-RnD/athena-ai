---

# SHAMap Comprehensive Homework Assignment

## Instructions

- For each section, answer all questions. Where code is required, use C++ (or pseudocode if specified).
- For test/debugging questions, describe your approach and provide code where appropriate.
- Be thorough in your explanations, especially for edge cases and design decisions.

---

## 1. Node Types and Structure

**a.** Describe the differences between `SHAMapInnerNode` and `SHAMapLeafNode`.  
**b.** Write C++ class definitions for `SHAMapTreeNode`, `SHAMapInnerNode`, and `SHAMapLeafNode`, including data members relevant to their function.  
**c.** What invariants must be maintained regarding node types and their positions in the tree?  
**d.** Write a function that checks if a given node pointer is a leaf or inner node, and explain how you would test this function.

---

## 2. Construction, Mutability, and Snapshots

**a.** Explain the difference between mutable and immutable `SHAMap`s.  
**b.** Write code to construct a mutable `SHAMap` and an immutable `SHAMap`.  
**c.** Implement the `snapShot` function, ensuring correct node sharing and immutability guarantees.  
**d.** Describe an edge case where improper snapshotting could lead to data corruption. How would you test for this?

---

## 3. Copy-on-Write and Node Sharing

**a.** Explain how copy-on-write (COW) is implemented in `SHAMap` using `shared_ptr`.  
**b.** Write code to perform a COW operation on a node with a non-zero sequence number.  
**c.** Describe a scenario where node sharing could lead to a bug if not handled correctly.  
**d.** Write a test that ensures nodes are not accidentally shared between two independent `SHAMap` instances after a modification.

---

## 4. Node Identification and Navigation

**a.** Explain how keys are used to navigate the radix trie structure of `SHAMap`.  
**b.** Write a function that, given a key, returns the path from the root to the corresponding leaf node.  
**c.** What edge cases must be considered when navigating the tree (e.g., missing nodes, invalid keys)?  
**d.** Write tests for your navigation function, including edge cases.

---

## 5. Traversal and Iteration (Including Parallel)

**a.** Write a function to traverse all leaf nodes in a `SHAMap` (depth-first).  
**b.** Modify your function to support parallel traversal, ensuring thread safety.  
**c.** What are the risks of parallel traversal in a mutable `SHAMap`?  
**d.** Write a test that detects race conditions or data corruption during parallel traversal.

---

## 6. Synchronization and Missing Node Detection

**a.** Describe how missing nodes are detected during synchronization between two `SHAMap`s.  
**b.** Write code to compare two `SHAMap`s and return a list of missing node hashes.  
**c.** What edge cases could cause false positives/negatives in missing node detection?  
**d.** Write a test to verify your missing node detection logic.

---

## 7. Node Addition and Canonicalization

**a.** Write code to add a new leaf node to a `SHAMap`, ensuring canonical placement.  
**b.** How do you handle the case where a node with the same key already exists?  
**c.** Write a function to canonicalize a node (i.e., ensure it is in the correct position and form).  
**d.** Test your addition and canonicalization logic with duplicate and conflicting keys.

---

## 8. Serialization and Proofs

**a.** Explain how a `SHAMap` can be serialized for storage or transmission.  
**b.** Write code to serialize and deserialize a `SHAMap` node.  
**c.** Implement a function to generate a Merkle proof for a given leaf node.  
**d.** Write tests to verify serialization/deserialization and proof correctness, including tampered data.

---

## 9. State Management

**a.** Describe how state changes are managed in a `SHAMap` (e.g., transaction application).  
**b.** Write code to apply a batch of state changes to a `SHAMap`.  
**c.** What edge cases arise when applying conflicting or invalid state changes?  
**d.** Write tests to ensure state changes are applied atomically and correctly.

---

## 10. Caching and Storage

**a.** Explain the role of caching in `SHAMap` performance.  
**b.** Write code to implement a simple cache for recently accessed nodes.  
**c.** How would you handle cache eviction and consistency?  
**d.** Write tests to ensure cache correctness under concurrent access.

---

## 11. Thread Safety

**a.** Identify which operations on `SHAMap` require thread safety.  
**b.** Write code to make node addition and traversal thread-safe.  
**c.** What are the risks of deadlock or race conditions in your implementation?  
**d.** Write a test that attempts to trigger a race condition or deadlock.

---

## 12. Supporting Classes and Utilities

**a.** List and describe at least three supporting classes/utilities used by `SHAMap` (e.g., hash functions, key encoders, database interfaces).  
**b.** Write code for a utility function that computes the hash of a node’s contents.  
**c.** How would you test the correctness and performance of your utility functions?  
**d.** Write a test suite for your utility functions, including edge cases (e.g., empty data, very large data).

---

# Submission

- Submit your code files and a document with your answers and explanations.
- Include all test cases and results.
- Be prepared to discuss your design decisions and testing strategies.

---

**End of Assignment**