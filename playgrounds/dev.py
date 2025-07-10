#!/usr/bin/env python
# coding: utf-8

AGENT_MODEL = "claude-4-sonnet-20250514"
ATHENAH_CLIENT_NAME: str = "rippled-ai-core"


def main():
    # from athenah_ai.indexer import AthenahIndexer

    # path: str = "/Users/darkmatter/projects/ledger-works/rippled"
    # indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-core", "v1")
    # indexer.build_from_dirs(path, ["include", "src/libxrpl", "src/xrpld"], False, False)

    from athenah_ai.client import AthenahClient

    ai_source: AthenahClient = AthenahClient(
        "id",
        # provider="anthropic",
        provider="openai",
        model_group="dist",
        custom_model=ATHENAH_CLIENT_NAME,
        version="v1",
        # model_name="claude-4-sonnet-20250514",
        model_name="o3-mini",
        temperature=1,
        best_of=3,
    )
    system_prompt: str = """
"""
    user_input: str = """
"""
    response = ai_source.rag_prompt_v2(system_prompt, user_input)
    print(response)
    # write to a file
    with open("response.txt", "w") as f:
        f.write(response)


main()
