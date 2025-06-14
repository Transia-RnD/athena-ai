import os
import ast
from typing import Any, List, Dict

from athenah_ai.client import AthenahClient
from playgrounds.core_dev.utils import collect_ai_v1_descriptions
from athenah_ai.utils.fs import read_file, write_file
from playgrounds.core_dev.tools import map_and_classify_symbols

# === CONFIGURATION ===
PROJECT_ROOT = "/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source"
DETAIL_PATH = f"{PROJECT_ROOT}/src/xrpld/app/tx/detail"
TEMPLATE_PATH = (
    "/Users/darkmatter/projects/transia/athena-ai/playgrounds/core_dev/template.md"
)
PRE_PATH = "/Users/darkmatter/projects/transia/athena-ai/playgrounds/core_dev/pre"
RESULTS_DIR = (
    "/Users/darkmatter/projects/transia/athena-ai/playgrounds/core_dev/results"
)
FUNCTIONALITY = "Transactors"
AGENT_MODEL = "gpt-4.1"
REVISION_ROUNDS = 3


def get_athenah_client():
    """Initialize and return an AthenahClient."""
    return AthenahClient("id", "dist", "rippled-ai-core", "v1", AGENT_MODEL)


def gather_symbol_and_description(symbol: str, project_root: str):
    """Collect symbol locations and AI descriptions."""
    athenah = AthenahClient("id", "dist")
    athenah.init_llm()
    symbol_map = map_and_classify_symbols(symbol, project_root, athenah.llm)
    descriptions = collect_ai_v1_descriptions(DETAIL_PATH)
    return symbol_map, descriptions


def filter_relevant_symbols(
    client: AthenahClient, symbol_map: Any, descriptions: Any, pre_info: str
):
    """Use an agent to filter relevant symbol locations."""
    desc_list = "\n".join(
        [f"File: {d['file']}\nDescription: {d['description']}" for d in descriptions]
    )

    prompt = f"""
You are a code documentation assistant. Your job is to identify which symbol locations are most relevant to the functionality described. 
You must only use the symbol map, descriptions, and pre-existing information provided. Do not invent or assume anything not present.

Symbol Map:
{symbol_map}

Descriptions:
{desc_list}

Pre-existing information:
{pre_info}

Return a list of relevant file paths and a brief justification for each.
"""
    response = client.agent_prompt(
        "Relevance Classifier",
        "Classify which symbol locations are most relevant to the functionality.",
        prompt,
    )
    return response


def extract_function_code(file_path: str, function_name: str) -> str:
    """Extract the source code of a function from a file (Python version)."""
    # For C++ or other languages, you may need a different parser or regex.
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    with open(file_path, "r") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                start_line = node.lineno - 1
                end_line = node.end_lineno
                return "\n".join(source.splitlines()[start_line:end_line])
    except Exception:
        # For non-Python code, fallback to a simple grep-like extraction
        lines = source.splitlines()
        in_func = False
        func_lines = []
        for line in lines:
            if function_name in line and ("{" in line or ":" in line):
                in_func = True
            if in_func:
                func_lines.append(line)
                if "}" in line:
                    break
        return (
            "\n".join(func_lines)
            if func_lines
            else f"Function {function_name} not found."
        )
    return f"Function {function_name} not found."


def parse_process_map(
    client, relevant_info: str, question: str
) -> List[Dict[str, str]]:
    """Ask the agent to create a process map (list of steps with file and function names)."""
    prompt = f"""
You are a code process mapper. Your job is to create a JSON list of the process flow for the functionality described below.
For each step, include the file path and the exact function name, in the order they are called.
Do not invent or assume any steps not present in the provided information.

Question:
{question}

Relevant Information:
{relevant_info}

Return a JSON list like:
[
  {{"file": "path/to/file.cpp", "function": "FunctionName"}},
  ...
]
"""
    response = client.agent_prompt(
        "Process Mapper",
        "Create a JSON process map of the code flow.",
        prompt,
    )
    # Try to parse the response as JSON
    import json

    try:
        process_map = json.loads(response)
    except Exception:
        process_map = []
    return process_map


def step_through_code(
    client, process_map: List[Dict[str, str]], relevant_info: str
) -> List[Dict[str, str]]:
    """For each function in the process map, extract its code and ask the agent to explain it."""
    explanations = []
    for step in process_map:
        file_path = step["file"]
        function_name = step["function"]
        code = extract_function_code(file_path, function_name)
        prompt = f"""
You are a code explainer. ONLY use the code below and the provided context. Do not invent or assume anything not present.

Function: {function_name}
File: {file_path}

Code:
{code}

Relevant context:
{relevant_info}

Explain what this function does, step by step, in plain language. If the code is missing or incomplete, say so.
"""
        explanation = client.agent_prompt(
            "Code Explainer",
            f"Explain {function_name} using only the code provided.",
            prompt,
        )
        explanations.append(
            {
                "function": function_name,
                "file": file_path,
                "explanation": explanation,
                "code": code,
            }
        )
    return explanations


