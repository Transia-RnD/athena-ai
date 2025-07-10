# AI Summary: concepts/transactions/fees.md

**Source:** https://xrpl.org/docs/concepts/transactions/fees
**Category:** transactions
**Generated:** 2025-07-10 16:17:07

---

## XRPL Fees Documentation Summary

**Overview:**
The XRP Ledger implements multiple fee types to protect against network abuse while allowing optional user-defined fees. These include neutral fees that are destroyed (not paid to anyone) and optional fees that users can collect from each other.

**Key Concepts and Terminology:**
• **Transaction Cost** - Miniscule amount of XRP destroyed when sending transactions
• **Reserve Requirement** - Minimum XRP an account must hold, increases with owned objects
• **Transfer Fees** - Optional percentage fees charged by currency issuers
• **Trust Line Quality** - Setting allowing accounts to value balances above/below face value
• **Fee Escalation** - Mechanism where fees increase rapidly during high network traffic
• **Reference Transaction** - Standard single-signed transaction requiring a fee

**Main Technical Details:**
The fee system uses escalation based on network load - fees remain low during normal conditions but increase dramatically during high traffic to deter abuse. Each server maintains a minimum cost threshold, and transactions below this threshold are rejected. Fee levels start at a base of 256 (10 drops for reference transactions), with limits on transactions per ledger that adjust based on consensus health.

**Practical Applications:**
Transaction costs prevent spam attacks, reserve requirements discourage ledger bloat, and transfer fees allow token issuers to monetize their currencies. The system enables legitimate users to pay higher fees for priority processing during network congestion.

**Important Warnings and Limitations:**
External fees (outside the ledger) are common from financial institutions and service providers - users should always verify fee schedules before conducting business. The decentralized nature means no single party can require network access fees, but various service fees may still apply.