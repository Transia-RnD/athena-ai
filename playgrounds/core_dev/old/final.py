#!/usr/bin/env python
# coding: utf-8

from athenah_ai.client import AthenahClient


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


# Initialize the Athenah client
client = AthenahClient("id", "dist", "rippled-ai-core", "v1", "gpt-4.1")
# Read the system prompt and user prompt from files
system = read_file(
    "/Users/darkmatter/projects/transia/athena-ai/playgrounds/core_dev/final.md"
)
prompt: str = f"""
Reformat the following markdown content. For the different STTypes give an example. Return the entire XRPL Protocol Feature and Object Management. Also include in the examples the getters and setters with getUInt32, etc.
"""

response = client.rag_prompt_v2(system, prompt)
# Save the response to a file
with open(
    "/Users/darkmatter/projects/transia/athena-ai/playgrounds/core_dev/final_response.md",
    "w",
) as file:
    file.write(response)
