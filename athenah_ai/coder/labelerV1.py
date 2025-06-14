import os
import json
import logging
from typing import Dict, Any, List

from athenah_ai.client import AthenahClient, MODEL_MAP
from athenah_ai.utils.tokens import get_token_total

from basedir import basedir

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)


class AICodeLabelerV1:
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
        self.client = AthenahClient(
            self.id, self.dir, self.name, self.version, "gpt-4.1", temperature=0
        )

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

    def get_description_of_file(
        self, file_name: str, content: str
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

        Response Template:
        {response_template}

        Instructions:

        - Do not include code blocks
        - If the list of points is empty return []
        - Return valid json
        """
        ai_response = self.client.prompt(prompt)
        # print(f"Description: {ai_response}")
        try:
            json_data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error: `get_description_of_file`: {e}")
            json_data = {"description": ""}
            # raise ValueError(f"Failed to parse AI response: {e}")
        return json_data

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
        logger.debug("file: {} language: {}".format(file_name, language))
        if language:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
                description = self.get_description_of_file(file_path, source_code)
                config: Dict[str, Any] = {
                    "file_path": file_path,
                    "description": description["description"],
                    "language": language,
                }
                # remove the .txt extension
                file_path = file_path.replace(".txt", "")
                dest_file_path = f"{file_path}.ai.v1.json"
                with open(dest_file_path, "w") as f:
                    json.dump(config, f, indent=2, sort_keys=True)

    def get_details_in_dir(self, dir_path: str) -> Dict[str, str]:
        """
        Traverse the directory and subdirectories to find all source files.
        For each file, extract function definitions using AI assistance.
        Build a mapping from function name to file path.
        """
        MAX_TOKENS: int = MODEL_MAP[self.client.model_name]
        too_big_files: List[str] = []
        for root, _, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                total_lines: int = self.get_total_lines_of_file(file_path)
                logger.debug(f"File {file_name} has: {total_lines} lines")
                # Check for ai file first
                if file_path.endswith(".ai.v1.json"):
                    logger.debug(f"Skipping AI file: {file_path}")
                    continue
                # Check if the file has an ai.v1.json file already
                ai_file_path = f"{file_path.replace('.txt', '')}.ai.v1.json"
                if os.path.exists(ai_file_path):
                    logger.debug(f"Skipping existing AI file: {ai_file_path}")
                    continue
                with open(file_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
                    total_tokens = get_token_total(source_code)
                    print(total_tokens)
                    if total_tokens > MAX_TOKENS:
                        logger.warning(
                            f"File {file_path} has {total_tokens} tokens, which exceeds the limit of {MAX_TOKENS} tokens."
                        )
                        too_big_files.append(file_path)
                        continue

                    self.get_details_for_file(file_path, file_name)

        print(f"Too big files: {too_big_files}")
