#!/usr/bin/env python
# coding: utf-8
import os
import json
from dotenv import load_dotenv
from typing import List, Any, Dict, Tuple
import importlib.util
import inspect

from athenah_ai.logger import logger


def get_tools_in_dir(dir_path: str) -> Tuple[List[str], Dict[str, Any]]:
    functions_list = []
    functions_dict = {}

    # Get all .py files in the directory
    python_files = [f for f in os.listdir(dir_path) if f.endswith(".py")]

    for filename in python_files:
        module_name = filename[:-3]  # Remove '.py' from the end
        module_path = os.path.join(dir_path, filename)

        # Load the module from the file
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get all function members from the module
        module_functions = inspect.getmembers(module, inspect.isfunction)

        # Append functions to the list or dictionary
        for func_name, func_obj in module_functions:
            functions_list.append(func_name)
            functions_dict[func_name] = func_obj  # If using a dictionary

    # Now functions_list contains all functions from all modules
    # functions_dict maps function names to function objects
    return functions_list, functions_dict


def build_agent_tools(tool_names: List[str] = None) -> List[Any]:
    try:
        name_list, tool_dict = get_tools_in_dir("playgrounds/core_dev/tools")
        if tool_names is None:
            raise Exception("Tool names is None")

        logger.info(f"Tools Found #: {len(name_list)}")
        if len(name_list) == 0:
            raise Exception("No Tools found in the directory")
        tools: List[Any] = []
        for name in tool_names:
            logger.info(f"Query for LocalTool: {name}")
            if name in name_list:
                tools.append(tool_dict[name])
        return tools
    except Exception as e:
        logger.error(f"Error building tool list: {e}")
        return []


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
