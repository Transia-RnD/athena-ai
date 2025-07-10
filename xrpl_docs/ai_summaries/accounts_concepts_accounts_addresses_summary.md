# AI Summary: concepts/accounts/addresses.md

**Source:** https://xrpl.org/docs/concepts/accounts/addresses
**Category:** accounts
**Generated:** 2025-07-10 16:18:52

---

# XRPL Addresses Documentation Summary

## Overview
XRPL addresses are unique identifiers for XRP Ledger accounts using base58 encoding format. Addresses are mathematically derived from cryptographic key pairs and can be generated entirely offline without communicating with the XRP Ledger network.

## Key Concepts and Terminology
• **Address** - Unique identifier for XRPL accounts in base58 format
• **Account ID** - RIPEMD160 hash of SHA-256 hash of public key (20 bytes)
• **Black hole addresses** - Addresses not derived from known secret keys, making funds permanently inaccessible
• **Type prefix** - One-byte prefix (0x00 for addresses) to distinguish different encoded data types
• **Base58 encoding** - Encoding method using custom dictionary starting with 'r'
• **Checksum** - First 4 bytes of double SHA-256 hash for error detection

## Main Technical Details
The address generation process involves:
1. Starting with 33-byte ECDSA secp256k1 or 32-byte Ed25519 public key
2. Computing RIPEMD160(SHA-256(public_key)) to get Account ID
3. Adding type prefix (0x00) and calculating checksum via double SHA-256
4. Concatenating payload and checksum, then base58 encoding the result

Special encoding considerations include prefixing Ed25519 keys with 0xED byte and using the custom base58 dictionary "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz".

## Practical Applications
• **Account creation** - Any valid address becomes an account when funded with XRP
• **Transaction signing** - Addresses identify transaction senders (must be funded accounts)
• **Key management** - Addresses can represent regular keys or signer list members
• **Offline generation** - Addresses can be created without network connectivity
• **Trust lines** - Used in RippleState entries for token relationships

## Important Warnings and Limitations
**Critical:** Funds sent to black hole addresses are permanently lost since no one controls the private keys. The one-way hash function makes it impossible to derive public keys from addresses alone, which is why transactions must include both the public key and address. Several special addresses exist with historical significance, including ACCOUNT_ZERO and ACCOUNT_ONE used for internal protocol functions, and various black hole addresses that have consumed XRP permanently.