import os
import ast
import time
from typing import Any, List, Dict

from athenah_ai.client import AthenahClient
from playgrounds.core_dev.utils import get_ai_v1_json
from athenah_ai.utils.fs import read_file, write_file, read_json, write_json
from athenah_ai.utils.response import safe_json_loads
from playgrounds.core_dev.tools import symbol_to_source_occurances

# === CONFIGURATION ===
ATHENAH_ROOT = "/Users/darkmatter/projects/transia/athena-ai"
PROJECT_ROOT = f"{ATHENAH_ROOT}/dist/rippled-ai-core/rippled-ai-core-source"
TEMPLATE_PATH = (
    f"{ATHENAH_ROOT}/playgrounds/core_dev/template.md"
)
RESULTS_DIR = (
    f"{ATHENAH_ROOT}/playgrounds/core_dev/results"
)
AGENT_MODEL = "gpt-4.1"
REVISION_ROUNDS = 1
ATHENAH_CLIENT_NAME: str = "rippled-ai-core"

ACCURACY_NOTICE = (
    "It is CRITICAL that your response is accurate, precise, and strictly grounded in the provided information. "
    "Do NOT invent, assume, or extrapolate beyond what is present. "
    "If you are unsure, state so clearly. "
    "Every statement must be directly supported by the input.",
    f"Project Root: {PROJECT_ROOT} src/xrpld/file.h -> {PROJECT_ROOT}/src/xrpld/file.h",
    "Do not return the `input` and `output` keys in your response. Only return the output"
)


def filter_relevant_symbols(
    client: AthenahClient,
    symbol_map: Any,
    pre_info: str,
    lesson_info: str,
    descriptions: List[Dict[str, Any]] = [],
):
    """Use an agent to filter relevant symbol locations."""
    response_format: str = """
    [{"file_path": "path/to/file.cpp", "justification": "Why this is relevant."}]
"""
    prompt = f"""
You are a code documentation assistant. Your job is to identify which symbol locations are most relevant to the functionality described. 
You must only use the symbol map, descriptions, and pre-existing information provided.

{ACCURACY_NOTICE}

Symbol Map:
{symbol_map}

Descriptions:
{descriptions}

Pre-existing information:
{pre_info}

Specific Lesson Information:
{lesson_info}

The lesson information is a summary of the functionality we are teaching. YOU MUST use this information to help you decide which symbols, and information is relevant.

Only Return json of relevant file paths and a brief justification for each.
Response Format:
{response_format}
"""
    response = client.agent_prompt(
        "Relevance Classifier",
        "Classify which symbol locations are most relevant to the functionality.",
        prompt,
    )
    if isinstance(response, str):
        # If the response is a string, attempt to parse it as JSON
        try:
            safe_response = safe_json_loads(response) or []
            if 'output' in safe_response:
                return safe_json_loads(safe_response['output']) or []
        except json.JSONDecodeError:
            safe_response = []
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        if 'output' in response:
            return safe_json_loads(response['output']) or []
        return response


def extract_function_code(file_path: str, function_name: str) -> str:
    """Extract the source code of a function from a file (Python version)."""
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

{ACCURACY_NOTICE}

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
    import json

    try:
        process_map = json.loads(response)
    except Exception:
        process_map = []
    return process_map


def step_through_code(
    client,
    process_map: List[Dict[str, str]],
    relevant_info: str,
    descriptions: List[Dict[str, Any]] = [],
    relevant_file_paths: List[str] = [],
) -> List[Dict[str, str]]:
    """For each function in the process map, extract its code and ask the agent to explain it."""
    explanations = []
    for step in process_map:
        file_path = step["file"]
        function_name = step["function"]
        code = extract_function_code(file_path, function_name)
        prompt = f"""
You are a code explainer. ONLY use the code below and the provided context.

{ACCURACY_NOTICE}

Function: {function_name}
File: {file_path}

Code:
{code}

Relevant context:
{relevant_info}

Descriptions:
{descriptions}

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


def create_lesson_plan(
    client,
    functionality,
    template,
    step_explanations,
    relevant_info,
    descriptions,
    relevant_file_paths: List[str] = [],
):
    """Generate lesson plan using the agent and a template, grounded in code explanations."""
    steps_md = ""
    for step in step_explanations:
        steps_md += f"### {step['function']} ({step['file']})\n\n"
        steps_md += f"```cpp\n{step['code']}\n```\n\n"
        steps_md += f"{step['explanation']}\n\n"

    prompt = f"""
