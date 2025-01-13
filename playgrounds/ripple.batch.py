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

system_prompt: str = """
```
const STVector256&
STTx::getBatchTransactionIDs() const
{
    static STVector256 transactionIDs;
    transactionIDs.clear();
    for (STObject const& rb : getFieldArray(sfRawTransactions))
    {
        transactionIDs.push_back(STTx{rb}.getTransactionID());
    }
    return transactionIDs;
}
```
"""

prompt: str = """

```
const STVector256&
STTx::getBatchTransactionIDs() const
{
    static STVector256 transactionIDs;
    transactionIDs.clear();
    for (STObject rb : getFieldArray(sfRawTransactions))
    {
        transactionIDs.push_back(STTx{std::move(rb)}.getTransactionID());
    }
    return transactionIDs;
}
```

What does std::move do in the code above? Is it necessary? Is it safe to remove it?

"""
client = AthenahClient("id", "dist", "rippled")
response = client.prompt(prompt)
print(response)
