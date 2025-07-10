# AI Summary: concepts/ledgers/index.md

**Source:** https://xrpl.org/docs/concepts/ledgers/index
**Category:** ledgers
**Generated:** 2025-07-10 16:15:41

---

# XRPL Ledgers Documentation Summary

## Overview
The XRP Ledger is a shared, global ledger that maintains data integrity through a distributed network where each server keeps a full copy of the ledger database. Ledgers are organized as a series of blocks (ledger versions) that record transaction history and state changes through a consensus process.

## Key Concepts and Terminology
• **Ledger versions/ledgers** - Individual blocks in the blockchain sequence
• **Ledger Index** - Identifies the correct order of ledgers
• **Open ledger** - Current in-progress ledger accepting new transactions
• **Closed ledgers** - Pending ledgers awaiting validation
• **Validated ledgers** - Immutable, finalized ledgers
• **Consensus** - Distributed agreement protocol preventing double-spending
• **Validation** - Signed statement confirming ledger built through consensus
• **Proposal** - Signed statement of transactions for next consensus ledger

## Main Technical Details
Each ledger consists of three components: a header (containing Ledger Index, hashes, and metadata), a transaction tree (transactions applied from previous ledger), and a state tree (all current ledger data including balances and settings). The system maintains ledger continuity through a publication stream that delivers fully-validated ledgers to clients, with servers attempting to maintain continuous streams unless they fall behind.

## Practical Applications
• Maintaining transaction history and account states across the network
• Enabling trustless verification without relying on single institutions
• Supporting real-time ledger streaming for client applications
• Facilitating consensus-based transaction validation

## Important Considerations
Byzantine failures can cause servers to reach different conclusions about the last closed ledger, requiring validation processes to resolve differences. Servers may become desynced during consensus rounds and must switch strategies to acquire the consensus ledger when supermajority agreement exists.