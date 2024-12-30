#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer
from athenah_ai.client import AthenahClient

path: str = "/Users/darkmatter/projects/transia/athena-ai/dist/rippled/rippled-source"
indexer = AthenahIndexer("local", "id", "dist", "rippled", "v1")
indexer.build_whitlist_from_dirs(
    path,
    ["include/xrpl/basics"],
)


prompt: str = "What is this?"
client = AthenahClient("id", "dist", "rippled")
response = client.prompt(prompt)
print(response)