def generate_documentation(client, template, step_explanations, relevant_info):
    """Generate documentation using the agent and a template, grounded in code explanations."""
    steps_md = ""
    for step in step_explanations:
        steps_md += f"### {step['function']} ({step['file']})\n\n"
        steps_md += f"```cpp\n{step['code']}\n```\n\n"
        steps_md += f"{step['explanation']}\n\n"

    prompt = f"""
You are a technical writer. ONLY use the code explanations and information provided. Do not invent or assume anything not present.

Our goal is to create documentation for the XRPL source code, specifically focusing on the {FUNCTIONALITY} functionality. 
We will use this template to break down the functionality into its components and describe how they work together.

Template: 
{template}

Code Explanations:
{steps_md}

Relevant Information:
{relevant_info}
"""
    return client.agent_prompt(
        "Source Code Teacher",
        "Teach the functionality of the XRPL source code in a structured way, using the provided template. The goal is to break down the functionality into its components and describe how they work together.",
        prompt,
    )


def revision_loop(client, initial_doc, relevant_info, template, rounds=3):
    """Iteratively ask the agent to check for missing information and revise the documentation."""
    doc = initial_doc
    for i in range(rounds):
        # 1. Ask if anything is missing
        missing_prompt = f"""
You are a documentation reviewer. ONLY use the documentation and information provided. Do not invent or assume anything not present.

Here is the current documentation draft:

{doc}

Is there anything missing or unclear in the above documentation? Use the following relevant information to help you decide:

{relevant_info}
"""
        missing_response = client.agent_prompt(
            "Documentation Reviewer",
            "Review the documentation and identify missing or unclear parts.",
            missing_prompt,
        )
        # 2. Ask to revise/update
        revise_prompt = f"""
You are a documentation reviser. ONLY use the documentation, feedback, and information provided. Do not invent or assume anything not present.

Here is the current documentation draft:

{doc}

Here is the feedback on what is missing or unclear:

{missing_response}

Please revise and update the documentation using the template below, making sure to address the feedback:

Template:
{template}

Relevant Information:
{relevant_info}
"""
        doc = client.agent_prompt(
            "Documentation Reviser",
            "Revise and update the documentation based on feedback.",
            revise_prompt,
        )
    return doc


def fact_check_documentation(client, doc, step_explanations):
    """Ask the agent to fact-check the documentation against the code explanations."""
    steps_md = ""
    for step in step_explanations:
        steps_md += f"### {step['function']} ({step['file']})\n\n"
        steps_md += f"{step['explanation']}\n\n"

    prompt = f"""
You are a fact-checker. ONLY use the code explanations provided. Do not invent or assume anything not present.

Here is the documentation draft:
{doc}

Here are the code explanations:
{steps_md}

Does every statement in the documentation have direct support in the code explanations? 
If not, point out the unsupported statements. If everything is supported, say "All statements are supported."
"""
    return client.agent_prompt(
        "Documentation Fact-Checker",
        "Fact-check the documentation against the code explanations.",
        prompt,
    )


def main():
    client = get_athenah_client()
    symbol_map, descriptions = gather_symbol_and_description(
        FUNCTIONALITY, PROJECT_ROOT
    )
    pre_info = read_file(PRE_PATH + "/" + FUNCTIONALITY + ".md")
    relevant_response = filter_relevant_symbols(
        client, symbol_map, descriptions, pre_info
    )

    # Step 1: Create process map (list of steps with file/function)
    question = (
        "When a transaction is submitted to the XRPL, it is processed by the Transactor class. "
        "What is the full process? Create a json map of the process. Use exact function names in the exact order. "
        "For each function, step into the function and describe it in an agnostic way."
    )
    process_map = parse_process_map(client, relevant_response, question)

    # Step 2: For each function, extract code and explain
    step_explanations = step_through_code(client, process_map, relevant_response)

    # Step 3: Read template
    template = read_file(TEMPLATE_PATH)

    # Step 4: Generate initial documentation
    initial_doc = generate_documentation(
        client, template, step_explanations, relevant_response
    )

    # Step 5: Revision loop
    final_doc = revision_loop(
        client, initial_doc, relevant_response, template, rounds=REVISION_ROUNDS
    )

    # Step 6: Fact-check
    fact_check = fact_check_documentation(client, final_doc, step_explanations)
    print("Fact-check result:\n", fact_check)

    # Step 7: Write to file
    output_path = f"{RESULTS_DIR}/{FUNCTIONALITY}.md"
    write_file(output_path, final_doc)
    print(f"Comprehensive documentation written to {output_path}")


if __name__ == "__main__":
    main()
