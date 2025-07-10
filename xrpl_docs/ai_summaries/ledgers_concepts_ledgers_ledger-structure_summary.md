# AI Summary: concepts/ledgers/ledger-structure.md

**Source:** https://xrpl.org/docs/concepts/ledgers/ledger-structure
**Category:** ledgers
**Generated:** 2025-07-10 16:15:57

---

# XRPL Ledger Structure Documentation Summary

## Overview
The XRP Ledger is a blockchain where each block is called a "ledger version" that contains state data, a transaction set, and a header with metadata. The consensus protocol builds new validated ledger versions by having validators agree on transactions to apply to the previous ledger, creating an immutable chain of transaction history.

## Key Concepts and Terminology
• **Ledger Version/Ledger** - Individual blocks in the XRPL blockchain
• **State Data** - Snapshot of all accounts, balances, and settings stored as ledger entries in a tree format
• **Transaction Set** - Group of transactions applied in canonical order to create state changes
• **Ledger Header** - Fixed-size summary containing metadata about the ledger version
• **Ledger Index** - Sequential position number identifying ledger's place in the chain
• **Ledger Hash** - Unique 256-bit identifier reflecting the ledger's exact contents
• **Validated Ledger** - Ledger version confirmed by consensus of validators as immutable

## Main Technical Details
The ledger structure consists of three main components: state data (stored as a tree of ledger entries with unique 256-bit IDs), transaction sets (containing both transaction instructions and metadata), and headers (containing ledger index, hash, parent hash, close time, and checksums). Each ledger entry can be looked up individually, and the entire state data represents a complete snapshot that any server can download to process transactions and answer queries.

## Practical Applications
Servers use ledger structure to maintain synchronized copies of all network data, process new transactions, and answer queries about current account states. The structure enables efficient verification of data integrity through hashing and supports the consensus mechanism that validates new ledger versions.

## Important Considerations
Ledger versions are only considered immutable after validation by consensus - unvalidated ledgers may have the same index but different contents. Two ledgers with identical hashes are always completely identical, while ledgers with the same index from different chains can have different hashes. The close time is rounded (usually by 10 seconds) and the ledger header maintains a fixed size regardless of transaction set or state data size.