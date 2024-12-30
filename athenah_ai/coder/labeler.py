import os
import json
import logging
from typing import Dict, Any, List

from athenah_ai.client import AthenahClient
from athenah_ai.utils.tokens import get_token_total

from basedir import basedir

logger = logging.getLogger("app")


class AICodeLabeler:
    storage_type: str = "local"
    id: str = ""
    dir: str = ""
    name: str = ""
    version: str = ""

    # Mapping of file extensions to languages
    language_extensions = {
        ".py": "python",
        ".cpp": "cpp",
        ".c": "c",
        ".js": "javascript",
        ".ts": "typescript",
        ".h": "c header",
        # Add more as needed
    }

    def __init__(
        self,
        storage_type: str,
        id: str,
        dir: str,
        name: str,
        version: str,
    ):
        self.storage_type = storage_type
        self.id = id
        self.dir = dir
        self.name = name
        self.version = version
        self.base_path: str = os.path.join(basedir, dir)
        self.name_path: str = os.path.join(self.base_path, name)
        self.source_path: str = os.path.join(self.name_path, f"{name}-source")
        self.client = AthenahClient(self.id, self.dir)

    def prepare_source_code(self, allowed_dirs: List[Any]) -> List[Dict[str, Any]]:
        """
        Prepare Source code by extracting functions and function calls from files in specified directories.
        """
        for dir_path in allowed_dirs:
            dir_full_path = os.path.join(self.source_path, dir_path)
            self.get_details_in_dir(dir_full_path)

    def get_total_lines_of_file(self, file_path: str) -> int:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def write_function_source(
        self, function_name: str, function_source: str, output_dir: str
    ):
        output_file = os.path.join(output_dir, f"{function_name}.ai")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(function_source)

    def write_function_call_list(
        self, function_name: str, function_calls: List[Dict[str, Any]], output_dir: str
    ):
        output_file = os.path.join(output_dir, f"{function_name}.list.json.ai")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(function_calls, f, indent=4)

    def get_description_of_file(
        self, file_name: str, content: str, classes: dict, functions: dict, args: dict
    ) -> List[Dict[str, Any]]:
        response_template: str = """
        { "description": "file_description" }
        """
        prompt = f"""
        Summarize the {file_name} file:
        ```code
        {content}
        ```

        FileName: {file_name}
        Classes: {classes}
        Functions: {functions}
        Arguments: {args}

        Response Template:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of points is empty return []
        - Return valid json
        """
        ai_response = self.client.base_prompt(None, prompt)
        # print(f"Description: {ai_response}")
        try:
            json_data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error: `get_description_of_file`: {e}")
            json_data = {"description": ""}
            # raise ValueError(f"Failed to parse AI response: {e}")
        return json_data

    def list_functions_in_file(self, content: str) -> List[Dict[str, Any]]:
        response_template: str = """
        [{
            "name": "function_name",
            "args": ["list of arguments"],
            "lineno": starting_line_number
        }]
        """
        prompt = f"""
        List all functions in the `source_code.txt`:

        ```source_code.txt
        {content}
        ```

        Response format:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of functions is empty return []
        """
        ai_response = self.client.base_prompt(None, prompt)
        # print(f"Function: {ai_response}")
        try:
            json_data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error: `list_functions_in_file`: {e}")
            json_data = []
            # raise ValueError(f"Failed to parse AI response: {e}")
        return json_data

    def list_namespaces_in_file(self, content: str) -> List[Dict[str, Any]]:
        response_template: str = """
        [{
            "name": "namespace_name",
        }]
        """
        prompt = f"""
        List all namespaces in the `source_code.txt`:

        ```source_code.txt
        {content}
        ```

        Response format:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of namespaces is empty return []
        """
        ai_response = self.client.base_prompt(None, prompt)
        # print(f"Function: {ai_response}")
        try:
            json_data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error: `list_namespaces_in_file`: {e}")
            json_data = []
            # raise ValueError(f"Failed to parse AI response: {e}")
        return json_data

    def list_classes_in_file(self, content: str) -> List[Dict[str, Any]]:
        response_template: str = """
        [{
            "name": "class_name",
            "constructors": "list of constructors",
            "lineno": starting_line_number
        }]
        """
        prompt = f"""
        List all classes in the `source_code.txt`:

        ```source_code.txt
        {content}
        ```

        Response format:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of functions is empty return []
        """
        ai_response = self.client.base_prompt(None, prompt)
        # print(f"Classes: {ai_response}")
        try:
            json_data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error: `list_classes_in_file`: {e}")
            json_data = []
            # raise ValueError(f"Failed to parse AI response: {e}")
        return json_data

    def list_args_in_file(self, content: str) -> List[Dict[str, Any]]:
        response_template: str = """
        [{
            "name": "class_name",
            "lineno": starting_line_number
        }]
        """
        prompt = f"""
        List all arguments and variables used in the `source_code.txt`:

        ```source_code.txt
        {content}
        ```

        Response format:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of args is empty return []
        """
        ai_response = self.client.base_prompt(None, prompt)
        # print(f"Arguments: {ai_response}")
        try:
            json_data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error: `list_args_in_file`: {e}")
            json_data = []
            # raise ValueError(f"Failed to parse AI response: {e}")
        return json_data

    def validate_functions(self, functions: List[Dict[str, Any]], total_lines: int):
        for func in functions:
            lineno = func.get("lineno", None)
            if lineno and lineno > total_lines:
                logger.warning(
                    f"Function {func['name']} starts at line {lineno}, which is beyond total lines {total_lines}."
                )

    def get_details_for_file(self, file_path: str, file_name: str) -> Dict[str, str]:
        """
        Traverse the directory and subdirectories to find all source files.
        For each file, extract function definitions using AI assistance.
        Build a mapping from function name to file path.
        """
        file_ext = os.path.splitext(file_name)[-2]
        _file_ext = ".".join([s for s in file_ext.split(".") if s != "txt"])
        _file_ext = _file_ext.split(".")[-1]
        language = self.language_extensions.get(f".{_file_ext}")
        logger.info("file: {} language: {}".format(file_name, language))
        if language:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
                classes = self.list_classes_in_file(source_code)
                args = self.list_args_in_file(source_code)
                functions = self.list_functions_in_file(source_code)
                namespaces = self.list_namespaces_in_file(source_code)
                description = self.get_description_of_file(
                    file_path, source_code, classes, functions, args
                )

                config: Dict[str, Any] = {
                    "file_path": file_path,
                    "description": description["description"],
                    "namespaces": namespaces,
                    "language": language,
                    "functions": functions,
                    "args": args,
                    "classes": classes,
                }
                # remove the .txt extension
                file_path = file_path.replace(".txt", "")
                dest_file_path = f"{file_path}.ai.json"
                with open(dest_file_path, "w") as f:
                    json.dump(config, f, indent=2, sort_keys=True)

    def get_details_in_dir(self, dir_path: str) -> Dict[str, str]:
        """
        Traverse the directory and subdirectories to find all source files.
        For each file, extract function definitions using AI assistance.
        Build a mapping from function name to file path.
        """
        MAX_TOKENS: int = 2000
        too_big_files: List[str] = []
        for root, _, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                total_lines: int = self.get_total_lines_of_file(file_path)
                print(f"File {file_name} has: {total_lines} lines")
                with open(file_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
                    total_tokens = get_token_total(source_code)
                    if total_tokens > MAX_TOKENS:
                        logger.warning(
                            f"File {file_path} has {total_tokens} tokens, which exceeds the limit of {MAX_TOKENS} tokens."
                        )
                        too_big_files.append(file_path)
                        continue

                    self.get_details_for_file(file_path, file_name)

        print(f"Too big files: {too_big_files}")
