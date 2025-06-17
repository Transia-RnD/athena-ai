#!/usr/bin/env python
# coding: utf-8


def process_core():
    from athenah_ai.labeler.labeler import AICodeLabeler

    labeler = AICodeLabeler("local", "id", "dist", "rippled-ai-core", "v1")
    labeler.process_directories(["include", "src/libxrpl", "src/xrpld"])



def process_tests():
    from athenah_ai.labeler.labeler import AICodeLabeler

    labeler = AICodeLabeler("local", "id", "dist", "rippled-ai-tests", "v1")
    labeler.process_directories(["src/test"])


process_core()
process_tests()
