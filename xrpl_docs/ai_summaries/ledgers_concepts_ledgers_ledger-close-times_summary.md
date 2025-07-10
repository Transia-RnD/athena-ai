# AI Summary: concepts/ledgers/ledger-close-times.md

**Source:** https://xrpl.org/docs/concepts/ledgers/ledger-close-times
**Category:** ledgers
**Generated:** 2025-07-10 16:16:33

---

# XRPL Ledger Close Times Summary

## Overview
The XRP Ledger records when each ledger version closes using a `close_time` field that is rounded to 10-second intervals to facilitate network consensus. This rounding system ensures that ledger close times are strictly increasing, with child ledgers always having close times at least 1 second later than their parent ledgers.

## Key Concepts and Terminology
• **Close Time Resolution** - Currently set to 10 seconds for rounding consensus
• **Ledger Header** - Contains the close_time field and other ledger metadata
• **Parent/Child Ledger Relationship** - Sequential ledgers where child must have later close time
• **Consensus Round** - Process where validators agree on close time
• **Time-based Measurements** - Limited by the 10-second resolution for precision

## Main Technical Details
The close time calculation follows a specific process: validators first record their observed close time, reach consensus on the actual time, round to the nearest 10-second interval, and adjust if necessary to ensure the time is greater than the parent ledger's close time. Since ledgers typically close every 3-5 seconds, this creates patterns where close times commonly end in :00, :01, :02, :10, :11, :20, :21, etc. The system guarantees strictly increasing close times by adding 1 second to any rounded time that would equal or precede the parent ledger's close time.

## Practical Applications
This timing system is crucial for time-sensitive operations like Escrow transactions, where expiration dates are checked against the parent ledger's close time. The close time serves as the network's authoritative timestamp for all time-based smart contract functionality and transaction ordering.

## Important Limitations
The 10-second resolution means the ledger cannot make time-based measurements more precise than this interval, potentially causing time-sensitive operations to execute up to 10 seconds later than their specified real-world expiration times. Additionally, expiration checks use the parent ledger's close time rather than the current ledger's close time, since the current close time isn't known during transaction execution.