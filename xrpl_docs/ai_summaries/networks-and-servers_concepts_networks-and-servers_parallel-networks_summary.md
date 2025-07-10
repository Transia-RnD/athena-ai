# AI Summary: concepts/networks-and-servers/parallel-networks.md

**Source:** https://xrpl.org/docs/concepts/networks-and-servers/parallel-networks
**Category:** networks-and-servers
**Generated:** 2025-07-10 16:12:44

---

# XRPL Parallel Networks Documentation Summary

## Overview
The XRP Ledger operates one production network (Mainnet) alongside several alternative test networks (altnets) that allow developers to experiment with XRPL technology without affecting real transactions or risking actual money. These parallel networks are determined by each server's configured UNL (Unique Node List) - the validators it trusts for consensus.

## Key Concepts and Terminology
• **Mainnet** - The production XRP Ledger network where all real business occurs
• **Altnets** - Alternative networks for testing and development
• **UNL (Unique Node List)** - List of validators a server trusts for consensus
• **Test XRP** - Free cryptocurrency with no real-world value used on test networks
• **Consensus groups** - Validators that trust each other and form parallel networks

## Main Technical Details
The primary technical mechanism separating networks is the UNL configuration - servers follow whichever network contains their trusted validators. Different consensus groups create parallel networks even if servers connect to multiple networks, as long as they don't trust validators from other networks beyond their quorum settings. Test networks are typically centralized and operated by Ripple, making them resettable but less stable than Mainnet.

## Available Networks and Applications
• **Testnet** - Stable testing environment mirroring Mainnet amendments
• **Devnet** - Beta testing for unstable core software changes  
• **Hooks V3 Testnet** - Smart contract functionality preview
• **Sidechain-Devnet** - Cross-chain bridge feature testing with library support

## Important Warnings and Limitations
Test networks are centralized with no guarantees of stability or availability, unlike the decentralized Mainnet. Test XRP has no real value and is lost when networks reset, and these networks are primarily used for testing server configurations and network performance rather than production use.