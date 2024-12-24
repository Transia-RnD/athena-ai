#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/broker-hooks"
# indexer = AthenahIndexer("local", "id", "dist", "broker-hooks", "v1")
# indexer.index_whitelist(
#     path,
#     ["."],
#     "broker-hooks",
# )

from athenah_ai.client import AthenahClient

prompt: str = """
Create a README.md for the context. Explain to the user how to use the repo. 
"""
client = AthenahClient("id", "dist", "broker-hooks")
response = client.promptv1(prompt)
print(response)
