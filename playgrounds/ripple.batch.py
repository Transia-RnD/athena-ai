#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled", "v1")
# indexer.build_from_dirs(
#     path,
#     ["include", "src/libxrpl", "src/test", "src/xrpld"],
#     False,
# )

from athenah_ai.client import AthenahClient

prompt: str = """
```
XRPL Development Curriculum
Goals and Objectives
Understand and manage Technical Debt
Implement Mutex strategies
Convert Multi-Threaded code into a Single-Threaded Application
Learn to write and evaluate XLS amendments
Master Testing and Debugging techniques
General Overview of Blockchain
What problem are we solving?
Software Lifecycle
Working with Amendments
Feature Amendments (XLS Template) (Phase 1)
Understanding the architecture of the system
Evaluating architectural compatibility
Configuration
Standalone implementation
Binary Codec
Transactors
Debugging
Versioning
Testing
Fix Amendments (XLS Template) (Phase 1)
Understanding the architecture of the system
Evaluating architectural compatibility
Versioning
Signing & Verifying with Quantum Signatures (Phase 2)
CMake integration
Signing & Verification processes
Database Management
LMDB vs Memory DB options
LedgerHead Database
Transaction Database
Technical Debt Management
Using libxrpl to build a module to update the server
Priority: 10
Core Components
Configuration
Standalone (Submit new XLS transaction)
Consensus
Binary Codec
Signing & Verifying
Versioning
Transactors
Overlay (Pass messages back and forth)
LedgerHead Database
Transaction Database
Debugging
Testing
Technical Debt (Removing and Updating)
Server (websockets & rpc)
Best Practices
Candidate Evaluation
Contributors
Nic Bugalos
Richard Holland
Scott Schumer
Howard Hinnant
Tequ
Nic Xahaud


```
We are building a 2 week 12 day course for new XRPL developers. We will focus on the ripple(d) repo and cpp. We need to build an outline for the course. Go through each file and folder and organize the course into 12 days. Each day should have a theme and a list of files to go through. The course should be for new developers who are not familiar with the XRPL or cpp. The course should be hands on and include exercises and examples. The course should be fun and engaging. The course should be for developers who are interested in building on the XRPL.

Day 1 lets focus on the XRPL Architecture. List all the files and folders we should review?

"""
client = AthenahClient("id", "dist", "rippled")
response = client.promptv1(prompt)
print(response)
