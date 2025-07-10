# Consensus_TXOrdering Comprehensive Quiz

## Instructions
Answer the following questions based on the lesson plan on Consensus_TXOrdering. Make sure to review each section carefully. The quiz mixes multiple choice and true/false questions. Write your answers in the space provided and check your responses against the answer key at the end.

---

## Questions

1. Which of the following is the first component used to form the full sort key in the CanonicalTXSet ordering?  
   A. Transaction ID  
   B. Sequence Proxy  
   C. Salted Account Key  
   D. Fee Level  

2. True or False: In the CanonicalTXSet, if two transactions have the same salted account key and sequence proxy, the one with the higher transaction ID will be ordered first.

3. When a transaction is inserted into the CanonicalTXSet, under what condition can an existing transaction be replaced?  
   A. The new transaction has a lower fee.  
   B. The new transaction is from a different account.  
   C. The new transaction is a valid replacement (e.g., with a higher fee) for the same account and sequence.  
   D. The transaction IDs are different even if all other parameters match.

4. True or False: The purpose of the salted account key in the ordering process is to enhance security against manipulation by ensuring a non-predictable order.

5. In the context of consensus, what is a DisputedTx?  
   A. A transaction that has been finalized and applied to the ledger.  
   B. A transaction that is under review because it appears in one node’s set but not in another’s.  
   C. A transaction that is automatically rejected due to low fees.  
   D. A transaction that is held in the TxQ due to per-account limits.

6. True or False: If a DisputedTx does not receive a change in votes after a configurable number of rounds, it is considered stalled.

7. Which of the following best describes the role of the checkConsensus function?  
   A. It orders transactions based on fee level exclusively.  
   B. It determines the consensus state using parameters such as proposers, vote counts, timeouts, and stalled conditions.  
   C. It resets the transaction queue when consensus fails.  
   D. It manages the retry logic for blocked transactions.

8. True or False: In the TxQ ordering process, transactions from the same account may be blocked if a preceding transaction (blocker) has not been resolved.

9. When building the CanonicalTXSet for consensus, what interaction does it have with the TxQ?  
   A. It replaces all transactions in the TxQ regardless of block status.  
   B. It ignores fee levels from the TxQ.  
   C. It pulls eligible transactions in a canonical order and leaves blocked or ineligible ones in the TxQ.  
   D. It only accepts transactions with the lowest fee levels.

10. True or False: The consensus process described uses both threshold-based decision-making and a fallback mechanism if consensus is stalled or expired.

---

## Answer Key

1. C  
2. False (the lower lexicographical transaction ID is taken as a tie-breaker)  
3. C  
4. True  
5. B  
6. True  
7. B  
8. True  
9. C  
10. True