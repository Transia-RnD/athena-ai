# AI Summary: concepts/consensus-protocol/unl.md

**Source:** https://xrpl.org/docs/concepts/consensus-protocol/unl
**Category:** consensus-protocol
**Generated:** 2025-07-10 16:14:27

---

## XRPL Unique Node List (UNL) Documentation Summary

### Overview
The Unique Node List (UNL) is a server's curated list of validators that it trusts not to collude during the XRP Ledger consensus process. Each UNL entry represents an independent entity to ensure no single party has excessive control over network validation. The system requires high overlap (up to 90%) between different servers' UNLs to prevent network forks.

### Key Concepts and Terminology
• **UNL (Unique Node List)** - List of trusted validators for consensus
• **Validators** - Impartial nodes that process transactions and vote on ledger validation
• **UNL Overlap** - Percentage of shared validators between different servers' UNLs
• **Fork** - Network split where different sides cannot agree on transaction validity
• **Recommended Validator Lists** - Published lists of quality validators for easy UNL configuration
• **Default UNL (dUNL)** - Standard validator set published by XRP Ledger Foundation and Ripple
• **Publisher** - Entity that creates and maintains recommended validator lists
• **Supermajority** - >80% agreement threshold required for transaction confirmation

### Main Technical Details
The consensus mechanism requires validators to be online, operational, and impartial in processing transactions. Research determined that 90% UNL overlap is necessary to prevent forks in worst-case scenarios, significantly limiting customization flexibility. The system uses recommended validator lists with JSON format containing signed binary data, including sequence numbers, expiration times, and activation dates for coordinated updates. Publishers sign lists with public keys and distribute them via websites or peer-to-peer networks.

### Practical Applications
Server operators can configure UNLs using recommended lists from trusted publishers, with the default configuration using lists from XRP Ledger Foundation and Ripple. The system allows multiple publisher lists to be combined, creating a union of all validators across lists. This approach ensures network reliability while maintaining decentralization through diverse validator representation.

### Important Warnings and Limitations
Server operators must carefully select validator list publishers as their choices significantly impact network reliability. The 90% overlap requirement severely limits UNL customization options compared to the initially believed 60% threshold. Publishers wield considerable power in validator selection despite not participating in daily validation, making their trustworthiness crucial for network stability.