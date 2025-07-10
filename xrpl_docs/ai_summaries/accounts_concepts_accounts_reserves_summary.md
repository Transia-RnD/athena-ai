# AI Summary: concepts/accounts/reserves.md

**Source:** https://xrpl.org/docs/concepts/accounts/reserves
**Category:** accounts
**Generated:** 2025-07-10 16:19:05

---

# XRPL Reserves Documentation Summary

## Overview
The XRP Ledger implements reserve requirements to prevent spam and maintain ledger efficiency by requiring accounts to hold minimum amounts of XRP. These reserves consist of a base reserve for account existence and owner reserves for each ledger object owned, with requirements adjustable through validator consensus.

## Key Concepts and Terminology
• **Base Reserve** - Minimum XRP required for any address to exist in the ledger
• **Owner Reserve** - Additional XRP required for each object owned by an account
• **Owner Count** - Number of objects an account owns that count toward reserves
• **Fee Voting** - Consensus process for adjusting reserve requirements
• **Incremental Reserve** - Per-item cost for owned objects

## Main Technical Details
The current mainnet requirements are a base reserve plus owner reserve per item owned. Objects counting toward reserves include Checks, Escrows, NFT Offers, Payment Channels, Trust Lines, and others. Special cases exist for NFTs (grouped in pages of up to 32), Trust Lines (shared between accounts), and Oracles (1-2 items based on PriceData objects). Reserve calculations use the formula: (OwnerCount × incremental_reserve) + base_reserve.

## Practical Applications
Reserves prevent ledger bloat while allowing normal operations - reserved XRP can pay transaction fees and be recovered by deleting accounts or objects. Applications can query current reserves using server_info or server_state methods, and calculate account requirements using the account_info method's OwnerCount field.

## Important Warnings and Limitations
Accounts below reserve requirements cannot send XRP or create new objects but can still receive transactions and use OfferCreate to acquire XRP. Transaction fees can reduce balances below reserves, potentially consuming all XRP. The first two trust lines have special reserve exemptions if funded with exactly the base reserve amount.