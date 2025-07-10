# AI Summary: concepts/accounts/cryptographic-keys.md

**Source:** https://xrpl.org/docs/concepts/accounts/cryptographic-keys
**Category:** accounts
**Generated:** 2025-07-10 16:19:26

---

## XRPL Cryptographic Keys Documentation Summary

**Overview:**
The XRP Ledger uses cryptographic key pairs to authorize transactions through digital signatures, which are the only method for transaction authorization with no administrative override capabilities. Key pairs can function as master keys, regular keys, or signer list members regardless of the cryptographic algorithm used to generate them.

**Key Concepts and Terminology:**
• **Digital Signature** - Authorizes transactions for execution on the XRP Ledger
• **Key Pair** - Mathematical connection between private key (secret) and public key (public)
• **Seed** - Compact value used to derive private and public keys
• **Account ID** - Core 20-byte identifier derived from public key
• **Classic Address** - Base58 representation of Account ID with checksum
• **X-Address** - Combined Account ID and Destination Tag in base58 format
• **Master Key Pair** - Primary cryptographic keys for an account
• **Regular Key Pair** - Alternative signing keys that can be changed
• **Passphrase** - Optional input for generating seeds (less secure than random generation)

**Main Technical Details:**
The key derivation process flows from passphrase → seed → private key → public key → Account ID ↔ address. The system supports multiple cryptographic signing algorithms (Ed25519 and secp256k1), with different tools having different defaults. Private keys, seeds, and passphrases are secret information requiring careful protection, while public keys, Account IDs, and addresses are safe to share publicly. Account IDs don't necessarily represent funded accounts until they receive XRP to meet reserve requirements.

**Practical Applications:**
Key pairs enable transaction signing and account control, support multi-signing configurations, and allow for regular key rotation without changing the account address. The system accommodates both technical users who manage keys directly and applications that handle key management automatically.

**Important Warnings and Limitations:**
Critical security warning: compromised secret information (private key, seed, or passphrase) grants full account control with no recovery mechanism. Users must only generate keys with trusted devices and software, as compromised applications can expose secrets to malicious actors. Different tools may generate different addresses from the same seed unless the cryptographic algorithm is explicitly specified.