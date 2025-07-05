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
Sui's Relaying Process (Narwhal/Bullshark)
What Gets Relayed:

Transaction data (the raw transaction)
Cryptographic certificates (validity proofs)
Dependency information (object references)
Early validation results (but not full execution)

Early Checks During Relaying:

Signature validation
Object existence checks
Basic format validation
Dependency analysis (which objects are touched)
Gas estimation

What's Deferred:

Full state execution
Complex computation
Final state changes
Cross-object interactions
"""
    user_input: str = """
I want to update the transaction relay process for the XRPL to use the sui ideas. Transaction relay happens in app.overlay().relay but is called I believe by TxQ. We want to change it from applying the transaction to only doing preflight and preclaim.

- Only return the code changes.
"""
    response = ai_source.rag_prompt_v2(system_prompt, user_input)
    print(response)
    # write to a file
    with open("response.txt", "w") as f:
        f.write(response)


main()