You are a technical writer. ONLY use the code explanations and information provided.

{ACCURACY_NOTICE}

Our goal is to create a lesson plan that fully and comprehensivly explains EVERY aspect of the source code, specifically focusing on the {functionality} functionality. 
We will use this template to break down the functionality into its components and describe how they work together.

Template: 
{template}

Code Explanations:
{steps_md}

Relevant Information:
{relevant_info}
Relevant File Paths:
{relevant_file_paths}

Descriptions:
{descriptions}

The user should come away with a complete understanding of the functionality, how it works, and how the components interact.
"""
    return client.agent_prompt(
        "Source Code Teacher",
        "Teach the functionality of the XRPL source code in a structured way, using the provided template. The goal is to break down the functionality into its components and describe how they work together.",
        prompt,
    )
import json

def update_lesson_plan(
    client,
    lesson: Dict[str, Any],
    current: str,
    template: str,
    user_input: str,
):

    """Generate lesson plan using the agent and a template, grounded in code explanations."""
    prompt = f"""
We are teaching the functionality of source code. We need to explain every aspect of the source code. We need to organize the information in a way that is easy to understand and follow. Also we have some updates from the user. We should add source code and links into the lesson plan.

{ACCURACY_NOTICE}

Here is the current documentation draft:
{json.dumps(current, indent=2)}
Here is a template we can use to break down the functionality into its components and describe how they work together:
{template}

Lesson Metadata: {lesson}

User Input: {user_input}

"""
    return client.agent_prompt(
        "Source Code Content Creator",
        "Update the lesson plan with new information and explanations.",
        prompt,
    )

def revision_loop(client, initial_doc, relevant_info, descriptions, template, rounds=3):
    """Iteratively ask the agent to check for missing information and revise the documentation."""
    doc = initial_doc
    for i in range(rounds):
        # 1. Ask if anything is missing
        missing_prompt = f"""
You are a documentation reviewer. ONLY use the documentation and information provided.

{ACCURACY_NOTICE}

Here is the current documentation draft:

{doc}

Is there anything missing or unclear in the above documentation? Use the following relevant information to help you decide:

{relevant_info}

{descriptions}
"""
        missing_response = client.agent_prompt(
            "Documentation Reviewer",
            "Review the documentation and identify missing or unclear parts.",
            missing_prompt,
        )
        # 2. Ask to revise/update
        revise_prompt = f"""
You are a documentation reviser. ONLY use the documentation, feedback, and information provided.

{ACCURACY_NOTICE}

Here is the current documentation draft:

{doc}

Here is the feedback on what is missing or unclear:

{missing_response}

Please revise and update the documentation using the template below, making sure to address the feedback:

Template:
{template}

Relevant Information:
{relevant_info}

Do not make up any information not present in the documentation. The documentation should be a direct reflection of the code and explanations provided.
"""
        doc = client.agent_prompt(
            "Documentation Reviser",
            "Revise and update the documentation based on feedback.",
            revise_prompt,
        )
    return doc


def get_symbol_names(
    client: AthenahClient,
    functionality: str,
    extra_info: List[str],
) -> List[str]:
    prompt: str = f"""
Create a list of symbols (functions, classes, variables, etc.) that are relevant to the functionality described below.

{ACCURACY_NOTICE}

Functionality: {functionality}

