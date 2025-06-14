#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

path: str = "/Users/darkmatter/projects/ledger-works/rippled"
indexer = AthenahIndexer("local", "id", "dist", "rippled-smart", "v1")
indexer.build_from_dirs(
    path,
    ["include", "src/libxrpl", "src/test", "src/xrpld"],
    True,
)


from athenah_ai.client import AthenahClient

prompt: str = """

I want to add the beast::Journal to the WasmEngine and WamrEngine. Show me the code implemenation for this.

"""
client = AthenahClient("id", "dist", "rippled-smart")
response = client.promptv1(prompt)
print(response)
