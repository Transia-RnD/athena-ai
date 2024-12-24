import os
import json
import logging
from typing import Dict, Any, List

from athenah_ai.client import AthenahClient

from basedir import basedir

logger = logging.getLogger("app")


class AthenahPreparer:
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

    def prepare_github_data(self, allowed_dirs: List[Any]) -> List[Dict[str, Any]]:
        """
        Prepare GitHub data by extracting functions and function calls from files in specified directories.
        """
        for dir_path in allowed_dirs:
            dir_full_path = os.path.join(self.source_path, dir_path)
            print(dir_full_path)
            self.get_details_in_dir(dir_full_path)

        # Now, iterate through files in dirs (data['dirs'])
        # dirs_to_process = data.get("dirs", [])
        # output_dir = data.get("output_dir", "output")
        # output_dir_full = os.path.join(self.base_path, output_dir)
        # os.makedirs(output_dir_full, exist_ok=True)

        # for dir_path in dirs_to_process:
        #     dir_full_path = os.path.join(self.base_path, dir_path)
        #     for root, _, files in os.walk(dir_full_path):
        #         for file in files:
        #             file_ext = os.path.splitext(file)[1]
        #             language = self.language_extensions.get(file_ext)
        #             if language:
        #                 file_path = os.path.join(root, file)
        #                 total_lines = self.get_total_lines_of_file(file_path)

        #                 # List functions in the file based on the language
        #                 functions = self.list_functions_in_file(file_path, language)
        #                 self.validate_functions(functions, total_lines)

        #                 for function_info in functions:
        #                     function_name = function_info["name"]
        #                     function_linenumber = function_info.get("lineno", None)
        #                     # Extract function source code
        #                     function_source = self.extract_function_source_language(
        #                         file_path, function_name, language
        #                     )
        #                     # Extract function calls using AI
        #                     function_calls = self.extract_function_calls_ai(
        #                         function_source, language
        #                     )
        #                     # Write function calls to file
        #                     self.write_function_call_list(
        #                         function_name, function_calls, output_dir_full
        #                     )
        #                     # Write function source code to file
        #                     self.write_function_source(
        #                         function_name, function_source, output_dir_full
        #                     )
        # return []

    def get_total_lines_of_file(self, file_path: str) -> int:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def get_description_of_file(
        self, file_path: str, classes: dict, functions: dict, args: dict
    ) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        prompt = f"""
        Bullet Point the `source_code.txt`:

        ```source_code.txt
        {source_code}
        ```

        Classes: {classes}
        Functions: {functions}
        Arguments: {args}

        Response Template:
        - Describe the source code in a few sentences.
        """
        ai_response = self.client.base_prompt(None, prompt)
        print(ai_response)
        try:
            functions = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            # functions = []
            raise ValueError(f"Failed to parse AI response: {e}")
        return functions

    def list_functions_in_file(
        self, file_path: str, language: str
    ) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

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
        {source_code}
        ```

        Response format:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of functions is empty return []
        """
        ai_response = self.client.base_prompt(None, prompt)
        print(ai_response)
        try:
            functions = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            # functions = []
            raise ValueError(f"Failed to parse AI response: {e}")
        return functions

    def list_classes_in_file(
        self, file_path: str, language: str
    ) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

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
        {source_code}
        ```

        Response format:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of functions is empty return []
        """
        ai_response = self.client.base_prompt(None, prompt)
        print(ai_response)
        try:
            functions = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            # functions = []
            raise ValueError(f"Failed to parse AI response: {e}")
        return functions

    def list_args_in_file(self, file_path: str, language: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        response_template: str = """
        [{
            "name": "class_name",
            "lineno": starting_line_number
        }]
        """
        prompt = f"""
        List all arguments and variables used in the `source_code.txt`:

        ```source_code.txt
        {source_code}
        ```

        Response format:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of args is empty return []
        """
        ai_response = self.client.base_prompt(None, prompt)
        print(ai_response)
        try:
            functions = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            # functions = []
            raise ValueError(f"Failed to parse AI response: {e}")
        return functions

    def validate_functions(self, functions: List[Dict[str, Any]], total_lines: int):
        for func in functions:
            lineno = func.get("lineno", None)
            if lineno and lineno > total_lines:
                logger.warning(
                    f"Function {func['name']} starts at line {lineno}, which is beyond total lines {total_lines}."
                )

    def extract_function_source_language(
        self, file_path: str, function_name: str, language: str
    ) -> str:
        """
        Extract the full source code of a function using AI assistance.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        prompt = f"""
You are a code extraction assistant. In the following {language} source code, extract the full source code of the function named "{function_name}".
Provide only the function source code, including its signature and body.

Source code:
{source_code}

Response:
"""
        function_source = self.client.prompt(prompt).strip()
        print(function_source)
        return function_source

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

    def extract_function_calls_ai(
        self, function_source_code: str, language: str
    ) -> List[Dict[str, Any]]:
        prompt = f"""
You are a code analysis assistant. Extract all function calls within the following {language} function source code.
Include the function name and the line number where it is called.

Function Source Code:
{function_source_code}

Response format:
[
    {{"function_name": "called_function_name", "line_number": line_number}},
    ...
]
"""
        ai_response = self.client.prompt(prompt)
        print(ai_response)
        try:
            function_calls = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response for function calls: {e}")
            function_calls = []
        return function_calls

    def get_details_for_file(self, base_path: str, file_path: str) -> Dict[str, str]:
        """
        Traverse the directory and subdirectories to find all source files.
        For each file, extract function definitions using AI assistance.
        Build a mapping from function name to file path.
        """
        file_ext = os.path.splitext(file_path)[-2]
        _file_ext = ".".join([s for s in file_ext.split(".") if s != "txt"])
        _file_ext = _file_ext.split(".")[-1]
        language = self.language_extensions.get(f".{_file_ext}")
        print("file: {} language: {}".format(file_path, language))
        return
        if language:
            file_path = os.path.join(base_path, file_path)
            classes = self.list_classes_in_file(file_path, language)
            args = self.list_args_in_file(file_path, language)
            functions = self.list_functions_in_file(file_path, language)
            description = self.get_description_of_file(
                file_path, classes, functions, args
            )
            # store the functions args and classes in a config.ai.json file
            with open(f"{file_path}.ai.json", "w") as f:
                json.dump(
                    {
                        "file_path": file_path,
                        "description": description,
                        "language": language,
                        "functions": functions,
                        "args": args,
                        "classes": classes,
                    },
                    f,
                )

    def get_details_in_dir(self, dir_path: str) -> Dict[str, str]:
        """
        Traverse the directory and subdirectories to find all source files.
        For each file, extract function definitions using AI assistance.
        Build a mapping from function name to file path.
        """
        for root, _, files in os.walk(dir_path):
            for file in files:
                self.get_details_for_file(root, file)
