#!/usr/bin/env python
# coding: utf-8

from typing import List

from athenah_ai.indexer import AthenahIndexer
from athenah_ai.client import AthenahClient


source_dir: str = "/Users/darkmatter/projects/ledger-works/binary-models-ts"
indexer = AthenahIndexer("local", "id", "dist", "binary-models-ts", "v1")
indexer.build_from_dirs(source_dir, ["."], True)

prompt: str = (
    "I want to update this to allow me to create BaseModels where all of the numberal values are little endian. I've already update all of the hexTo and uintFrom to include the flip. What I need to do now is be able to create a BaseModel in either BE or LE"
)
client = AthenahClient("id", "dist", "binary-models-ts")
response = client.promptv1(prompt)
print(response)
