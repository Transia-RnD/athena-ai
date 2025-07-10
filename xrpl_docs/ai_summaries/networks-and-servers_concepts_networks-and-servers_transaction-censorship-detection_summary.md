# AI Summary: concepts/networks-and-servers/transaction-censorship-detection.md

**Source:** https://xrpl.org/docs/concepts/networks-and-servers/transaction-censorship-detection
**Category:** networks-and-servers
**Generated:** 2025-07-10 16:12:29

---

# XRPL Transaction Censorship Detection - Comprehensive Summary

## Overview
The XRP Ledger includes an automated transaction censorship detector (introduced in rippled 1.2.0) that monitors all rippled servers to identify when transactions are potentially being censored by the network. This system tracks transactions that should have been included in validated ledgers and issues warnings when transactions remain unprocessed after multiple consensus rounds, supporting the XRP Ledger's censorship-resistant design.

## Key Concepts and Terminology
• **Transaction Censorship Detector** - Automated system that tracks potentially censored transactions
• **Tracker** - Component that monitors transactions from consensus proposals through validation
• **Consensus Rounds** - Cycles where transactions are proposed and validated into ledgers
• **Validated Ledger** - Final ledger state after consensus completion
• **False Positives** - Innocent scenarios that trigger censorship warnings
• **Warning/Error Messages** - Log alerts issued when transactions remain unprocessed

## Main Technical Details and Processes
The detector operates through a three-step process: (1) adds all transactions from the server's initial consensus proposal to the tracker, (2) removes transactions that get included in the resulting validated ledger after consensus, and (3) issues warning messages for transactions remaining in the tracker for 15 ledgers or more. The system escalates alerts by issuing warnings every 15 ledgers up to five times, then issues a final error message after 75 ledgers before stopping notifications. All messages include transaction IDs, starting ledger numbers, and current ledger positions for investigation purposes.

## Practical Applications and Use Cases
• **Network Monitoring** - Enables all network participants to detect potential censorship attempts
• **Server Diagnostics** - Helps identify server synchronization issues or bugs
• **Network Health Assessment** - Provides transparency into transaction processing across the network
• **Compliance Verification** - Supports the XRP Ledger's censorship-resistant design goals
• **Bug Detection** - Can reveal transaction relay issues or processing inconsistencies

## Important Warnings, Limitations, and Considerations
The detector frequently produces false positives that require investigation before assuming malicious censorship. Common innocent causes include running incompatible server builds, server synchronization issues, or bugs in transaction relay mechanisms. Users should investigate flagged transactions starting with the assumption that causes are more likely innocent bugs rather than malicious censorship. The system only functions when the rippled server is properly synced with the network, and running compatible versions of the core XRP Ledger server is crucial to avoid false positives.