#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

path: str = "/Users/darkmatter/projects/ledger-works/jshooks-api"
indexer = AthenahIndexer("local", "id", "dist", "jshooks-api", "v1")
indexer.index_dir(path, ["."], "jshooks-api")

from athenah_ai.client import AthenahClient

client = AthenahClient("id", "dist", "jshooks-api")

prompt: str = """
Create documentation for the funds/modular/user.c hook. Be extremely detailed. Dont use code. The average person should be able to understand it. Mainly the operations Deposit, Withdraw, Debit Etc

```
Operations:

// payment ops are:
    // D - deposit (any)

// invoke ops are:
    // B - debit (settler)
    // W - withdraw (user)

// invoke (Asset) ops are:
    // C - create asset (integration) - Set TrustLine ~
    // D - delete asset (integration) - Set Trustline 0

// invoke (Withdraw) ops are:
    // A - Approval (user)
    // I - Intent (user)
    // E - Execution (user)
    // C - Cancel (user)
```
"""
response = client.prompt(prompt)
print(response)
