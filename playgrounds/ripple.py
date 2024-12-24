#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled", "v1")
# indexer.index_whitelist(
#     path,
#     ["include", "src/libxrpl", "src/test", "src/xrpld"],
#     "rippled",
# )

from athenah_ai.client import AthenahClient

prompt: str = """
```
Keylet const acctKeylet = keylet::account(acctID);
    if (auto const acct = view.read(acctKeylet);
        priorBalance < view.fees().accountReserve((*acct)[sfOwnerCount] + 1))
        return tecINSUFFICIENT_RESERVE;

    auto const offerID = keylet::nftoffer(acctID, seqProxy.value());

    // Create the offer:
    {
        // Token offers are always added to the owner's owner directory:
        auto const ownerNode = view.dirInsert(
            keylet::ownerDir(acctID), offerID, describeOwnerDir(acctID));

        if (!ownerNode)
            return tecDIR_FULL;

        bool const isSellOffer = txFlags & tfSellNFToken;

        // Token offers are also added to the token's buy or sell offer
        // directory
        auto const offerNode = view.dirInsert(
            isSellOffer ? keylet::nft_sells(nftokenID)
                        : keylet::nft_buys(nftokenID),
            offerID,
            [&nftokenID, isSellOffer](std::shared_ptr<SLE> const& sle) {
                (*sle)[sfFlags] =
                    isSellOffer ? lsfNFTokenSellOffers : lsfNFTokenBuyOffers;
                (*sle)[sfNFTokenID] = nftokenID;
            });

        if (!offerNode)
            return tecDIR_FULL;

        std::uint32_t sleFlags = 0;

        if (isSellOffer)
            sleFlags |= lsfSellNFToken;

        auto offer = std::make_shared<SLE>(offerID);
        (*offer)[sfOwner] = acctID;
        (*offer)[sfNFTokenID] = nftokenID;
        (*offer)[sfAmount] = amount;
        (*offer)[sfFlags] = sleFlags;
        (*offer)[sfOwnerNode] = *ownerNode;
        (*offer)[sfNFTokenOfferNode] = *offerNode;

        if (expiration)
            (*offer)[sfExpiration] = *expiration;

        if (dest)
            (*offer)[sfDestination] = *dest;

        view.insert(offer);
    }

    // Update owner count.
    adjustOwnerCount(view, view.peek(acctKeylet), 1, j);

    return tesSUCCESS;
```

The above code adds the nftoken offer to 3 directories. The owners directory, and either the buy or sell directory. 

In hooks, we are limited on namespaces (directories) so the how can I do the above in a c hook (smart contract)? 


"""
client = AthenahClient("id", "dist", "rippled")
response = client.promptv1(prompt)
print(response)