Return the results using the template below:
- Only return a python array of strings
"""
    return ast.literal_eval(
        client.rag_prompt_v2(
            extra_info,
            prompt,
        )
    )


# print(f"Relevant Files: {all_relevant_file_names[0]}")
# find and update lessons from functionality
def find_lesson_by_functionality(lessons: List[Dict[str, Any]], functionality: str) -> Dict[str, Any]:
    for lesson in lessons:
        if lesson["functionality"] == functionality:
            return lesson
    return None


def create_update_lesson(functionality: str, extra_info: Dict[str, Any] = None, user_input: List[Dict[str, Any]] = None) -> None:
    # functionality: str = lesson["functionality"]
    current_json: Dict[str, Any] = read_json(
        f"{ATHENAH_ROOT}/playgrounds/core_dev/lesson.json"
    )
    current_json = current_json.copy()

    # Note do not update the detail
    latest_topic = current_json[functionality]

    latest_topic['extra_info'] = extra_info
    latest_topic['user_input'] = user_input
    # current_json[functionality][f'{time.time()}'] = latest_topic
    write_json(
        f"{ATHENAH_ROOT}/playgrounds/core_dev/lesson.json",
        current_json)

def write_lesson_plan(functionality: str, data: Any) -> None:
    output_path = f"{RESULTS_DIR}/{functionality}.md"
    if isinstance(data, str):
        print("Data is a str.")
        data = "\n".join(data)
        data = data.replace("```markdown", "````")
        data = data.replace("```", "````")
        write_file(output_path, data)
    if isinstance(data, list):
        print("Data is a list.")
        write_file(output_path, "\n".join(data))
    if isinstance(data, dict):
        print("Data is a dict.")
        data = "\n".join(
            [f"{key}: {value}" for key, value in data.items()]
        )
        write_file(output_path, data)


def create_extra_info(
    detail: Dict[str, Any],
    extra_info: Dict[str, Any],
) -> None:
    functionality = detail["functionality"]
    description = detail["description"]
    detail_paths = detail["detail_paths"]
    ignore_info = detail["ignore_info"]

    # print(f"Creating lesson for: {detail}")
    ai_base: AthenahClient = AthenahClient("id", "dist", model_name="gpt-4o-mini")
    ai_base.init_llm()
    ai_source: AthenahClient = AthenahClient(
        "id", "dist", ATHENAH_CLIENT_NAME, "v1", AGENT_MODEL
    )

    all_relevant_file_names = ai_source.get_relevant_file_names(functionality, 0, 100)
    if 'all_relevant_file_names' in detail:
        percent_difference = (
            len(all_relevant_file_names) / len(detail['all_relevant_file_names'])
        ) * 100

        print(f"Percent difference: {percent_difference:.2f}%")
    
    extra_info['all_relevant_file_names'] = all_relevant_file_names
    write_json(f'{functionality}_all_relevant_file_names.json', all_relevant_file_names)

    relevant_files_str = "\n".join([f"Relevant File: {path}" for path in detail_paths])
    _extra_info = f"""
    {relevant_files_str}

    # Important Information provided as feedback for you: {extra_info}
    # """

    symbols: List[str] = get_symbol_names(
        ai_source, functionality, _extra_info
    )
    # print(f"Symbols found: {len(symbols)}")
    write_json(f'{functionality}_symbols.json', {"symbols": symbols})
    extra_info['symbols'] = symbols

    symbol_map: List[Dict[str, Any]] = all_relevant_file_names
    # symbol_map: List[Dict[str, Any]] = []
    # for symbol in symbols:
    #     result = symbol_to_source_occurances(symbol, PROJECT_ROOT)
    #     if result is None:
    #         print(f"Symbol {symbol} not found in {PROJECT_ROOT}.")
    #         continue
    #     symbol_map.extend(result)
    extra_info['symbol_map'] = symbol_map
    write_json(f'{functionality}_symbol_map1.json', extra_info['symbol_map'])
    for i in range(len(symbol_map)):
        symbol = symbol_map[i]
        ai_help = get_ai_v1_json(symbol["file_path"])
        if "error" in ai_help:
            print(f"Error getting AI v1 JSON for {symbol['file_path']}: {ai_help['error']}")
            ai_help = None
        extra_info['symbol_map'][i]['ai'] = ai_help
    
    write_json(f'{functionality}_symbol_map2.json', extra_info['symbol_map'])
    pre_info: str = ""
    try:
        pre_info = read_file(RESULTS_DIR + "/" + functionality + ".md")
    except FileNotFoundError:
        print(
            f"Pre-existing information file not found at {RESULTS_DIR}. Using empty string."
        )

    relevant_response = filter_relevant_symbols(
        ai_source, symbol_map, all_relevant_file_names, pre_info, description
    )
    extra_info['relevant_response'] = relevant_response
    write_json(f'{functionality}_relevant_response.json', relevant_response)

    question = f"""
    Your purpose is to teach the functionality of source code to someone. You will need to teach them all the steps and processes involved in the functionality.
    
    Topic: {functionality}
    Similar Names: {symbols}
    
    What is the full process or flow of the functionality described?

    Create a json map of the process. Use exact function names in the exact order. 
    For each function, step into the function and describe it in an agnostic way.
    We want a complete and comprehensive map of the functionality we are teaching.

    Ignore Subjects:
    {ignore_info}

    {ACCURACY_NOTICE}
    """
    process_map = parse_process_map(ai_source, relevant_response, question)
    write_json(f'{functionality}_process_map.json', process_map)

    step_explanations = step_through_code(
        ai_source,
        process_map,
        relevant_response,
        [],
        all_relevant_file_names,
    )
    extra_info['step_explanations'] = step_explanations
    write_json(f'{functionality}_step_explanations.json', step_explanations)


    template = read_file(TEMPLATE_PATH)

    initial_doc = create_lesson_plan(
        ai_source,
        functionality,
        template,
        step_explanations,
        relevant_response,
        [],
        all_relevant_file_names,
    )
    extra_info['initial_doc'] = initial_doc
    write_json(f'{functionality}_initial_doc.json', initial_doc)

    final_doc = revision_loop(
        ai_source,
        initial_doc,
        relevant_response,
        all_relevant_file_names,
        template,
        rounds=REVISION_ROUNDS,
    )
    extra_info['final_doc'] = final_doc
    write_json(f'{functionality}_final_doc.json', final_doc)
    return extra_info

