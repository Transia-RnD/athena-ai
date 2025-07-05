#!/usr/bin/env python
# coding: utf-8


def process_core():
    from athenah_ai.indexer import AthenahIndexer

    path: str = "/root/athena-ai/dist/rippled-ai-core"
    indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-core", "v1")
    indexer.build_from_dirs(path, ["include", "src/libxrpl", "src/xrpld"], False, False)


# def process_tests():
#     from athenah_ai.indexer import AthenahIndexer

#     path: str = "/root/athena-ai/dist/rippled-ai-core"
#     indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-tests", "v1")
#     indexer.build_from_dirs(
#         path,
#         ["src/test"],
#         False,
#         False
#     )


process_core()
# process_tests()
