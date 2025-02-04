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
Expected<void, std::string>
STTx::checkMultiSign(
    RequireFullyCanonicalSig requireCanonicalSig,
    Rules const& rules) const
{
    bool const fullyCanonical = (getFlags() & tfFullyCanonicalSig) ||
        (requireCanonicalSig == RequireFullyCanonicalSig::yes);

    // We can ease the computational load inside the loop a bit by
    // pre-constructing part of the data that we hash.  Fill a Serializer
    // with the stuff that stays constant from signature to signature.
    Serializer dataStart = startMultiSigningData(*this);
    return multiSignHelper(
        *this,
        fullyCanonical,
        [&dataStart](
            AccountID const& accountID) mutable -> std::vector<uint8_t> {
            Serializer s = dataStart;
            finishMultiSigningData(accountID, s);
            return s.getData();
        },
        rules);
}
```

Should this use a shared_ptr?

"""
client = AthenahClient("id", "dist", "rippled")
response = client.promptv1(prompt)
print(response)
