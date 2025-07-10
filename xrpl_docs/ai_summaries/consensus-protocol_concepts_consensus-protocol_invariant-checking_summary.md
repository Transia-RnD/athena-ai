# AI Summary: concepts/consensus-protocol/invariant-checking.md

**Source:** https://xrpl.org/docs/concepts/consensus-protocol/invariant-checking
**Category:** consensus-protocol
**Generated:** 2025-07-10 16:14:59

---

# XRPL Invariant Checking Documentation Summary

## Overview
Invariant checking is a critical safety feature of the XRP Ledger that acts as a second layer of validation, automatically examining every transaction's results before they're committed to the ledger. This system ensures that fundamental rules of the XRP Ledger are never violated, even if bugs exist in the main transaction processing code. If a transaction would break any invariant, it's rejected with a `tecINVARIANT_FAILED` result code and included in the ledger with no effects.

## Key Concepts and Terminology
• **Invariants** - Fundamental rules that must always hold true across all XRPL transactions
• **Real-time validation** - Invariant checks run automatically after each transaction before commitment
• **tecINVARIANT_FAILED** - Result code for transactions rejected due to invariant violations
• **tefINVARIANT_FAILED** - Result code for transactions that fail invariants during minimal processing
• **Safety layer** - Secondary validation system separate from normal transaction processing
• **Ledger integrity** - Protection against bugs that could corrupt the network or halt operations

## Main Technical Details and Processes
The invariant checker operates as an automated real-time validation system that examines transaction results before ledger commitment. The system includes 12+ active invariants covering:

**Core XRP Protection:**
- Transaction Fee Check: Validates fees are non-negative and within specified limits
- XRP Not Created: Ensures transactions only destroy XRP (via fees), never create it
- XRP Balance Checks: Enforces XRP balances stay between 0 and 100 billion XRP

**Account and Ledger Integrity:**
- Account Roots Not Deleted: Prevents account deletion except via AccountDelete transactions
- Ledger Entry Types Match: Ensures modified entries maintain correct types
- Valid New Account Root: Validates new accounts are created properly with correct sequences

**Asset and Trading Rules:**
- No XRP Trust Lines: Prevents creation of trust lines using XRP
- No Bad Offers: Ensures offers are for positive amounts and not XRP-to-XRP
- No Zero Escrow: Validates escrow entries hold appropriate XRP amounts

**NFT-Specific Validations:**
- ValidNFTokenPage: Ensures NFT minting/burning only occurs via proper transactions
- NFTokenCountTracking: Validates NFT page organization, sorting, and ownership

## Practical Applications and Use Cases
• **Network Protection**: Prevents bugs in transaction processing from corrupting the entire XRPL network
• **Data Integrity**: Ensures ledger data remains consistent and valid across all operations
• **Trust Maintenance**: Preserves confidence in the XRP Ledger by preventing impossible states
• **Development Safety**: Provides protection against future bugs in code updates or modifications
• **Automatic Validation**: Requires no manual intervention - operates transparently on every transaction
• **Debugging Aid**: Failed invariants help identify specific problems when transactions are rejected

## Important Warnings, Limitations, and Considerations
**Critical Limitations:**
- Invariant failures indicate serious problems that could potentially halt the entire network
- Transactions failing invariant checks are still included in the ledger (with tec codes) but have no effects
- The system is designed as a last resort - invariants should theoretically never trigger in normal operation

**Important Considerations:**
- Failed invariants suggest bugs in the main transaction processing code that need immediate attention
- The complexity of XRPL code makes invariant checking essential for maintaining network reliability
- Developers should understand these limits as they define hard boundaries for transaction processing
- Invariant violations are logged as fatal errors and require investigation to prevent network instability