#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/xahaud"
# indexer = AthenahIndexer("local", "id", "dist", "xahaud", "v1")
# indexer.index_dir(path, ["src/ripple", "src/test"], "xahaud")

from athenah_ai.client import AthenahClient

client = AthenahClient("id", "dist", "xahaud")

prompt: str = """
I want to change how the logging is done. I want to log based on the date and time. Or rather I want to create a new log for every hour. Find out where the log file is created and then update the code to create a new log file every hour.

The logging is done with Journal.h.

"""
response = client.prompt(prompt)
print(response)
