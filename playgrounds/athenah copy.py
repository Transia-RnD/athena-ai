#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled", "v1")
# indexer.build_whitlist_from_dirs(
#     path,
#     ["include", "src/libxrpl", "src/xrpld", "src/test"],
# )

# from athenah_ai.bots.parse import AthenahPreparer

# preparer = AthenahPreparer("local", "id", "dist", "rippled", "v1")
# preparer.prepare_source_code(
#     ["include", "src/ripple", "src/libxrpl", "src/xrpld", "src/test"]
# )

path: str = "/Users/darkmatter/projects/transia/athena-ai/dist/rippled/rippled-source"
indexer = AthenahIndexer("local", "id", "dist", "rippled-ai", "v1")
indexer.build_whitlist_from_dirs(
    path,
    ["include/xrpl/basics"],
)

# from athenah_ai.mini.chat import main

from athenah_ai.client import AthenahClient

prompt: str = ""
client = AthenahClient("id", "dist", "rippled-ai")
response = client.prompt(prompt)
print(response)

# chatbot = main()

# from athenah_ai.mini.client import MiniAI

# categorical_features = [
#     "ip_address",
#     "timestamp",
#     "method",
#     "url",
#     "protocol",
#     "referer",
#     "user_agent",
#     # "api_calls",
# ]
# ai = MiniAI("local", "id", "dist", "access", "v1", categorical_features)
# df = ai.load_data()
# response = ai.build(df)
# import pandas as pd

# test_data = pd.DataFrame(
#     [
#         {
#             "ip_address": "172.70.54.90",
#             "timestamp": "08/Apr/2023:07:41:16 +0000",
#             "method": "POST",
#             "url": "/favicon.ico",
#             "protocol": "HTTP/1.1",
#             "status_code": 200,
#             "response_length": 588,
#             "referer": "-",
#             "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
#         }
#     ]
# )
# response = ai.invoke(test_data)
# print(response)


# print(response)

# from athenah_ai.client import AthenahClient

# prompt: str = """
# We need to implement

# """
# client = AthenahClient("id", "dist", "rippled")
# response = client.prompt(prompt)
# print(response)

# import os
# from entry_point_finder import EntryPointFinder

# # Specify the base directory of your project
# base_dir = "/path/to/your/project"

# # Specify the entry point file and line number
# # For example, if the entry point starts at line 10 in 'main.py' in the 'src' directory
# entry_file = os.path.join(base_dir, "src", "main.py")
# entry_line = 10  # Change this to the line number where the entry point starts

# # Initialize the EntryPointFinder with the specified entry file and line number
# finder = EntryPointFinder(
#     base_dir=base_dir, entry_file=entry_file, entry_line=entry_line
# )

# # Build the concatenated entry point file
# tmp_file = finder.build_concatenated_entry_point()
