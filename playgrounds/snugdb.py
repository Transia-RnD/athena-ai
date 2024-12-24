#!/usr/bin/env python
# coding: utf-8
from athenah_ai.indexer import AthenahIndexer

path: str = "/Users/darkmatter/projects/ledger-works/snugdb"
indexer = AthenahIndexer("local", "id", "dist", "snugdb", "v1")
indexer.index_dir(path, ["."], "snugdb")

from athenah_ai.client import AthenahClient

client = AthenahClient("id", "dist", "snugdb")

prompt: str = """
Write a test to test the `write_big_entry_internal` function. This is only called within the write_entry_internal which is called from the write_entry. To test this I beleive we need to first call the write_entry with less than 984 bytes then more than that.

"""
response = client.prompt(prompt)
print(response)
