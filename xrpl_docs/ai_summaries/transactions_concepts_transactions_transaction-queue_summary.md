# AI Summary: concepts/transactions/transaction-queue.md

**Source:** https://xrpl.org/docs/concepts/transactions/transaction-queue
**Category:** transactions
**Generated:** 2025-07-10 16:18:18

---

## XRPL Transaction Queue Summary

### Overview
The XRPL transaction queue is a mechanism used by `rippled` servers to manage transactions that cannot immediately enter the current ledger due to high network traffic or insufficient fees. Rather than discarding these transactions, the queue holds them for inclusion in future ledgers, working alongside the open ledger cost system to maintain network efficiency during periods of high demand.

### Key Concepts and Terminology
• **Open Ledger Cost** - Dynamic fee that escalates when ledger size exceeds target capacity
• **Fee Averaging** - Ability to submit high-fee transactions that "push" queued transactions into the ledger
• **Consensus Process** - Multi-round validation where queued transactions play a role in ledger building
• **Fee Level** - Relative transaction cost compared to minimum required for that transaction type
• **LastLedgerSequence** - Optional field that sets transaction expiration

### Main Technical Details
The queue operates through a multi-step consensus process where validators propose transaction sets, queue rejected transactions, and use queued transactions to build subsequent ledger proposals. Transactions are ranked by relative fee level (not absolute XRP cost) and processed in normalized order to ensure consistency across servers. The system enforces strict queuing restrictions including proper authorization, valid signatures, and sufficient XRP balance for fees and reserves.

### Practical Applications
• **Low-priority transactions** - Submit with lower fees during high-traffic periods
• **Traffic management** - Continue transacting during network congestion
• **Fee optimization** - Use fee averaging to expedite multiple queued transactions
• **Transaction planning** - Queue transactions for future execution when immediate processing isn't critical

### Important Warnings and Limitations
**Critical Restrictions**: Maximum 10 transactions per account, transactions with AccountTxnID cannot be queued, and LastLedgerSequence must be at least current ledger + 2. **Financial Requirements**: Senders must maintain sufficient XRP for all queued transaction fees (capped at base reserve), maximum possible XRP sends, and account reserves. **Indefinite Queuing Risk**: Transactions can remain queued indefinitely until processed, expired, canceled, or dropped due to queue capacity limits, potentially blocking subsequent transactions from the same account.