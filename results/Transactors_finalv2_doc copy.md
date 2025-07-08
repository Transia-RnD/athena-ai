---

# XRPL Transaction Type System

This document describes the transaction type system in XRPL, including the macro-based registration mechanism, handler classes, consequences factory, and the process for extending the system with new transaction types.

---

## 1. Transaction Types Table

The transaction types are defined using the `TRANSACTION` macro in `transactions.macro`. Each entry specifies:

- **Tag**: The transaction type identifier (e.g., `ttPAYMENT`)
- **Value**: Numeric code for the transaction type
- **Handler Class**: The C++ class in the `ripple` namespace that implements the transaction logic
- **Delegatable**: Whether the transaction can be delegated
- **Fields**: Required and optional fields for the transaction
- **Consequences Factory**: The type of consequences factory used (see Section 2)

| Tag                | Value | Handler Class         | Delegatable           | Consequences Factory | Fields (summary)         |
|--------------------|-------|----------------------|-----------------------|---------------------|--------------------------|
| ttPAYMENT          | 0     | Payment              | Delegation::delegatable | Normal              | sfDestination, sfAmount, ... |
| ttVAULT_CLAWBACK   | 70    | VaultClawback        | Delegation::delegatable | Normal              | sfVaultID, sfHolder, ... |
| ttBATCH            | 71    | Batch                | Delegation::notDelegatable | Custom              | sfRawTransactions, sfBatchSigners |
| ttAMENDMENT        | 100   | EnableAmendment      | Delegation::notDelegatable | Blocker             | sfLedgerSequence, sfAmendment |
| ...                | ...   | ...                  | ...                   | ...                 | ...                      |

**Note:** The full list is in `xrpl/protocol/detail/transactions.macro`.

---

## 2. ConsequencesFactory Mechanism

Each transaction handler class in the `ripple` namespace defines a static member `ConsequencesFactory` that determines how the transaction's consequences are calculated. The system uses C++ concepts and template specialization to select the appropriate logic.

### Types

- **Transactor::Normal**: Standard consequences calculation.
- **Transactor::Blocker**: Used for transactions that block further processing (e.g., amendments).
- **Transactor::Custom**: Handler provides its own logic.

### Example

```cpp
template <class T>
requires(T::ConsequencesFactory == Transactor::Normal)
TxConsequences consequences_helper(PreflightContext const& ctx)
{
    return TxConsequences(ctx.tx);
}

template <class T>
requires(T::ConsequencesFactory == Transactor::Blocker)
TxConsequences consequences_helper(PreflightContext const& ctx)
{
    return TxConsequences(ctx.tx, TxConsequences::blocker);
}

template <class T>
requires(T::ConsequencesFactory == Transactor::Custom)
TxConsequences consequences_helper(PreflightContext const& ctx)
{
    return T::makeTxConsequences(ctx);
}
```

The correct overload is selected at compile time based on the handler's `ConsequencesFactory` type.

---

## 3. Registering New Transaction Types

To register a new transaction type:

1. **Define the Transaction Macro**  
   Add a `TRANSACTION` entry in `transactions.macro`:
   ```cpp
   TRANSACTION(ttMY_NEW_TYPE, 200, MyNewType, Delegation::delegatable, ({ {sfField1, soeREQUIRED}, ... }))
   ```

2. **Implement the Handler Class**  
   Create a handler class in the `ripple` namespace, e.g., `ripple::MyNewType`, implementing the required logic.

3. **Include the Handler in applySteps.cpp**  
   Add an `#include` for your handler in `src/xrpld/app/tx/detail/applySteps.cpp`:
   ```cpp
   #include <xrpld/app/tx/detail/MyNewType.h>
   ```

4. **Build and Test**  
   Rebuild the project and add tests for your new transaction type.

---

## 4. Batch Transactions (`ttBATCH`)

**Purpose:**  
Batch transactions allow multiple transactions to be submitted and processed together.

**Macro Definition:**
```cpp
TRANSACTION(ttBATCH, 71, Batch, Delegation::notDelegatable, ({
    {sfRawTransactions, soeREQUIRED},
    {sfBatchSigners, soeOPTIONAL},
}))
```

**Fields:**
- `sfRawTransactions` (REQUIRED): The set of transactions to execute in the batch.
- `sfBatchSigners` (OPTIONAL): Signers for the batch.

**Processing Logic:**
- The `Batch` handler parses and validates each transaction in `sfRawTransactions`.
- Each transaction is processed in sequence, with the batch as a single atomic operation if possible.
- Errors in individual transactions may cause the entire batch to fail, depending on implementation.

---

## 5. Pseudo-Transactions (e.g., `ttAMENDMENT`)

**Definition:**  
Pseudo-transactions are system-generated and not submitted by users. They are used for protocol-level changes, such as enabling amendments.

**Example:**
```cpp
TRANSACTION(ttAMENDMENT, 100, EnableAmendment, Delegation::notDelegatable, ({
    {sfLedgerSequence, soeREQUIRED},
    {sfAmendment, soeREQUIRED},
}))
```

**Handling:**
- Pseudo-transactions are created and inserted by the system.
- They are processed by their handler class (e.g., `EnableAmendment`).
- They often use the `Blocker` consequences factory to prevent further transactions in the same ledger.

---

## 6. Extending the System with New Transaction Types

**Step-by-Step Process:**

1. **Define the Transaction Macro**  
   Add a new `TRANSACTION` entry in `transactions.macro` with a unique tag and value.

2. **Implement the Handler**  
   - Create a new handler class in the `ripple` namespace.
   - Implement the required transaction logic and static `ConsequencesFactory` member.

3. **Include the Handler**  
   - Add an `#include` for your handler in `src/xrpld/app/tx/detail/applySteps.cpp`.

4. **Register Fields**  
   - Ensure all custom fields are defined and handled appropriately.

5. **Build and Test**  
   - Rebuild the codebase.
   - Add unit and integration tests for your new transaction type.

**Example:**
```cpp
// transactions.macro
TRANSACTION(ttMY_NEW_TYPE, 200, MyNewType, Delegation::delegatable, ({
    {sfField1, soeREQUIRED},
    {sfField2, soeOPTIONAL},
}))

// Handler implementation (MyNewType.h)
namespace ripple {
class MyNewType : public Transactor { ... };
}

// applySteps.cpp
#include <xrpld/app/tx/detail/MyNewType.h>
```

---

**Note:**  
All transaction types must have a corresponding handler class in the `ripple` namespace and be included in `applySteps.cpp` to be recognized by the system.

---

## References

- `xrpl/protocol/detail/transactions.macro`
- `src/xrpld/app/tx/detail/applySteps.cpp`
- Handler classes in `src/xrpld/app/tx/detail/`

---

This documentation should provide a comprehensive overview for developers working with XRPL transaction types and extending the system.