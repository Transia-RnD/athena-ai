# AI Summary: concepts/transactions/transaction-cost.md

**Source:** https://xrpl.org/docs/concepts/transactions/transaction-cost
**Category:** transactions
**Generated:** 2025-07-10 16:17:58

---

# XRPL Transaction Cost Documentation Summary

## Overview
The XRP Ledger implements a transaction cost system where each transaction must destroy a small amount of XRP to prevent spam and denial-of-service attacks. This cost dynamically increases with network load, making it expensive to overload the system while keeping normal usage affordable.

## Key Concepts and Terminology
• **Transaction Cost** - Small amount of XRP destroyed (not paid to anyone) for each transaction
• **Reference Transaction** - Standard single-signed transaction requiring minimum fee (10 drops)
• **Load Cost** - Server-specific threshold based on current processing load
• **Open Ledger Cost** - Network-wide threshold for immediate transaction inclusion
• **Fee Levels** - Proportional measurement system (256 = minimum fee level)
• **Queued Transactions** - Transactions meeting load cost but not open ledger cost
• **Drops** - Smallest XRP unit (1 XRP = 1,000,000 drops)

## Main Technical Details
The system operates on two cost thresholds: transactions below the load cost are rejected entirely, while those below the open ledger cost are queued for later ledgers. The open ledger uses a soft limit that triggers exponential fee escalation when exceeded. Different transaction types have varying base costs, from 0 drops for key reset transactions to 2,000,000 drops for account deletion and AMM creation.

## Practical Applications
• **Standard transactions** - 0.00001 XRP (10 drops) minimum cost
• **Multi-signed transactions** - Cost multiplied by (1 + number of signatures)
• **Complex transactions** - Higher fees for EscrowFinish with fulfillment data
• **Network congestion** - Automatic fee escalation during high traffic periods

## Important Warnings and Limitations
Transaction costs are permanently destroyed, not transferred to validators or any party. During network congestion, fees can escalate exponentially, making transactions expensive. Users should query current costs using server_info or fee methods before submitting transactions, as costs fluctuate based on real-time network conditions.