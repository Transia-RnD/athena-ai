#!/usr/bin/env python
# coding: utf-8

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/xahaud"
# indexer = AthenahIndexer("local", "id", "dist", "xahaud", "v1")
# indexer.build_from_dirs(
#     path,
#     ["src/ripple"],
#     "xahaud",
# )

from athenah_ai.client import AthenahClient

prompt: str = """
```
if (TER const result = trustTransferLockedBalance(
    ctx_.view(),
    *owner,
    sleOwner,
    sleIssuer,
    amount,
    0,
    Rate{1000000},
    ctx_.journal,
    WetRun); !isTesSuccess(result))
{
    JLOG(ctx_.journal.fatal())
        << "URIToken: trustTransferLockedBalance failed: " << result;
    return result;
}
```

```
template <class V, class S, class R>
[[nodiscard]] TER
trustTransferLockedBalance(
    V& view,
    AccountID const& actingAccID,  // the account whose tx is actioning xfer
    S& sleSrcAcc,
    S& sleDstAcc,
    STAmount const& amount,  // issuer, currency are in this field
    int deltaLockCount,      // -1 decrement, +1 increment, 0 unchanged
    Rate const& lXferRate,   // locked transfer rate
    beast::Journal const& j,
    R dryRun)
{
    typedef typename std::conditional<
        std::is_same<V, ApplyView>::value && !dryRun,
        std::shared_ptr<SLE>,
        std::shared_ptr<SLE const>>::type SLEPtr;

    auto peek = [&](Keylet& k) {
        if constexpr (std::is_same<V, ApplyView>::value && !dryRun)
            return const_cast<ApplyView&>(view).peek(k);
        else if constexpr (std::is_same<V, Sandbox>::value)
            return const_cast<Sandbox&>(view).peek(k);
        else
            return view.read(k);
    };

    static_assert(
        std::is_same<V, ApplyView>::value || std::is_same<V, Sandbox>::value || dryRun,
        "trustTransferLockedBalance requires ApplyView or Sandbox"
    );

    if (!view.rules().enabled(featurePaychanAndEscrowForTokens))
        return tefINTERNAL;

    if (!sleSrcAcc || !sleDstAcc)
    {
        JLOG(j.warn()) << "trustTransferLockedBalance without sleSrc/sleDst";
        return tecINTERNAL;
    }

    if (amount <= beast::zero)
    {
        JLOG(j.warn()) << "trustTransferLockedBalance with non-positive amount";
        return tecINTERNAL;
    }

    auto const issuerAccID = amount.getIssuer();
    auto const currency = amount.getCurrency();
    auto const srcAccID = sleSrcAcc->getAccountID(sfAccount);
    auto const dstAccID = sleDstAcc->getAccountID(sfAccount);

    bool const srcHigh = srcAccID > issuerAccID;
    bool const dstHigh = dstAccID > issuerAccID;
    bool const srcIssuer = issuerAccID == srcAccID;
    bool const dstIssuer = issuerAccID == dstAccID;

    // check for freezing, auth, no ripple and TL sanity
    {
        TER const result = trustTransferAllowed(
            view, {srcAccID, dstAccID}, {currency, issuerAccID}, j);

        JLOG(j.trace())
            << "trustTransferLockedBalance: trustTransferAlowed result="
            << result;
        if (!isTesSuccess(result))
            return result;
    }

    // default dstAmount to amount
    auto dstAmt = amount;

    // if tx acct not source issuer or dest issuer
    // and xfer rate is not parity
    if ((!srcIssuer && !dstIssuer) && lXferRate != parityRate)
    {
        // compute transfer fee, if any
        auto const xferFee = amount.value() -
            divideRound(amount, lXferRate, amount.issue(), true);
        // compute balance to transfer
        dstAmt = amount.value() - xferFee;
    }
    // ensure source line exists
    Keylet klSrcLine{keylet::line(srcAccID, issuerAccID, currency)};
    SLEPtr sleSrcLine = peek(klSrcLine);

    // if source account is not issuer
    if (!srcIssuer)
    {
        // if source account has no trust line - fail
        if (!sleSrcLine)
            return tecNO_LINE;

        // can't transfer a locked balance that does not exist
        if (!sleSrcLine->isFieldPresent(sfLockedBalance) ||
            !sleSrcLine->isFieldPresent(sfLockCount))
        {
            JLOG(j.trace()) << "trustTransferLockedBalance could not find "
                               "sfLockedBalance/sfLockCount on source line";
            return tecINSUFFICIENT_FUNDS;
        }

        // decrement source balance
        {
            STAmount priorBalance = srcHigh ? -((*sleSrcLine)[sfBalance])
                                            : (*sleSrcLine)[sfBalance];

            STAmount priorLockedBalance = srcHigh
                ? -((*sleSrcLine)[sfLockedBalance])
                : (*sleSrcLine)[sfLockedBalance];

            uint32_t priorLockCount = (*sleSrcLine)[sfLockCount];

            // check they have sufficient funds
            if (amount > priorLockedBalance)
            {
                JLOG(j.trace())
                    << "trustTransferLockedBalance amount > lockedBalance: "
                    << "amount=" << amount
                    << " lockedBalance=" << priorLockedBalance;
                return tecINSUFFICIENT_FUNDS;
            }

            STAmount finalBalance = priorBalance - amount;

            STAmount finalLockedBalance = priorLockedBalance - amount;

            uint32_t finalLockCount = priorLockCount + deltaLockCount;

            // check if there is significant precision loss
            if (!isAddable(priorBalance, amount) ||
                !isAddable(priorLockedBalance, amount))
                return tecPRECISION_LOSS;

            // sanity check possible overflows on the lock counter
            if ((deltaLockCount > 0 && priorLockCount > finalLockCount) ||
                (deltaLockCount < 0 && priorLockCount < finalLockCount) ||
                (deltaLockCount == 0 && priorLockCount != finalLockCount))
                return tecOVERSIZE;

            // this should never happen but defensively check it here before
            // updating sle
            if (finalBalance < beast::zero || finalLockedBalance < beast::zero)
            {
                JLOG(j.warn()) << "trustTransferLockedBalance results in a "
                                  "negative balance on source line";
                return tecINTERNAL;
            }

            if constexpr (!dryRun)
            {
                sleSrcLine->setFieldAmount(
                    sfBalance, srcHigh ? -finalBalance : finalBalance);

                if (finalLockedBalance == beast::zero || finalLockCount == 0)
                {
                    sleSrcLine->makeFieldAbsent(sfLockedBalance);
                    sleSrcLine->makeFieldAbsent(sfLockCount);
                }
                else
                {
                    sleSrcLine->setFieldAmount(
                        sfLockedBalance,
                        srcHigh ? -finalLockedBalance : finalLockedBalance);
                    sleSrcLine->setFieldU32(sfLockCount, finalLockCount);
                }
            }
        }
    }

    // check for a destination line
    Keylet klDstLine = keylet::line(dstAccID, issuerAccID, currency);
    SLEPtr sleDstLine = peek(klDstLine);

    // if dest account is not issuer
    if (!dstIssuer)
    {
        // if dest acct has no trustline
        if (!sleDstLine)
        {
            // if tx acct is not dest acct and src acct is not dest acct
            if (actingAccID != dstAccID && srcAccID != dstAccID)
                return tecNO_LINE;

            STAmount dstBalanceDrops = sleDstAcc->getFieldAmount(sfBalance);

            // no dst line exists, we might be able to create one...
            if (std::uint32_t const ownerCount = {sleDstAcc->at(sfOwnerCount)};
                dstBalanceDrops < view.fees().accountReserve(ownerCount + 1))
                return tecNO_LINE_INSUF_RESERVE;

            // create destination trust line
            if constexpr (!dryRun)
            {
                // clang-format off
                if (TER const ter = trustCreate(
                        view,
                        !dstHigh,                       // is dest low?
                        issuerAccID,                    // source
                        dstAccID,                       // destination
                        klDstLine.key,                  // ledger index
                        sleDstAcc,                      // Account to add to
                        false,                          // authorize account
                        (sleDstAcc->getFlags() & lsfDefaultRipple) == 0,
                        false,                          // freeze trust line
                        dstAmt,                         // initial balance
                        Issue(currency, dstAccID),      // limit of zero
                        0,                              // quality in
                        0,                              // quality out
                        j);                             // journal
                    !isTesSuccess(ter))
                {
                    return ter;
                }
            }
            // clang-format on
        }
        else
        {
            // dest trust line does exist
            // checked NoRipple and Freeze flags in trustTransferAllowed

            // check the limit
            STAmount dstLimit = dstHigh ? (*sleDstLine)[sfHighLimit]
                                        : (*sleDstLine)[sfLowLimit];

            // get prior balance
            STAmount priorBalance = dstHigh ? -((*sleDstLine)[sfBalance])
                                            : (*sleDstLine)[sfBalance];

            // combine prior with dest amount for final
            STAmount finalBalance = priorBalance + dstAmt;

            // if final is less than prior - fail
            if (finalBalance < priorBalance)
            {
                JLOG(j.warn()) << "trustTransferLockedBalance resulted in a "
                                  "lower/equal final balance on dest line";
                return tecINTERNAL;
            }

            // if final is more than dest limit and tx acct is not dest acct -
            // fail
            if (finalBalance > dstLimit && actingAccID != dstAccID)
            {
                JLOG(j.trace())
                    << "trustTransferLockedBalance would increase dest "
                       "line above limit without permission";
                return tecPATH_DRY;
            }

            // if there is significant precision loss - fail
            if (!isAddable(priorBalance, dstAmt))
                return tecPRECISION_LOSS;

            // compute final balance to send - reverse sign for high dest
            finalBalance = dstHigh ? -finalBalance : finalBalance;

            // if not dry run - set dst line field
            if constexpr (!dryRun)
                sleDstLine->setFieldAmount(sfBalance, finalBalance);
        }
    }

    if constexpr (!dryRun)
    {
        static_assert(std::is_same<V, ApplyView>::value);

        // if source account is not issuer
        if (!srcIssuer)
        {
            // check if source line ended up in default state
            if (isTrustDefault(sleSrcAcc, sleSrcLine))
            {
                // adjust owner count
                uint32_t flags = sleSrcLine->getFieldU32(sfFlags);
                uint32_t fReserve{srcHigh ? lsfHighReserve : lsfLowReserve};
                if (flags & fReserve)
                {
                    sleSrcLine->setFieldU32(sfFlags, flags & ~fReserve);
                    adjustOwnerCount(view, sleSrcAcc, -1, j);
                    view.update(sleSrcAcc);
                }
            }
            // update source line
            view.update(sleSrcLine);
        }

        // if dest line exists
        if (sleDstLine)
            // update dest line
            view.update(sleDstLine);
    }
    return tesSUCCESS;
}
```
the above fails if I do sb instead of ctx_.view(). I want to use the sandbox view in the trustTransferLockedBalance function. 


"""
client = AthenahClient("id", "dist", "xahaud", "v1", "gpt-4.1")
response = client.promptv1(prompt)
print(response)
