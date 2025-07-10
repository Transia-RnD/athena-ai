# AI Summary: concepts/networks-and-servers/peer-protocol.md

**Source:** https://xrpl.org/docs/concepts/networks-and-servers/peer-protocol
**Category:** networks-and-servers
**Generated:** 2025-07-10 16:12:09

---

# XRPL Peer Protocol Documentation Summary

## Overview
The XRP Ledger peer protocol defines how rippled servers communicate with each other across the network. It serves as the primary communication method for all network operations, including transaction sharing, ledger data requests, and consensus proposals. Servers establish connections using HTTPS with an upgrade to the XRPL/2.0 protocol.

## Key Concepts and Terminology
• **Peer Protocol** - Communication language between XRPL servers
• **Gossip Protocol** - Method for peer discovery and network connection
• **Node Key Pair** - Cryptographic identity for each server in peer communications
• **Fixed Peers** - Permanently connected peers based on IP addresses
• **Peer Reservations** - Priority connections identified by node keys
• **Private Peers** - Servers with hidden IP addresses for security
• **Public Hubs** - Hardcoded fallback servers for initial connections
• **Overlay Network** - Peer-to-peer network layered over the internet

## Main Technical Details
The protocol uses port 2459 (IANA assigned) or 51235 (legacy default) for peer connections. Servers discover peers through a gossip protocol, starting with hardcoded public hubs and expanding through peer referrals. Each server generates a unique node key pair for message signing and identity verification. Connection establishment involves HTTPS upgrade requests to switch to the XRPL protocol. The system supports both incoming and outgoing connections with configurable peer limits and reservation systems.

## Practical Applications
• **Network Participation** - Enables servers to join and maintain connections in the XRPL network
• **Transaction Broadcasting** - Facilitates sharing of candidate transactions across the network
• **Consensus Operations** - Supports proposal and validation of transaction sets
• **Data Synchronization** - Allows historical ledger data requests and sharing
• **Server Clustering** - Enables grouping of related servers for improved reliability
• **Validator Protection** - Private peer configuration protects important validators from attacks

## Important Warnings and Considerations
Servers should configure firewall port forwarding for optimal peer connectivity. Private servers require at least one non-private connection to participate in the network. Deleting server databases creates a new node identity unless a node_seed is configured. All peers are treated as untrusted unless explicitly clustered, requiring cryptographic verification of all communications. Fixed peer configurations require server restarts to take effect, while peer reservations can be adjusted during operation.