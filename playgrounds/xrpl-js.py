#!/usr/bin/env python
# coding: utf-8

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/xrpl.js"
# indexer = AthenahIndexer("local", "id", "dist", "xrpl-js", "v1")
# indexer.index_dir(
#     path,
#     [
#         "packages/xrpl/src",
#         "packages/ripple-binary-codec/src",
#         "packages/ripple-address-codec/src",
#         "packages/ripple-keypairs/src",
#     ],
#     "xrpl-js",
# )

from athenah_ai.client import AthenahClient

prompt: str = """
If I wanted to create an AMMPool and I need to immediately freeze the pool, how would I do that?

"""
client = AthenahClient("id", "dist", "xrpl-js")
response = client.prompt(prompt)
print(response)
