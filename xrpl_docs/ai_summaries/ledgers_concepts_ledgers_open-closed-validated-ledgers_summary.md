# AI Summary: concepts/ledgers/open-closed-validated-ledgers.md

**Source:** https://xrpl.org/docs/concepts/ledgers/open-closed-validated-ledgers
**Category:** ledgers
**Generated:** 2025-07-10 16:16:16

---

# XRPL Open, Closed, and Validated Ledgers - Documentation Summary

## Overview
The XRP Ledger operates with three distinct ledger states: open (temporary workspace), closed (proposed next state), and validated (confirmed previous state). Each server maintains one open ledger, zero or more closed ledgers, and an immutable history of validated ledgers that form the permanent blockchain record.

## Key Concepts and Terminology
• **Open Ledger** - Temporary workspace where new transactions are applied as received
• **Closed Ledger** - Proposed next state with transactions in canonical order, eligible for validation
• **Validated Ledger** - Immutable, consensus-confirmed ledger that becomes part of permanent history
• **Canonical Order** - Deterministic transaction ordering designed to prevent front-running
• **Consensus Process** - Distributed agreement protocol that resolves double-spending
• **Validation** - Signed statement confirming a ledger was built through consensus
• **Byzantine Failures** - Network disagreements resolved through supermajority consensus

## Main Technical Details
The ledger progression process is counterintuitive: servers don't convert open ledgers to closed ledgers directly. Instead, they discard the open ledger, create a new closed ledger by applying transactions in canonical order to a previous closed ledger, then build a new open ledger from the latest closed state. This process ensures deterministic results across the distributed network while handling the challenge that different servers may receive transactions in different orders.

## Practical Applications
• **Transaction Processing** - Open ledgers provide immediate tentative results for user transactions
• **Consensus Participation** - Closed ledgers serve as proposals during the consensus process
• **Historical Record** - Validated ledgers create the permanent, auditable transaction history
• **Decentralized Exchange** - Canonical ordering prevents manipulation of trading order execution

## Important Warnings and Limitations
Transactions in open ledgers show only tentative results that may differ from final outcomes since the open ledger may be discarded during consensus. The canonical ordering system, while preventing front-running, means transaction order in the final ledger may differ from submission order. Network participants must understand that only validated ledgers represent confirmed, irreversible states.