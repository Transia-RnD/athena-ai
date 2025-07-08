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
        provider="anthropic",
        model_group="dist",
        custom_model=ATHENAH_CLIENT_NAME,
        version="v1",
        model_name=AGENT_MODEL,
        best_of=3,
    )
    system_prompt: str = """
Create a workshop lesson plan based on the following system prompt:

```
🧪 Lab 1: Setup rippled build to be a validator. Create keys, add token and sync.(Discarded validations. Listen to the validation stream.)
```
"""
    response = ai_source.agent_prompt(
        "Workshop Creator",
        "Create a workshop lesson plan based on the provided system prompt.",
        system_prompt,
    )
    print(response)
    # write to a file
    with open("response.txt", "w") as f:
        f.write(response)


main()
