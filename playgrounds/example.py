#!/usr/bin/env python
# coding: utf-8

from typing import List

from athenah_ai.indexer import AthenahIndexer
from athenah_ai.client import AthenahClient


def index_dirs():
    source_dir: str = "/Users/darkmatter/projects/transia/athena-ai/tests/fixtures"
    indexer = AthenahIndexer("local", "id", "dist", "test-dirs", "v1")
    indexer.build_from_dirs(source_dir, ["subfixture"], False)


def index_dirs_with_root():
    source_dir: str = "/Users/darkmatter/projects/transia/athena-ai/tests/fixtures"
    indexer = AthenahIndexer("local", "id", "dist", "test-dirs-root", "v1")
    indexer.build_from_dirs(source_dir, ["subfixture"], True)


def index_dir():
    source_dir: str = "/Users/darkmatter/projects/transia/athena-ai/tests/fixtures"
    indexer = AthenahIndexer("local", "id", "dist", "test-dir", "v1")
    indexer.build_from_dir(
        source_dir,
    )


def index_files():
    file_paths: List[str] = [
        "/Users/darkmatter/projects/transia/athena-ai/tests/fixtures/BuildInfo.cpp",
        "/Users/darkmatter/projects/transia/athena-ai/tests/fixtures/subfixture/RCLConsensus.cpp",
    ]
    indexer = AthenahIndexer("local", "id", "dist", "test-files", "v1")
    indexer.build_from_files(
        file_paths,
    )


def index_file():
    file_path: str = (
        "/Users/darkmatter/projects/transia/athena-ai/tests/fixtures/BuildInfo.cpp"
    )
    indexer = AthenahIndexer("local", "id", "dist", "test-file", "v1")
    indexer.build_from_file(
        file_path,
    )


# index_dirs()
index_dirs_with_root()
# index_dir()
# index_files()
# index_file()
# prompt: str = "What is this?"
# client = AthenahClient("id", "dist", "test")
# response = client.promptv1(prompt)
# print(response)
