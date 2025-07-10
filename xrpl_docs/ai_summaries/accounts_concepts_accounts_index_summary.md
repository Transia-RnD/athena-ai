# AI Summary: concepts/accounts/index.md

**Source:** https://xrpl.org/docs/concepts/accounts/index
**Category:** accounts
**Generated:** 2025-07-10 16:18:32

---

## XRPL Accounts Documentation Summary

**Overview:**
An Account in the XRP Ledger represents a holder of XRP and sender of transactions, consisting of an address, XRP balance, sequence number, and transaction history. Accounts are created automatically when receiving sufficient XRP funding, with no dedicated "create account" transaction required.

**Key Concepts and Terminology:**
• **Address** - Unique identifier (e.g., rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn)
• **Sequence Number** - Ensures transactions are applied in correct order and only once
• **Reserve** - Portion of XRP balance set aside and locked
• **AccountRoot** - Ledger entry storing account's core data
• **Trust Lines** - Accounting relationships for non-XRP assets
• **Multi-signing** - Multiple cryptographic signatures for authorization
• **Black Hole** - Address with no known secret key where XRP is lost forever

**Main Technical Details:**
Accounts store core data in AccountRoot ledger entries including address, XRP balance, sequence number, and transaction history. Authorization methods include master key pairs (intrinsic but can be disabled), regular key pairs (rotatable), and signer lists for multi-signing. Account creation occurs through Payment transactions that fund mathematically-valid addresses with sufficient XRP.

**Practical Applications:**
Primary use cases include sending/receiving XRP payments, holding XRP balances, and serving as connection points for Trust Lines that enable trading of other currencies and assets on the XRPL.

**Important Warnings and Limitations:**
Funding an account requires paying the account reserve (currently locks up XRP indefinitely), and funding does not grant control over the account - only possession of the secret key provides account access. Users should consider whether direct XRPL account ownership justifies the reserve cost compared to exchange-held accounts.