import os
import re
from typing import Set, List


class EntryPointFinder:
    def __init__(self, base_dir: str, entry_file: str = None, entry_line: int = None):
        self.base_dir = base_dir
        self.language = None
        self.entry_point = entry_file
        self.entry_line = entry_line
        self.visited_files: Set[str] = set()
        self.file_order: List[str] = []
        self.separator = "\n\n# === File Separator ===\n\n"

        if not self.language:
            self.find_language()

    def find_language(self):
        # Check for language-specific files to determine the language
        if any(
            f.endswith(".js") or f.endswith(".ts") for f in os.listdir(self.base_dir)
        ):
            self.language = "JS/TS"
        elif any(f.endswith(".py") for f in os.listdir(self.base_dir)):
            self.language = "PY"
        elif any(
            f.endswith(".cpp") or f.endswith(".h") for f in os.listdir(self.base_dir)
        ):
            self.language = "CPP"
        else:
            raise ValueError("Unable to determine the programming language.")
        print(f"Detected language: {self.language}")

    def build_concatenated_entry_point(self):
        if not self.entry_point:
            raise ValueError("Entry point file not set.")
        if not os.path.exists(self.entry_point):
            raise FileNotFoundError(f"Entry point file {self.entry_point} not found.")

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
        # If entry_line is specified and this is the entry file, adjust the content
        if self.entry_line and os.path.abspath(file_path) == os.path.abspath(
            self.entry_point
        ):
            lines = content.splitlines()
            content = "\n".join(lines[self.entry_line - 1 :])
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
                r"^(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))",
                content,
                re.MULTILINE,
            )
            modules = set()
            for imp in imports:
                modules.update(filter(None, imp))
            return list(modules)
        elif self.language == "JS/TS":
            # Regex to find require or import statements
            imports = re.findall(
                r'(?:require\(["\'](.+?)["\']\)|import.*from\s+["\'](.+?)["\'])',
                content,
            )
            modules = set()
            for imp in imports:
                modules.update(filter(None, imp))
            return list(modules)
        elif self.language == "CPP":
            # Regex to find #include statements
            imports = re.findall(r'#include\s+[<"](.+?)[>"]', content)
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
            # Check in current directory
            possible_path = os.path.join(current_dir, import_name + ".py")
            if os.path.exists(possible_path):
                return possible_path
        elif self.language == "JS/TS":
            # Check for .js or .ts files
            for ext in [".js", ".ts"]:
                possible_path = os.path.join(current_dir, import_name + ext)
                if os.path.exists(possible_path):
                    return possible_path
            # Also check if import_name is a directory with index file
            possible_path = os.path.join(current_dir, import_name, "index.js")
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
            print(
                "The following source files are not included in the concatenated entry point:"
            )
            for file in unused_files:
                print(f"- {file}")
        else:
            print("All source files are included in the concatenated entry point.")

    def is_source_file(self, filename):
        if self.language == "PY" and filename.endswith(".py"):
            return True
        elif self.language == "JS/TS" and (
            filename.endswith(".js") or filename.endswith(".ts")
        ):
            return True
        elif self.language == "CPP" and (
            filename.endswith(".cpp") or filename.endswith(".h")
        ):
            return True
        return False
