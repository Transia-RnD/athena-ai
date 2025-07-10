# AI Summary: concepts/networks-and-servers/amendments.md

**Source:** https://xrpl.org/docs/concepts/networks-and-servers/amendments
**Category:** networks-and-servers
**Generated:** 2025-07-10 16:13:06

---

# XRPL Amendments Documentation Summary

## Overview
Amendments are the XRP Ledger's formal mechanism for implementing new features or changes to transaction processing rules. The system uses a consensus-based voting process where validators must achieve over 80% support for two weeks before any amendment becomes permanently enabled on the network.

## Key Concepts and Terminology
• **Amendment** - New features or changes to transaction processing that require network consensus
• **Flag Ledger** - Every 256th ledger where the amendment voting process occurs (approximately every 15 minutes)
• **EnableAmendment pseudo-transaction** - Special transaction that tracks amendment status changes
• **Amendment Blocked** - Security state where outdated servers cannot participate in network operations
• **Vetoed Amendments** - Amendments whose source code was removed before activation
• **Retired Amendments** - Amendments integrated into core protocol after 2+ years of activation

## Main Technical Details
The amendment process follows a structured timeline around flag ledgers: validators submit votes at Flag Ledger -1, votes are interpreted at Flag Ledger, status changes are recorded via pseudo-transactions at Flag Ledger +1, and amendments take effect at Flag Ledger +2. Amendments require sustained 80% validator support for two weeks, and if support drops below this threshold, the two-week countdown resets. Amendment-blocked servers cannot validate ledgers, process transactions, or participate in consensus until upgraded to compatible software versions.

## Practical Applications
Amendments enable the XRP Ledger to evolve with new features like multi-signing, payment channels, and escrow functionality while maintaining network consensus. Validators can configure their voting preferences for each amendment, and network operators must stay current with software updates to avoid being blocked from network participation.

## Important Warnings and Considerations
Amendment blocking is a critical security feature that prevents outdated servers from misinterpreting ledger data, but it completely disables their network functionality until upgraded. All amendments are considered irreversible once enabled, with no mechanism to disable them except through new amendments. Servers connecting to networks with different amendment sets (like Devnet) may become blocked if they lack the required amendment code.