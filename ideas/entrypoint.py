import os
import re
import json
import toml
from typing import Set, List


class EntryPointFinder:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.language = None
        self.entry_point = None
        self.visited_files: Set[str] = set()
        self.file_order: List[str] = []
        self.separator = "\n\n# === File Separator ===\n\n"
        self.config_file = os.path.join(self.base_dir, "entrypoint_config.txt")

    def find_language(self):
        # Check for language-specific files to determine the language
        if os.path.exists(os.path.join(self.base_dir, "package.json")):
            self.language = "JS/TS"
        elif os.path.exists(
            os.path.join(self.base_dir, "pyproject.toml")
        ) or os.path.exists(os.path.join(self.base_dir, "setup.py")):
            self.language = "PY"
        elif any(f.endswith(".cpp") for f in os.listdir(self.base_dir)):
            self.language = "CPP"
        else:
            raise ValueError("Unable to determine the programming language.")
        print(f"Detected language: {self.language}")

    def find_entry_point(self):
        potential_dirs = []
        if self.language == "JS/TS":
            potential_dirs = ["src", "lib"]
            entry_file = self.find_entry_in_dirs(
                potential_dirs, ["index.js", "index.ts", "main.js", "main.ts"]
            )
            if not entry_file:
                entry_file = self.find_entry_in_package_json()
        elif self.language == "PY":
            potential_dirs = ["src", "lib"]
            entry_file = self.find_entry_in_dirs(
                potential_dirs, ["__main__.py", "main.py"]
            )
            if not entry_file:
                entry_file = self.find_entry_in_pyproject()
        elif self.language == "CPP":
            potential_dirs = ["src", "lib"]
            entry_file = self.find_entry_in_dirs(potential_dirs, ["main.cpp"])
        else:
            raise ValueError("Language not supported.")

        if entry_file:
            self.entry_point = entry_file
            self.save_entry_point_config()
            print(f"Found entry point: {self.entry_point}")
        else:
            raise FileNotFoundError("Entry point not found.")

    def find_entry_in_dirs(self, dirs, filenames):
        for directory in dirs:
            dir_path = os.path.join(self.base_dir, directory)
            if not os.path.isdir(dir_path):
                continue
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file in filenames:
                        return os.path.join(root, file)
        return None

    def find_entry_in_package_json(self):
        package_json_path = os.path.join(self.base_dir, "package.json")
        if not os.path.exists(package_json_path):
            return None
        with open(package_json_path, "r") as f:
            data = json.load(f)
            if "main" in data:
                return os.path.join(self.base_dir, data["main"])
        return None

    def find_entry_in_pyproject(self):
        pyproject_path = os.path.join(self.base_dir, "pyproject.toml")
        if not os.path.exists(pyproject_path):
            return None
        data = toml.load(pyproject_path)
        # Simplified example, real implementation might be more complex
        scripts = data.get("tool", {}).get("poetry", {}).get("scripts", {})
        if scripts:
            script_entry = next(iter(scripts.values()))
            return os.path.join(self.base_dir, script_entry)
        return None

    def save_entry_point_config(self):
        with open(self.config_file, "w") as f:
            f.write(self.entry_point)
        print(f"Entry point saved to config: {self.config_file}")

    def build_concatenated_entry_point(self):
        if not self.entry_point:
            raise ValueError("Entry point not set.")
        tmp_file_path = os.path.join(
            self.base_dir, "entrypoint_tmp" + self.get_file_extension()
        )
        with open(tmp_file_path, "w") as tmp_file:
            self.recursive_file_import(self.entry_point, tmp_file, generation=0)
        print(f"Temporary entry point file created at: {tmp_file_path}")
        self.compare_source_files()
        return tmp_file_path

    def recursive_file_import(self, file_path, tmp_file, generation):
        if file_path in self.visited_files:
            return
        self.visited_files.add(file_path)
        self.file_order.append(file_path)
        # Use generation to keep track of hierarchy
        with open(file_path, "r") as f:
            content = f.read()
        # Find imports in the file based on language
        imports = self.find_imports(content)
        # Recursively import the dependencies first
        for imp in imports:
            imp_path = self.resolve_import_path(imp, os.path.dirname(file_path))
            if imp_path:
                self.recursive_file_import(imp_path, tmp_file, generation + 1)
        # Write separator and file content to the temp file
        tmp_file.write(
            f"{self.separator}# File: {file_path}, Generation: {generation}\n"
        )
        tmp_file.write(content + "\n")

    def find_imports(self, content):
        if self.language == "PY":
            # Simple regex to find import statements
            imports = re.findall(
                r"^(?:from\s+(\S+)\s+import|import\s+(\S+))", content, re.MULTILINE
            )
            modules = set()
            for imp in imports:
                modules.update(filter(None, imp))
            return list(modules)
        elif self.language == "JS/TS":
            # Regex to find require or import statements
            imports = re.findall(
                r'(?:require\(["\'](.+)["\']\)|import.*from\s+["\'](.+)["\'])', content
            )
            modules = set()
            for imp in imports:
                modules.update(filter(None, imp))
            return list(modules)
        elif self.language == "CPP":
            # Regex to find #include statements
            imports = re.findall(r'#include\s+[<"](.+)[>"]', content)
            return imports
        return []

    def resolve_import_path(self, import_name, current_dir):
        # This function resolves the import path to a file path
        if self.language == "PY":
            # Convert module name to path
            relative_path = import_name.replace(".", os.sep) + ".py"
            possible_path = os.path.join(self.base_dir, relative_path)
            if os.path.exists(possible_path):
                return possible_path
        elif self.language == "JS/TS":
            # Assume .js extension
            relative_path = import_name
            if not relative_path.endswith(".js") and not relative_path.endswith(".ts"):
                relative_path += ".js"
            possible_path = os.path.join(current_dir, relative_path)
            if os.path.exists(possible_path):
                return possible_path
        elif self.language == "CPP":
            # For simplicity, assume includes are local files
            possible_path = os.path.join(current_dir, import_name)
            if os.path.exists(possible_path):
                return possible_path
        return None

    def get_file_extension(self):
        if self.language == "PY":
            return ".py"
        elif self.language == "JS/TS":
            return ".js"
        elif self.language == "CPP":
            return ".cpp"
        return ""

    def compare_source_files(self):
        # Get all source files in the repo
        source_files = set()
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if self.is_source_file(file):
                    file_path = os.path.join(root, file)
                    source_files.add(file_path)
        # Check which files are not included in the tmp file
        unused_files = source_files - self.visited_files
        if unused_files:
            print("The following source files are not included in the entry point:")
            for file in unused_files:
                print(f"- {file}")
        else:
            print("All source files are included in the entry point.")

    def is_source_file(self, filename):
        if self.language == "PY" and filename.endswith(".py"):
            return True
        elif self.language == "JS/TS" and (
            filename.endswith(".js") or filename.endswith(".ts")
        ):
            return True
        elif self.language == "CPP" and filename.endswith(".cpp"):
            return True
        return False


# Example Usage:
# finder = EntryPointFinder(base_dir='/path/to/project')
# finder.find_language()
# finder.find_entry_point()
# tmp_file = finder.build_concatenated_entry_point()
