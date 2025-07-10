# AI Summary: concepts/consensus-protocol/fee-voting.md

**Source:** https://xrpl.org/docs/concepts/consensus-protocol/fee-voting
**Category:** consensus-protocol
**Generated:** 2025-07-10 16:15:13

---

## Overview

Fee voting is XRPL's mechanism for validators to collectively adjust network fees, including transaction costs and reserve requirements. Validators express their preferences every 15 minutes, and the network automatically adopts the median of trusted validators' preferences to balance network accessibility with spam protection.

## Key Concepts and Terminology

• **Reference transaction cost** - Base fee in drops (1 XRP = 1 million drops) destroyed for cheapest transactions
• **Account reserve** - Minimum XRP required to maintain an account 
• **Owner reserve** - Additional XRP required for each ledger object owned
• **Flag ledger** - Every 256th ledger where fee voting occurs
• **SetFee pseudo-transaction** - Transaction type that implements fee changes
• **Drops** - Smallest unit of XRP (0.000001 XRP)

## Main Technical Details

The voting process follows a 4-ledger cycle: validators submit votes in the ledger before a flag ledger, tally votes in the flag ledger, insert SetFee pseudo-transactions in the next ledger, and implement changes in the following ledger. Validators configure preferences in their rippled.cfg file and the network adopts the median values. When there's a tie between two median values, the system chooses the option closer to current settings.

## Practical Applications

Fee voting allows the network to adapt to XRP price fluctuations and changing network conditions while maintaining decentralized governance. Validators can adjust fees to keep transaction costs reasonable for users while ensuring adequate spam protection and resource management.

## Important Warnings and Limitations

Insufficient fees adopted by >50% of trusted validators could expose the network to denial-of-service attacks. Conservative approaches are recommended, especially when lowering reserves, as increases are more disruptive than decreases. The XRPFees amendment removed previous maximum fee limitations, allowing more flexible fee setting.