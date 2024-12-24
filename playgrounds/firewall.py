#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer
from athenah_ai.client import AthenahClient
from athenah_ai.libs.shell import ShellClient
import ast

# Indexing (if required)
path: str = "/Users/darkmatter/projects/nerd-nest/firewall-monorepo/ts-api"
indexer = AthenahIndexer("local", "id", "dist", "firewall-server", "v1")
indexer.index_dir(path, ["src", "tests"], "firewall-server")


class Core:
    """
    Core class for handling file operations and generating code fixes.
    """

    def __init__(self, client_id: str, client_dist: str, client_server: str):
        self.client = AthenahClient(client_id, client_dist, client_server)

    def read_file(self, path: str) -> str:
        with open(path, "r") as f:
            return f.read()

    def save_code(self, code_changes: list):
        for content in code_changes:
            print(f"Applying changes to file: {content['file']}")
            file_path: str = content["file"]
            code: str = content["code"]
            start_line: int = content["start_line"] - 1
            end_line: int = content["end_line"]

            with open(file_path, "r") as f:
                data = f.readlines()

            updated_data = data[:start_line] + code.split("\n") + data[end_line:]
            with open(file_path, "w") as f:
                f.writelines(updated_data)

    def generate_code_fix(self, content: str, errors: str, full_path: str) -> list:
        return_format: str = """
        [{
            "file": "The file path",
            "start_line": "The start line of the new code",
            "end_line": "The end line of the new code",
            "code": "The code changes that will fix the errors"
        }]
        """
        prompt: str = f"""
        Fix the following errors in this code:

        Only fix one error at a time and only return one code change at a time.

        Code: {content}
        Errors: {errors}
        Path: {full_path}

        - You must return valid TypeScript code that will fix the errors.
        - Do not return code in code blocks or use ```typescript.
        - Return the full code from line 1 to the end of the file.

        {return_format}
        """
        response = self.client.prompt(prompt)
        code_changes = ast.literal_eval(response)
        print(code_changes)
        return code_changes


class TypeScriptTester:
    """
    Class for formatting and testing TypeScript code.
    """

    def __init__(self, base_path: str, test_file: str):
        self.base_path = base_path
        self.test_file = test_file
        self.shell_client = ShellClient()

    def format_test_file(self):
        print("Formatting the test file...")
        self.shell_client.do_run(
            self.base_path,
            [f"npx prettier --write {self.test_file}"],
        )

    def run_tests(self):
        print("Running tests...")
        response = self.shell_client.do_run(
            self.base_path,
            [f"npm run test:integration {self.test_file}"],
        )
        print(response.stderr)
        success = f"PASS {self.test_file}" in response.stderr
        print(f"Test {'passed' if success else 'failed'}.")
        return success, response


class CodeFixer:
    """
    Class that uses Core and TypeScriptTester to fix code based on test results.
    """

    def __init__(
        self,
        base_path: str,
        test_file: str,
        client_id: str,
        client_dist: str,
        client_server: str,
    ):
        self.base_path = base_path
        self.test_file = test_file
        self.core = Core(client_id, client_dist, client_server)
        self.tester = TypeScriptTester(base_path, test_file)

    def run(self):
        while True:
            self.tester.format_test_file()
            test_passed, response = self.tester.run_tests()
            if test_passed:
                print("All tests passed successfully!")
                break

            full_path = f"{self.base_path}/{self.test_file}"
            content = self.core.read_file(full_path)
            errors = response.stderr

            print("Generating code fixes...")
            code_changes = self.core.generate_code_fix(content, errors, full_path)
            self.core.save_code(code_changes)
            print("Code fixes applied. Retesting...\n")


if __name__ == "__main__":
    base_path = "/Users/darkmatter/projects/nerd-nest/firewall-monorepo/ts-api"
    test_file = "tests/integration/api/user/passwordreset.test.ts"
    client_id = "id"
    client_dist = "dist"
    client_server = "firewall-server"

    code_fixer = CodeFixer(base_path, test_file, client_id, client_dist, client_server)
    code_fixer.run()
