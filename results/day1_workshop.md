---

# Distributed Ledger Protocols: Comprehensive Assignment

## Instructions

- Answer each question thoroughly.
- Where applicable, cite specific mechanisms or code snippets.
- Pay special attention to cases where a feature is **not** present, is **disabled**, or where "None" is a valid or important state.

---

### 1. Peer Protocol and Discovery

**a.** Explain how a node discovers peers in the network. What happens if peer discovery is disabled or not configured?  
**Answer:**  
Nodes discover peers via peer discovery protocols, which may include DNS seeds, static configuration, or peer gossip. If peer discovery is disabled or not configured, the node will only connect to explicitly specified peers (fixed peers), and will not automatically find or connect to new peers, potentially isolating it from the network.

**b.** What is the function of the peer protocol port? What are the consequences if this port is not open or is misconfigured?  
**Answer:**  
The peer protocol port is used for peer-to-peer communication between nodes. If this port is not open or is misconfigured, the node cannot accept incoming peer connections, limiting its ability to participate in the network and potentially preventing it from syncing with the ledger.

---

### 2. Node Key Pair

**a.** What is the purpose of the node key pair? What are the risks if a node does not have a key pair configured?  
**Answer:**  
The node key pair is used to sign messages and identify the node cryptographically. If a node does not have a key pair, it cannot participate in secure communication, cannot be uniquely identified, and may be rejected by other nodes.

---

### 3. Fixed Peers and Peer Reservations

**a.** Describe the difference between fixed peers and peer reservations. What happens if neither is configured?  
**Answer:**  
Fixed peers are nodes that are always connected to, while peer reservations are slots reserved for specific peers. If neither is configured, the node relies entirely on dynamic peer discovery, which may not be reliable or possible in private or restricted networks.

---

### 4. Private Peers and Private Server Configuration

**a.** What does it mean to configure a server as private (`PEER_PRIVATE = true`)? What functionalities are disabled in this mode?  
**Answer:**  
A private server does not accept incoming connections from unknown peers and does not participate in peer discovery. It only connects to explicitly configured peers. This disables automatic peer discovery and public peering.

**b.** What are the pros and cons of private peering configurations?  
**Answer:**  
Pros: Enhanced security, reduced attack surface, predictable network topology.  
Cons: Reduced redundancy, risk of isolation, manual configuration required.

---

### 5. Fee Voting

**a.** How does fee voting work in the network? What happens if a node does not participate in fee voting?  
**Answer:**  
Nodes propose and vote on transaction fees during consensus. If a node does not participate, it simply follows the majority decision and does not influence fee changes.

---

### 6. Transaction Censorship Detection

**a.** How can a node detect transaction censorship? What are the limitations if censorship detection is not implemented?  
**Answer:**  
A node can detect censorship by comparing its mempool and ledger state with peers. If censorship detection is not implemented, the node may not notice if its transactions are being excluded from the ledger.

---

### 7. Invariant Checking

**a.** What is invariant checking? What are the risks if invariant checking is disabled?  
**Answer:**  
Invariant checking ensures that certain conditions (e.g., no negative balances) always hold after transactions. If disabled, invalid or malicious transactions could corrupt the ledger state.

---

### 8. Secure Signing

**a.** Why is secure signing important? What are the consequences if transactions are not signed or are signed insecurely?  
**Answer:**  
Secure signing ensures authenticity and integrity of transactions. If not signed or signed insecurely, transactions can be forged or tampered with.

---

### 9. Ledger States and Transaction Cost

**a.** What is the significance of the ledger state? What happens if a node cannot access the current ledger state?  
**Answer:**  
The ledger state represents the current balances and account data. If a node cannot access it, it cannot validate or submit transactions.

**b.** How is transaction cost determined? What if the cost is set to zero?  
**Answer:**  
Transaction cost is determined by network voting and is used to prevent spam. If set to zero, the network is vulnerable to spam attacks.

---

### 10. Cryptographic Keys

**a.** What are the different types of cryptographic keys used? What happens if a key is missing or compromised?  
**Answer:**  
Node keys, account keys, and signing keys are used. If a key is missing, the associated entity cannot participate. If compromised, security is lost.

---

### 11. Reliable Transaction Submission

**a.** Describe the process of reliable transaction submission. What are the risks if this process is not followed?  
**Answer:**  
Transactions are submitted, monitored for inclusion, and resubmitted if necessary. If not followed, transactions may be lost or not included in the ledger.

---

### 12. Accounts, Transactions, and Consensus

**a.** What is the role of accounts and transactions in the consensus process? What happens if a transaction is not included in consensus?  
**Answer:**  
Accounts hold balances and submit transactions. Transactions are included in consensus to update the ledger. If not included, the transaction is not executed.

---

### 13. Parallel Networks

**a.** What are parallel networks? What are the implications if a node is not aware of parallel networks?  
**Answer:**  
Parallel networks are separate instances of the protocol. If a node is not aware, it may connect to the wrong network or be isolated.

---

### 14. Reserves and Negative UNL

**a.** What is the reserve requirement? What happens if an account does not meet the reserve?  
**Answer:**  
A minimum balance is required to prevent spam. If not met, the account cannot submit transactions.

**b.** What is the negative UNL? What happens if it is not used?  
**Answer:**  
Negative UNL allows the network to ignore unreliable validators. If not used, consensus may be slowed or blocked by unreliable nodes.

---

### 15. Ledgers and Amendments

**a.** How are ledgers created and validated? What happens if a node does not receive a new ledger?  
**Answer:**  
Ledgers are created via consensus and validated by nodes. If a node does not receive a new ledger, it falls behind and may be unable to participate.

**b.** What are amendments? What happens if a node is amendment-blocked?  
**Answer:**  
Amendments are protocol upgrades. If a node is amendment-blocked, it cannot participate in consensus until it upgrades.

---

### 16. Edge Cases and "None" Functionalities

**a.** Give an example of a situation where a "None" or disabled state is critical to network operation or security.  
**Answer:**  
If `PEER_PRIVATE` is set to true, peer discovery is disabled, which is critical for private networks to prevent unwanted connections.

**b.** What happens if the validation quorum (`VALIDATION_QUORUM`) is not set?  
**Answer:**  
If not set, the node may not be able to determine if consensus is reached, risking network partition or stalling.

---

### 17. Monitoring and Cluster Management

**a.** How does the `peers` command help monitor the network? What information is missing if a peer is not reporting?  
**Answer:**  
The `peers` command shows peer status, age, and cluster fee. If a peer is not reporting, its status and health are unknown, which may indicate a problem.

---

## Submission

- Submit your answers in a document.
- For each answer, explain the reasoning and cite relevant code or documentation where possible.

---

**End of Assignment**