def create_lesson(
    latest_lesson: Dict[str, Any],
) -> None:
    extra_info: Dict[str, Any] = {}

    detail: Dict[str, Any] = latest_lesson.get("detail", {})
    if not isinstance(latest_lesson, dict):
        raise ValueError("Lesson must be a dictionary.")
    
    functionality = detail["functionality"]

    extra_info = create_extra_info(
        detail,
        extra_info,
    )

    write_lesson_plan(functionality, extra_info['final_doc'])
    create_update_lesson(functionality, extra_info, [])
    

def update_lesson(
    lesson: Dict[str, Any],
    user_input: str,
) -> None:
    detail = lesson.get('detail').copy()
    extra_info = lesson.get('extra_info').copy()
    user_input_array = lesson.get('user_input').copy()
    functionality = detail["functionality"]
    all_relevant_file_names: List[Any] = extra_info.get("all_relevant_file_names", [])
    relevant_response: List[Dict[str, Any]] = extra_info.get("relevant_response", [])

    ai_base: AthenahClient = AthenahClient("id", "dist", model_name="gpt-4o-mini")
    ai_base.init_llm()
    ai_source: AthenahClient = AthenahClient(
        "id", "dist", ATHENAH_CLIENT_NAME, "v1", AGENT_MODEL
    )
    
    print(f"Updating lesson for: {functionality}")

    current = read_file(TEMPLATE_PATH)
    template = read_file(TEMPLATE_PATH)

    update_doc = update_lesson_plan(
        ai_source,
        lesson,
        current,
        template,
        user_input,
    )

    extra_info['update_doc'] = update_doc

    final_doc = revision_loop(
        ai_source,
        update_doc,
        relevant_response,
        all_relevant_file_names,
        template,
        rounds=REVISION_ROUNDS,
    )

    extra_info['final_doc'] = final_doc
    user_input_array.append({
        "user_input": user_input,
        "timestamp": time.time(),
    })

    write_lesson_plan(functionality, final_doc)
    create_update_lesson(functionality, extra_info, user_input_array)


if __name__ == "__main__":
    lesson_json: Dict[str, Any] = read_json(
        f"{ATHENAH_ROOT}/playgrounds/core_dev/lesson.json"
    )

    for key, json_data in lesson_json.items():
        latest_lesson: Dict[str, Any] = json_data.get('latest', {})
        latest_detail = latest_lesson.get("detail", {})
        functionality = latest_detail['functionality']
        if not latest_detail.get('retry'):
            print(f"Skipping {functionality} due to retry flag.")
            continue

        create_lesson(
            latest_lesson,
        )
#         print(f"Lesson for {functionality} created successfully.")
#         latest_user_input = latest_lesson.get("user_input", {})
#         _user_input = f"""
# The user has provided the following input to update the lesson:
# {latest_user_input}
# """
#         update_lesson(
#             latest_lesson,
#             user_input=_user_input,
#         )
