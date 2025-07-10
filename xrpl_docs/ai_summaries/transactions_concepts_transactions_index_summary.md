# AI Summary: concepts/transactions/index.md

**Source:** https://xrpl.org/docs/concepts/transactions/index
**Category:** transactions
**Generated:** 2025-07-10 16:16:54

---

## XRPL Transactions Documentation Summary

**Overview:**
Transactions are the exclusive mechanism for modifying the XRP Ledger, requiring digital signatures and consensus validation to become final. They encompass not only payments but also account management, key rotation, and decentralized exchange operations.

**Key Concepts and Terminology:**
• **Transaction Hash** - Unique identifier for each signed transaction, serves as proof of payment
• **Transaction Cost** - Anti-spam fee required for all transactions, charged even for failed ones
• **Consensus Process** - Network validation mechanism that determines which transactions are included
• **Pseudo-transactions** - System-generated transactions that don't require signatures but need consensus
• **Fee Level** - Minimum cost threshold (base level 256 = 10 drops for reference transactions)
• **Transaction Blob** - Binary data format of signed transactions submitted to network

**Main Technical Details:**
The transaction lifecycle involves six steps: creating unsigned JSON, adding authorization signatures, submitting to rippled servers, consensus validation, canonical application to ledger, and final validation. Three authorization methods are supported: master private key signatures, regular key signatures, and multi-signatures. Failed transactions (tec class) are still included in ledgers to maintain sequence numbering and prevent network abuse.

**Practical Applications:**
Transactions enable XRP payments, token transfers, account settings management, cryptographic key rotation, and decentralized exchange trading. The transaction hash serves as verifiable proof of payment that anyone can lookup for confirmation.

**Important Warnings and Limitations:**
Transaction results are only final when included in a validated ledger - provisional results can change. Only master private keys can disable master keys or permanently remove freeze abilities. Accounts must always maintain at least one signing method and cannot remove all authorization mechanisms.