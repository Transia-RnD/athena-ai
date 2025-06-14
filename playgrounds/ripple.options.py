#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

path: str = "/Users/darkmatter/projects/ledger-works/rippled"
indexer = AthenahIndexer("local", "id", "dist", "rippled-options", "v1")
indexer.build_from_dirs(
    path,
    ["include", "src/libxrpl", "src/test", "src/xrpld"],
    True,
)

from athenah_ai.client import AthenahClient

prompt: str = """
```
//------------------------------------------------------------------------------
/*
    This file is part of rippled: https://github.com/ripple/rippled
    Copyright (c) 2025 Ripple Labs Inc.

    Permission to use, copy, modify, and/or distribute this software for any
    purpose  with  or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE  SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH  REGARD  TO  THIS  SOFTWARE  INCLUDING  ALL  IMPLIED  WARRANTIES  OF
    MERCHANTABILITY  AND  FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY  SPECIAL ,  DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER  RESULTING  FROM  LOSS  OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION  OF  CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
*/
//==============================================================================

#include <xrpld/app/tx/detail/OptionDelete.h>
#include <xrpld/ledger/Sandbox.h>
#include <xrpld/ledger/View.h>

#include <xrpl/basics/Log.h>
#include <xrpl/protocol/Feature.h>
#include <xrpl/protocol/TxFlags.h>

namespace ripple {

NotTEC
OptionDelete::preflight(PreflightContext const& ctx)
{
    if (!ctx.rules.enabled(featureOptions))
        return temDISABLED;

    if (auto const ret = preflight1(ctx); !isTesSuccess(ret))
        return ret;

    if (ctx.tx.getFlags() & tfUniversalMask)
    {
        JLOG(ctx.j.trace()) << "Malformed transaction: Invalid flags set.";
        return temINVALID_FLAG;
    }
    return preflight2(ctx);
}

TER
OptionDelete::preclaim(PreclaimContext const& ctx)
{
    return tesSUCCESS;
}

TER
OptionDelete::doApply()
{
    Sandbox sb(&ctx_.view());

    auto const optionID = ctx_.tx[sfOptionID];
    auto const optionSle = sb.peek({ltOPTION, optionID});
    if (!optionSle)
    {
        JLOG(j_.trace()) << "OptionDelete: Option list not found.";
        return tecNO_ENTRY;
    }

    Asset const asset = optionSle->getFieldIssue(sfAsset).value();
    Issue const issue = asset.get<Issue>();
    STAmount const strikePrice = optionSle->getFieldAmount(sfStrikePrice);
    std::int64_t const strike = strikePrice.mantissa();
    std::uint32_t const expiration = optionSle->getFieldU32(sfExpiration);

    // Delete all the options in the list dir
    // Define a callback function to handle each item in the directory
    auto callback = [&](uint256 const& item) {
        // Here you can add logic to handle each item before deletion
        JLOG(j_.error()) << "Deleting item: " << to_string(item);
    };

    // Use dirDelete to delete the directory
    if (!sb.dirDelete(keylet::optionBook(issue.account, issue.currency, strike, expiration), callback))
    {
        JLOG(j_.error()) << "Failed to delete option list directory.";
        return tefBAD_LEDGER;
    }

    // Now delete the option from issuer's owner dir
    if (!sb.dirRemove(
            keylet::ownerDir(issue.account),
            optionSle->at(sfOwnerNode),
            optionSle->key(),
            false))
    {
        JLOG(j_.error()) << "Failed to delete option from owner directory.";
        return tefBAD_LEDGER;
    }

    sb.erase(optionSle);
    sb.apply(ctx_.rawView());
    return tesSUCCESS;
}

}  // namespace ripple

```

Im getting the tefBAD_LEDGER when doing sb.dirDelete. What is wrong?

"""
client = AthenahClient("id", "dist", "rippled-options")
response = client.promptv1(prompt)
print(response)
