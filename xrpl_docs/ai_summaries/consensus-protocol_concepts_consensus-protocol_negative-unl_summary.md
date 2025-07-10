# AI Summary: concepts/consensus-protocol/negative-unl.md

**Source:** https://xrpl.org/docs/concepts/consensus-protocol/negative-unl
**Category:** consensus-protocol
**Generated:** 2025-07-10 16:15:27

---

# Negative UNL - XRPL Documentation Summary

## Overview
The Negative UNL (Unique Node List) is a consensus protocol feature that improves the XRP Ledger's ability to maintain forward progress during partial network outages. It allows the network to temporarily exclude offline or malfunctioning validators from consensus requirements, enabling continued validation even when trusted validators are unavailable.

## Key Concepts and Terminology
• **Negative UNL** - A list of trusted validators believed to be offline or malfunctioning
• **Liveness** - The network's ability to make forward progress during outages
• **Quorum** - 80% of trusted validators needed for consensus (minimum 60% of total validators)
• **Reliability Score** - Percentage of last 256 ledgers where a validator's vote matched consensus
• **Flag Ledger** - Ledgers divisible by 256 where Negative UNL modifications occur
• **UNL (Unique Node List)** - List of validators a server trusts not to collude

## Main Technical Details
• Validators with reliability scores below 50% become candidates for Negative UNL inclusion
• Validators need reliability scores above 80% to be removed from Negative UNL
• Changes only occur on flag ledgers (approximately every 15 minutes)
• Maximum 25% of validators can be on Negative UNL simultaneously
• Consensus of remaining validators required to modify the Negative UNL
• No impact on transaction processing, only on validation finality

## Practical Applications
• Maintains network operation during validator maintenance or upgrades
• Handles temporary connectivity issues between validators
• Provides resilience against targeted attacks on specific validators
• Enables gradual adjustment to validator availability changes
• Supports network stability during hardware failures or natural disasters

## Important Warnings and Limitations
• Hard minimum of 60% of total validators required for any consensus
• If more than 20% of validators go offline simultaneously, network may halt validation
• Validators cannot propose adding themselves to Negative UNL
• Changes occur slowly to prevent time-based disagreements
• No effect in stand-alone server mode
• Network fragmentation risk if quorum thresholds aren't maintained