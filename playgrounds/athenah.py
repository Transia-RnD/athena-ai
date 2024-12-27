#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-test", "v1")
# indexer.build_whitlist_from_dirs(
#     path,
#     ["include/xrpl/basics"],
# )

# path: str = "/Users/darkmatter/projects/transia/athena-ai/dist/rippled/rippled-source"
# indexer = AthenahIndexer("local", "id", "dist", "rippled-ai", "v1")
# indexer.build_whitlist_from_dirs(
#     path,
#     ["include/xrpl/basics"],
# )

# from athenah_ai.client import AthenahClient

# prompt: str = "What is the generalized_set_intersection function?"

# old_client = AthenahClient("id", "dist", "rippled-ai-test")
# old_response = old_client.prompt(prompt)
# print(old_response)

# new_client = AthenahClient("id", "dist", "rippled-ai")
# new_response = new_client.prompt(prompt)
# print(new_response)

from athenah_ai.mini.chat import main

main()
