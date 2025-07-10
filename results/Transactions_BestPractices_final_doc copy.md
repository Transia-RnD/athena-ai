---

# CheckCreate Transaction Functionality and Architecture: Comprehensive Lesson Plan

This document provides a detailed, code-based breakdown of the CheckCreate transaction type in the XRPL (XRP Ledger) source code. It covers every aspect of CheckCreate, including its architecture, class structure, transaction lifecycle (preflight, preclaim, doApply), error handling, feature flags, ledger entry management, reserve and directory handling, account and trustline checks, expiration logic, and references to relevant source code. All explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [CheckCreate Overview](#checkcreate-overview)
- [Class Structure and Inheritance](#class-structure-and-inheritance)
- [Transaction Lifecycle](#transaction-lifecycle)
  - [Preflight: Transaction Field Validation](#preflight-transaction-field-validation)
  - [Preclaim: Ledger State Checks](#preclaim-ledger-state-checks)
  - [doApply: Applying the Transaction](#doapply-applying-the-transaction)
- [Transaction Flags](#transaction-flags)
- [Ledger Entry Management](#ledger-entry-management)
  - [Creating a Check Ledger Entry](#creating-a-check-ledger-entry)
  - [Directory Management: dirAdd and dirRemove](#directory-management-diradd-and-dirremove)
  - [Reserve Handling and adjustOwnerCount](#reserve-handling-and-adjustownercount)
  - [Deleting a Check Ledger Entry](#deleting-a-check-ledger-entry)
- [Account and Trustline Checks](#account-and-trustline-checks)
  - [Querying Balances and Holds](#querying-balances-and-holds)
  - [Freezing and Authorization](#freezing-and-authorization)
- [parentCloseTime and Expiration](#parentclosetime-and-expiration)
- [Error Handling and Logging](#error-handling-and-logging)
- [Feature Flags and Protocol Upgrades](#feature-flags-and-protocol-upgrades)
- [Practical Examples and Exercises](#practical-examples-and-exercises)
- [Key Source Code References](#key-source-code-references)
- [Summary Table](#summary-table)
- [Further Reading](#further-reading)

---

## CheckCreate Overview

- **Purpose:** The CheckCreate transaction allows an account to create a Check object, which is a deferred payment instrument that can be cashed by the destination account.
- **Location:** [`src/xrpld/app/tx/detail/CreateCheck.cpp`](https://github.com/XRPLF/rippled/blob/develop/src/ripple/app/tx/impl/CreateCheck.cpp)
- **Class:** `CreateCheck` (aliased as `CheckCreate`)
- **Lifecycle:** The transaction is processed in three main stages: `preflight`, `preclaim`, and `doApply`.

---

## Class Structure and Inheritance

- **Inheritance:**  
  The `CreateCheck` class inherits from the `Transactor` base class.  
  - `Transactor` provides the core interface and shared logic for all transaction types, including methods for preflight validation, preclaim checks, application to the ledger, fee calculation, signature verification, and permission checks.
  - By inheriting from `Transactor`, `CreateCheck` gains access to these mechanisms and only needs to implement transaction-specific logic.

- **ConsequencesFactoryType:**  
  `CreateCheck` sets `ConsequencesFactoryType` to `Normal`, indicating that this transaction has standard consequences (e.g., it does not block other transactions or require custom consequence handling).

- **Alias:**  
  The type alias `CheckCreate = CreateCheck;` is used for naming consistency with the transaction type.

---

## Transaction Lifecycle

### Preflight: Transaction Field Validation

**Function:** `CreateCheck::preflight(PreflightContext const& ctx)`

**Purpose:**  
Performs stateless validation of the transaction fields before any ledger access.

**Key Steps and Code Snippets:**

- **Feature Enablement:**  
  Checks if the `featureChecks` amendment is enabled. If not, the transaction is rejected with `temDISABLED`.
  ```cpp
  if (!ctx.rules.enabled(featureChecks))
      return temDISABLED;
  ```

- **Base Preflight:**  
  Calls `preflight1(ctx)` to perform standard transaction checks (signatures, fee, etc.). If these fail, the transaction is rejected.
  ```cpp
  NotTEC const ret{preflight1(ctx)};
  if (!isTesSuccess(ret))
      return ret;
  ```
  - `preflight1` is a shared routine in `Transactor` that checks for valid signatures, correct fee, valid account, and other basic transaction structure requirements.

- **Flags Validation:**  
  Ensures only valid flags are set. Any flag outside the allowed set (checked via `tfUniversalMask`) results in `temINVALID_FLAG`.
  ```cpp
  if (ctx.tx.getFlags() & tfUniversalMask)
      return temINVALID_FLAG;
  ```

- **Self-Check Prevention:**  
  Prevents creating a check to oneself. If the source and destination accounts are the same, returns `temREDUNDANT`.
  ```cpp
  if (ctx.tx[sfAccount] == ctx.tx[sfDestination])
      return temREDUNDANT;
  ```

- **Amount Validation:**  
  Ensures `SendMax` is a legal, positive amount and not a bad currency.
  ```cpp
  STAmount const sendMax{ctx.tx.getFieldAmount(sfSendMax)};
  if (!isLegalNet(sendMax) || sendMax.signum() <= 0)
      return temBAD_AMOUNT;
  if (badCurrency() == sendMax.getCurrency())
      return temBAD_CURRENCY;
  ```

- **Expiration Field Validation:**  
  If the optional `sfExpiration` field is present, it must be nonzero.
  ```cpp
  if (auto const optExpiry = ctx.tx[~sfExpiration]) {
      if (*optExpiry == 0)
          return temBAD_EXPIRATION;
  }
  ```

- **Error Codes:**  
  - `temDISABLED`: Feature not enabled.
  - `temINVALID_FLAG`: Invalid flag set.
  - `temREDUNDANT`: Check to self.
  - `temBAD_AMOUNT`: Invalid or non-positive amount.
  - `temBAD_CURRENCY`: Disallowed currency.
  - `temBAD_EXPIRATION`: Invalid expiration.

---

### Preclaim: Ledger State Checks

**Function:** `CreateCheck::preclaim(PreclaimContext const& ctx)`

**Purpose:**  
Performs stateful checks against the current ledger to ensure the transaction can be successfully applied.

**Key Steps and Code Snippets:**

- **Destination Account Existence:**  
  The destination account must exist in the ledger.
  ```cpp
  AccountID const dstId{ctx.tx[sfDestination]};
  auto const sleDst = ctx.view.read(keylet::account(dstId));
  if (!sleDst)
      return tecNO_DST;
  ```

- **Destination Account Flags:**  
  - If the `featureDisallowIncoming` is enabled and the destination has `lsfDisallowIncomingCheck`, the transaction is rejected.
  - If the destination is a pseudo-account, the transaction is rejected.
  ```cpp
  auto const flags = sleDst->getFlags();
  if (ctx.view.rules().enabled(featureDisallowIncoming) &&
      (flags & lsfDisallowIncomingCheck))
      return tecNO_PERMISSION;
  if (isPseudoAccount(sleDst))
      return tecNO_PERMISSION;
  ```

- **Destination Tag Requirement:**  
  If the destination requires a destination tag and none is provided, the transaction is rejected.
  ```cpp
  if ((flags & lsfRequireDestTag) && !ctx.tx.isFieldPresent(sfDestinationTag))
      return tecDST_TAG_NEEDED;
  ```

- **Trustline and Freeze Checks (for IOUs):**  
  For IOU checks, verifies that the issuer and trustlines are not frozen and that the destination is authorized to hold the currency.
  ```cpp
  STAmount const sendMax{ctx.tx[sfSendMax]};
  if (!sendMax.native()) {
      AccountID const& issuerId{sendMax.getIssuer()};
      if (isGlobalFrozen(ctx.view, issuerId))
          return tecFROZEN;
      AccountID const srcId{ctx.tx.getAccountID(sfAccount)};
      if (issuerId != srcId) {
          auto const sleTrust = ctx.view.read(keylet::line(srcId, issuerId, sendMax.getCurrency()));
          if (sleTrust && sleTrust->isFlag((issuerId > srcId) ? lsfHighFreeze : lsfLowFreeze))
              return tecFROZEN;
      }
      if (issuerId != dstId) {
          auto const sleTrust = ctx.view.read(keylet::line(issuerId, dstId, sendMax.getCurrency()));
          if (sleTrust && sleTrust->isFlag((dstId > issuerId) ? lsfHighFreeze : lsfLowFreeze))
              return tecFROZEN;
      }
  }
  ```

- **Expiration Check:**  
  If the check has already expired, the transaction is rejected.
  ```cpp
  if (hasExpired(ctx.view, ctx.tx[~sfExpiration]))
      return tecEXPIRED;
  ```

- **Error Codes:**  
  - `tecNO_DST`: Destination account does not exist.
  - `tecNO_PERMISSION`: Not permitted due to account flags or pseudo-account.
  - `tecDST_TAG_NEEDED`: Destination tag required.
  - `tecFROZEN`: Asset or trustline is frozen.
  - `tecEXPIRED`: Check has already expired.

---

### doApply: Applying the Transaction

**Function:** `CreateCheck::doApply()`

**Purpose:**  
Executes the transaction, modifying the ledger to create the Check object and update all related state.

**Key Steps and Code Snippets:**

- **Reserve Calculation and Check:**  
  Ensures the source account has enough XRP for the new reserve (owner count incremented by 1).
  ```cpp
  auto const sle = view().peek(keylet::account(account_));
  STAmount const reserve{
      view().fees().accountReserve(sle->getFieldU32(sfOwnerCount) + 1)};
  if (mPriorBalance < reserve)
      return tecINSUFFICIENT_RESERVE;
  ```

- **Check Ledger Entry Creation:**  
  Creates a new ledger entry of type `ltCHECK` with all required and optional fields.
  ```cpp
  std::uint32_t const seq = ctx_.tx.getSeqValue();
  Keylet const checkKeylet = keylet::check(account_, seq);
  auto sleCheck = std::make_shared<SLE>(checkKeylet);

  sleCheck->setAccountID(sfAccount, account_);
  AccountID const dstAccountId = ctx_.tx[sfDestination];
  sleCheck->setAccountID(sfDestination, dstAccountId);
  sleCheck->setFieldU32(sfSequence, seq);
  sleCheck->setFieldAmount(sfSendMax, ctx_.tx[sfSendMax]);
  if (auto const srcTag = ctx_.tx[~sfSourceTag])
      sleCheck->setFieldU32(sfSourceTag, *srcTag);
  if (auto const dstTag = ctx_.tx[~sfDestinationTag])
      sleCheck->setFieldU32(sfDestinationTag, *dstTag);
  if (auto const invoiceId = ctx_.tx[~sfInvoiceID])
      sleCheck->setFieldH256(sfInvoiceID, *invoiceId);
  if (auto const expiry = ctx_.tx[~sfExpiration])
      sleCheck->setFieldU32(sfExpiration, *expiry);

  view().insert(sleCheck);
  ```

- **Directory Management (dirAdd):**  
  Adds the Check to the owner directories of both the source and destination accounts.
  ```cpp
  auto viewJ = ctx_.app.journal("View");
  auto const page = dirAdd(view(), keylet::ownerDir(account_), sleCheck->key(), viewJ);
  if (!page)
      return tecDIR_FULL;
  sleCheck->setFieldU64(sfOwnerNode, *page);

  auto const destPage = dirAdd(view(), keylet::ownerDir(dstAccountId), sleCheck->key(), viewJ);
  if (!destPage)
      return tecDIR_FULL;
  sleCheck->setFieldU64(sfDestinationNode, *destPage);
  ```

- **Owner Count Adjustment:**  
  Increments the source account's `sfOwnerCount` by 1.
  ```cpp
  adjustOwnerCount(view(), sle, 1, ctx_.journal);
  ```

- **Error Codes:**  
  - `tecINSUFFICIENT_RESERVE`: Not enough XRP for reserve.
  - `tecDIR_FULL`: Directory is full.

---

## Transaction Flags

- **Validation:**  
  Only specific flags are allowed. Any flag outside the allowed set (checked via `tfUniversalMask`) results in `temINVALID_FLAG` in preflight.
- **Usage:**  
  No CheckCreate-specific flags are currently defined; the transaction is expected to have no flags set.

---

## Ledger Entry Management

### Creating a Check Ledger Entry

- **Object:**  
  The Check is a new ledger entry of type `ltCHECK`.
- **Fields Set:**  
  - `sfAccount` (source)
  - `sfDestination`
  - `sfSequence`
  - `sfSendMax`
  - Optional: `sfSourceTag`, `sfDestinationTag`, `sfInvoiceID`, `sfExpiration`
  - `sfOwnerNode`, `sfDestinationNode` (directory pages)

- **Insertion:**  
  The Check is inserted into the ledger with `view().insert(sleCheck)`.

### Directory Management: dirAdd and dirRemove

- **Purpose:**  
  To allow efficient lookup of Checks for both the source and destination accounts.

- **dirAdd:**  
  Adds the Check to the owner directories of both the source and destination accounts.
  ```cpp
  auto const page = dirAdd(view(), keylet::ownerDir(account_), sleCheck->key(), viewJ);
  auto const destPage = dirAdd(view(), keylet::ownerDir(dstAccountId), sleCheck->key(), viewJ);
  sleCheck->setFieldU64(sfOwnerNode, *page);
  sleCheck->setFieldU64(sfDestinationNode, *destPage);
  ```

- **dirRemove:**  
  When a Check is cashed or canceled, it is removed from both directories using `dirRemove`.

### Reserve Handling and adjustOwnerCount

- **Reserve Calculation:**  
  The required reserve is calculated as:
  ```cpp
  view().fees().accountReserve(sle->getFieldU32(sfOwnerCount) + 1)
  ```
  The source account must have at least this much XRP after the transaction.

- **Owner Count Adjustment:**  
  The source account's `sfOwnerCount` is incremented by 1 when the Check is created:
  ```cpp
  adjustOwnerCount(view(), sle, 1, ctx_.journal);
  ```
  This ensures the reserve requirement is enforced.

### Deleting a Check Ledger Entry

- **When:**  
  When a Check is cashed or canceled, the ledger entry is erased, and the reserve is released.
- **How:**  
  - Remove from both owner directories (`dirRemove`)
  - Decrement the source account's `sfOwnerCount`
  - Erase the Check object from the ledger

---

## Account and Trustline Checks

### Querying Balances and Holds

- **Balance Check:**  
  The source account's XRP balance is checked to ensure it can cover the new reserve.
- **Holds:**  
  For IOU checks, the code verifies that the issuer and trustlines are not frozen and that the destination is authorized to hold the currency.

### Freezing and Authorization

- **Global Freeze:**  
  ```cpp
  if (isGlobalFrozen(ctx.view, issuerId))
      return tecFROZEN;
  ```
- **Trustline Freeze:**  
  ```cpp
  if (sleTrust && sleTrust->isFlag((issuerId > srcId) ? lsfHighFreeze : lsfLowFreeze))
      return tecFROZEN;
  ```
- **Authorization:**  
  The code ensures the destination is not a pseudo-account and is authorized to receive the asset.

---

## parentCloseTime and Expiration

- **parentCloseTime:**  
  Used to determine if a Check has expired:
  ```cpp
  if (hasExpired(ctx.view, ctx.tx[~sfExpiration]))
      return tecEXPIRED;
  ```
  The expiration is compared to the parent ledger's close time.

---

## Error Handling and Logging

- **Logging:**  
  The code uses `JLOG` to log warnings and errors for malformed transactions and ledger state issues. This is important for diagnosing problems and maintaining ledger integrity.
- **Error Propagation:**  
  Error codes (e.g., `temDISABLED`, `tecNO_DST`, `tecFROZEN`) are returned at each stage to indicate the reason for transaction rejection or failure.

---

## Feature Flags and Protocol Upgrades

- **Feature Checks:**  
  The transaction checks for the `featureChecks` amendment to be enabled before proceeding. This ensures backward compatibility and allows for protocol upgrades to be rolled out safely.
  ```cpp
  if (!ctx.rules.enabled(featureChecks))
      return temDISABLED;
  ```
- **Impact:**  
  If the feature is not enabled, the transaction is not allowed, preventing use of unsupported features on older ledgers.

---

## Practical Examples and Exercises

- **Example 1: Valid CheckCreate Transaction**
  - Source: Account A
  - Destination: Account B (exists)
  - SendMax: 1000 USD.issuer (issuer not frozen, trustlines not frozen)
  - No flags set
  - Sufficient reserve in Account A
  - Result: Transaction succeeds, Check is created.

- **Example 2: Invalid CheckCreate (Check to Self)**
  - Source: Account A
  - Destination: Account A
  - Result: Fails with `temREDUNDANT`.

- **Example 3: Invalid CheckCreate (Bad Amount)**
  - SendMax: 0 USD.issuer
  - Result: Fails with `temBAD_AMOUNT`.

- **Exercise:**  
  Given a CheckCreate transaction with a frozen trustline between the source and issuer, what error code is returned?  
  **Answer:** `tecFROZEN`.

---

## Key Source Code References

- [`CreateCheck.cpp`](src/xrpld/app/tx/detail/CreateCheck.cpp)
- [`CreateCheck.h`](src/xrpld/app/tx/detail/CreateCheck.h)
- [`dirAdd` and `dirRemove` (directory management)](src/xrpld/ledger/View.h)
- [`adjustOwnerCount`](src/xrpld/app/tx/detail/Transactor.cpp)
- [`accountReserve`](src/xrpld/protocol/impl/Fees.cpp)
- [`hasExpired`](src/xrpld/protocol/impl/TxFormats.cpp)
- [Transactor base class](src/xrpld/app/tx/detail/Transactor.cpp)

---

## Summary Table

| Step         | Function/Mechanism      | Purpose/Action                                                                 |
|--------------|------------------------|-------------------------------------------------------------------------------|
| Preflight    | `preflight`            | Validate transaction structure, flags, and fields                             |
| Preclaim     | `preclaim`             | Check ledger state: account existence, reserve, destination status            |
| Apply        | `doApply`              | Deduct reserve, create Check, update directories, adjust owner count          |
| Flags        | `tfUniversalMask`      | Only allowed flags permitted; others rejected                                 |
| Ledger Entry | SLE (ltCHECK)          | Create (on apply), delete (on cash/cancel), update (rare)                     |
| Reserve      | `accountReserve`       | Deducted on create, released on delete                                        |
| Directory    | `dirAdd`/`dirRemove`   | Add/remove Check from source/destination directories                          |
| Balances     | Balance check          | Ensure sufficient funds and no restrictions                                   |
| Freezing     | `isGlobalFrozen`, etc. | Ensure destination/trustlines are not frozen                                  |
| Authing      | Trustline checks       | Ensure destination is authorized for issued currencies                        |
| parentCloseTime | Expiration logic    | Used for expiration and time-based logic                                      |
| adjustOwnerCount | Owner count        | Track number of owned objects for reserve calculation                         |

---

## Further Reading

- [XRPL Transaction Types: CheckCreate](https://xrpl.org/checkcreate.html)
- [XRPL Ledger Object: Check](https://xrpl.org/check.html)
- [XRPL Source Code: CheckCreate Implementation](https://github.com/XRPLF/rippled/blob/develop/src/ripple/app/tx/impl/CreateCheck.cpp)

---

**End of Lesson Plan**