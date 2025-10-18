#!/usr/bin/env python
# coding: utf-8

ATHENAH_CLIENT_NAME: str = "tatiana-ai"


def main():
    # from athenah_ai.indexer import AthenahIndexer

    # path: str = "/Users/darkmatter/projects/transia/amber-ai"
    # indexer = AthenahIndexer("local", "id", "dist", ATHENAH_CLIENT_NAME, "v1")
    # indexer.build_from_dirs(path, ["."], True, True)

    from athenah_ai.client import AthenahClient

    ai_source: AthenahClient = AthenahClient(
        "id",
        # provider="anthropic",
        provider="openai",
        # provider="xai",
        model_group="dist",
        custom_model=ATHENAH_CLIENT_NAME,
        version="v1",
        # model_name="claude-4-sonnet",
        model_name="gpt-4.1",
        # model_name="grok-4",
        temperature=0,
        best_of=5,
    )
    # get file content from file list
    content = ""
    file_list = [
        "/Users/darkmatter/projects/transia/amber-ai/consolidated_project.py",
    ]
    for file_path in file_list:
        with open(file_path, "r") as f:
            content += f.read() + "\n\n"
    system_prompt: str = f"""
{content}
"""
    user_input: str = """
I have an SField and data in the form of a slice. I need to add it to an existing STObject which will make a transaction. The SField can be any type like STAmount or STAccount

You MUST follow these rules:
- only return the valid code.
"""
    system_prompt = system_prompt + "\n" + user_input
    response = ai_source.agent_prompt("Developer", "Developer Coder", system_prompt)
    # write to a file
    with open("tatiana_ai.response.txt", "w") as f:
        f.write(response)


main()
