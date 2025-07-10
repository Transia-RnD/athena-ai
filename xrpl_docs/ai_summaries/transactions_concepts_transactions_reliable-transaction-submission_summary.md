# AI Summary: concepts/transactions/reliable-transaction-submission.md

**Source:** https://xrpl.org/docs/concepts/transactions/reliable-transaction-submission
**Category:** transactions
**Generated:** 2025-07-10 16:17:24

---

# XRPL Reliable Transaction Submission Summary

## Overview
This document outlines best practices for financial institutions and services to submit transactions to the XRP Ledger reliably, ensuring transactions are validated or rejected in a verifiable and prompt manner. The guidance focuses on achieving idempotency (processing transactions once and only once) and verifiability (determining final transaction results).

## Key Concepts and Terminology
• **Idempotency** - Transactions processed exactly once or not at all
• **Verifiability** - Applications can determine final transaction results
• **LastLedgerSequence** - Optional parameter preventing transactions from being included after a specific ledger version
• **Provisional results** - Temporary transaction outcomes that may change before final validation
• **Validated ledger** - Contains immutable, final transaction results
• **Reference transaction** - Standard single-signed transactions requiring fees
• **Consensus process** - Network agreement on transaction order and inclusion

## Main Technical Details
The transaction lifecycle involves: (1) account owner creates and signs transaction, (2) submission to network as candidate transaction, (3) consensus and validation process applies transaction to ledger, and (4) validated ledger includes final, immutable results. Applications must distinguish between provisional results from in-progress ledgers and final results from validated ledgers. The document recommends using LastLedgerSequence parameter set to 4 greater than the last validated ledger index to ensure prompt validation or rejection.

## Practical Applications
Financial institutions should submit transactions to trusted rippled servers and implement proper status checking mechanisms. Applications should query transaction status repeatedly until results appear in validated ledgers. The guidance includes a flowchart for reliable transaction submission processes and emphasizes the importance of using authoritative transaction results for business decisions.

## Important Warnings and Limitations
Applications failing to follow best practices risk submitting transactions that are never executed, mistaking provisional results for final ones, or failing to find authoritative transaction results. These errors can lead to serious problems like duplicate payments. Transaction costs can increase after submission, potentially delaying inclusion in ledgers, and network outages create additional challenges for determining transaction status.