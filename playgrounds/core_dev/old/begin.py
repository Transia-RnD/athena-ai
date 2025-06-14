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

import os
import json
from athenah_ai.client import AthenahClient


def collect_ai_v1_descriptions(root_folder):
    results = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".ai.v1.json"):
                full_path = os.path.join(dirpath, filename)
                try:
                    with open(full_path, "r") as f:
                        data = json.load(f)
                        # Get the file_path and description from the JSON
                        file_path = data.get("file_path", full_path)
                        description = data.get("description", "")
                        results.append({"file": file_path, "description": description})
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")
    return results


# Do a collect ai v1 for a list of files
def collect_ai_v1_for_files(files):
    results = []
    for file in files:
        try:
            with open(file, "r") as f:
                data = json.load(f)
                # Get the file_path and description from the JSON
                file_path = data.get("file_path", file)
                description = data.get("description", "")
                results.append({"file": file_path, "description": description})
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return results


# gather the contents of files from a list of files, the files will not be json but txt files
def collect_ai_v1_contents(files):
    results = []
    for file in files:
        try:
            with open(file, "r") as f:
                content = f.read()
                results.append({"file": file, "content": content})
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return results


# if __name__ == "__main__":
#     # Change this to your folder
#     folder = "protocol"
#     # combined = collect_ai_v1_descriptions(
#     #     "/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/include/xrpl/protocol"
#     # )
#     final = collect_ai_v1_descriptions(
#         "/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/src/libxrpl/protocol"
#     )
#     prompt = f"""
#     The following files are part of the XRPL (XRP Ledger) core library. Each file contains specific functionality related to the XRP Ledger, including transaction processing, account management, and network operations. The descriptions below provide an overview of each file's purpose and functionality. Format the response in a markdown file with structured sections for each file. If there is no major functionality in the header file, do not include it in the response.

#     Our goal is to create documentation for the XRPL core library, specifically focusing on the files in the {folder} folder. The descriptions should be concise and informative, highlighting the key functionalities of each file.

#     We do not want to just list the files but rather provide a written version of what the code does, similar to a documentation file. The descriptions should be clear and easy to understand, suitable for developers who are new to the XRPL core library.

#     Create a structure so that we can use it as a template for other folders that we will run the same function on.
#     """
#     for entry in final:
#         prompt += f"\nFile: {entry['file']}\nDescription: {entry['description']}\n"
#     # Initialize the Athenah client with the appropriate parameters
#     client = AthenahClient("id", "dist", "rippled-ai-core", "v1", "gpt-4.1")
#     response = client.promptv1(prompt)
#     print(response)
#     # save the response to a file
#     with open("xrpl_core_docs.md", "w") as f:
#         f.write(response)


# read the file and print the contents
def revise_content(topic: str, revision: int, ai_v1: str):
    with open("xrpl_core_docs.md", "r") as f:
        content = f.read()
    print(content)
    prompt = f"""
    I want to update the Feature Management section. We should review the files in the /Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/include/xrpl/protocol/detail folder. 

    Lets explain how features are added. The difference between a features and a fix.

    Then explain the transactins.macro file and how it is used. Then the ledger entries and sfields file. 

    Return the full content of the Feature Management section, including the new information about features, fixes, and the specific files mentioned.
    """

    client = AthenahClient("id", "dist", "rippled-ai-core", "v1", "gpt-4.1")
    response = client.rag_prompt_v2(content, prompt)
    with open(f"{topic}_{revision}.md", "w") as f:
        f.write(response)


if __name__ == "__main__":
    # Example usage
    topic = "protocol"
    revision = 1
    combined = collect_ai_v1_descriptions(
        "/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/include/xrpl/protocol"
    )
    final = combined + collect_ai_v1_descriptions(
        "/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/src/libxrpl/protocol"
    )
    prompt = ""
    for entry in final:
        prompt += f"\nFile: {entry['file']}\nDescription: {entry['description']}\n"
    revise_content(topic, revision, final)
    print(f"Revised content saved to {topic}_{revision}.md")
