#!/usr/bin/env python
# coding: utf-8

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-core", "v1")
# indexer.build_from_dirs(
#     path,
#     ["include", "src/libxrpl", "src/xrpld"],
#     False,
# )

from athenah_ai.coder.labelerV1 import AICodeLabelerV1

labeler = AICodeLabelerV1("local", "id", "dist", "rippled-ai-core", "v1")
labeler.process_directories(["include", "src/libxrpl", "src/xrpld"])
# labeler.prepare_source_code(["include", "src/libxrpl", "src/xrpld"])
