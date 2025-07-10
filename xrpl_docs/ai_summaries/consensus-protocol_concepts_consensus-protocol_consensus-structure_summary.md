# AI Summary: concepts/consensus-protocol/consensus-structure.md

**Source:** https://xrpl.org/docs/concepts/consensus-protocol/consensus-structure
**Category:** consensus-protocol
**Generated:** 2025-07-10 16:13:44

---

# XRPL Consensus Structure Documentation Summary

## Overview
This document provides a comprehensive overview of the XRP Ledger's consensus mechanism, explaining how the peer-to-peer network maintains a shared, authoritative ledger through validation processes. The XRP Ledger creates new ledger versions every few seconds, with each validated version becoming immutable and part of the permanent ledger history.

## Key Concepts and Terminology
• **Ledger Version** - A snapshot of the network state with two identifiers: ledger index (sequential number) and ledger hash (digital fingerprint)
• **Validation** - The process by which the network agrees on ledger contents, making them immutable
• **Consensus** - Distributed agreement protocol used to prevent double-spending
• **Validators** - Servers that contribute to advancing ledger history by sending proposals and validations
• **Tracking Servers** - Servers that distribute transactions and respond to queries but don't validate
• **Last Closed Ledger** - The most recent ledger a server believes achieved network consensus
• **Proposals** - Signed statements indicating which transactions should be included in the next ledger
• **Transaction Result Codes** - tesSUCCESS (successful), tec (failed but included), others (provisional failures)

## Main Technical Details
The ledger stores account settings, XRP and token balances, distributed exchange offers, network settings, and timestamps. Transactions are the only way to authorize changes, and each must be cryptographically signed by an account owner. The consensus process typically takes under 5 seconds under normal conditions, with an upper limit of roughly 20 seconds indicating potential network problems. Servers may create multiple candidate ledger versions with the same index but different hashes, though only one becomes validated while others are discarded.

## Practical Applications
Applications can query ledger state for account balances, transaction history, and network settings. The system enables secure peer-to-peer transactions, token trading through the distributed exchange, and programmable money features. Client applications include wallets, gateways to financial institutions, and trading platforms that submit transactions to XRP Ledger servers.

## Important Warnings and Limitations
**Critical**: Applications must never rely on provisional results from candidate transactions - only transactions in validated ledgers with tesSUCCESS codes are final. Transactions may appear successful initially but still fail during validation. All transactions destroy some XRP as a transaction cost regardless of success or failure. The LastLedgerSequence field creates a deadline - if this ledger is validated without including the transaction, that transaction can never succeed.