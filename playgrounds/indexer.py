#!/usr/bin/env python
# coding: utf-8


def process_core():
    from athenah_ai.indexer import AthenahIndexer

    path: str = "/Users/darkmatter/projects/ledger-works/rippled"
    indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-core", "v1")
    indexer.build_from_dirs(
        path,
        ["include", "src/libxrpl", "src/xrpld"],
        False,
    )


def process_tests():
    from athenah_ai.indexer import AthenahIndexer

    path: str = "/Users/darkmatter/projects/ledger-works/rippled"
    indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-tests", "v1")
    indexer.build_from_dirs(
        path,
        ["src/test"],
        False,
    )


process_core()
# process_tests()
