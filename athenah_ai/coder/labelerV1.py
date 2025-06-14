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

    def process_directories(self, directories: List[str]) -> None:
        """
        Process all files in the given directories, generating AI summaries for each source file.
        """
        for rel_dir in directories:
            abs_dir = os.path.join(self.source_path, rel_dir)
            self._process_directory(abs_dir)

    def _count_file_lines(self, file_path: str) -> int:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def _summarize_file(self, file_name: str, content: str) -> str:
        response_template = '{ "description": "file_description" }'
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
        try:
            json_data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error: `_summarize_file`: {e}")
            json_data = {"description": ""}
        return json_data.get("description", "")

    def _process_file(self, file_path: str, file_name: str) -> None:
        file_ext = os.path.splitext(file_name)[-2]
        _file_ext = ".".join([s for s in file_ext.split(".") if s != "txt"])
        _file_ext = _file_ext.split(".")[-1]
        language = self.language_extensions.get(f".{_file_ext}")
        logger.debug("file: {} language: {}".format(file_name, language))
        if language:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
                description = self._summarize_file(file_name, source_code)
                metadata = {
                    "file_path": file_path,
                    "description": description,
                    "language": language,
                }
                dest_file_path = f"{file_path.replace('.txt', '')}.ai.v1.json"
                with open(dest_file_path, "w") as out_f:
                    json.dump(metadata, out_f, indent=2, sort_keys=True)

    def _process_directory(self, dir_path: str) -> None:
        max_tokens = MODEL_MAP[self.client.model_name]
        oversized_files: List[str] = []
        for root, _, files in os.walk(dir_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_path.endswith(".ai.v1.json"):
                    logger.debug(f"Skipping AI file: {file_path}")
                    continue
                ai_file_path = f"{file_path.replace('.txt', '')}.ai.v1.json"
                if os.path.exists(ai_file_path):
                    logger.debug(f"Skipping existing AI file: {ai_file_path}")
                    continue
                total_lines = self._count_file_lines(file_path)
                logger.debug(f"File {file_name} has: {total_lines} lines")
                with open(file_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
                    total_tokens = get_token_total(source_code)
                    if total_tokens > max_tokens:
                        logger.warning(
                            f"File {file_path} has {total_tokens} tokens, which exceeds the limit of {max_tokens} tokens."
                        )
                        oversized_files.append(file_path)
                        continue
                    self._process_file(file_path, file_name)
        if oversized_files:
            print(f"Oversized files: {oversized_files}")
