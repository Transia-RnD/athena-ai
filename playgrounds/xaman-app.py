#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer
from athenah_ai.client import AthenahClient

# path: str = "/Users/darkmatter/projects/ledger-works/Xaman-App"
# indexer = AthenahIndexer("local", "id", "dist", "xaman", "v1")
# indexer.index_whitelist(path, ["src", "typings"], "xaman", include_root=True)


prompt: str = (
    "How do I add tests to this react-native project? I want to test the VaultOverlay. Create a test file for the VaultOverlay screen. Use typescript."
)
client = AthenahClient("id", "dist", "xaman")
response = client.promptv1(prompt)
print(response)
