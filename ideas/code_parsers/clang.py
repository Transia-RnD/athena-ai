import os
import sys
import json
import clang.cindex


def get_directory_description(dirpath):
    directory_descriptions = {
        "src/ripple/app": "Contains core application logic for the Ripple server, including ledger management and transaction processing.",
        "src/ripple/consensus": "Handles consensus algorithm implementation for transaction validation.",
        "src/ripple/net": "Manages networking and peer-to-peer communication between Ripple nodes.",
        "tests": "Contains unit and integration tests for the Ripple server components.",
    }
    return directory_descriptions.get(dirpath, "No description available.")


def get_file_description(filepath):
    with open(filepath, "r") as file:
        lines = []
        for line in file:
            line = line.strip()
            if line.startswith("//") or line.startswith("/*") or line.startswith("/**"):
                # Remove comment markers
                line = line.lstrip("/").lstrip("*").strip()
                lines.append(line)
            else:
                break  # Stop at the first line of code
        return " ".join(lines) if lines else "No description available."


def extract_function_snippet(cursor):
    extent = cursor.extent
    start = extent.start.offset
    end = extent.end.offset
    with open(extent.start.file.name, "r", encoding="utf-8") as f:
        source = f.read()
    snippet = source[start:end]
    return snippet.strip()


def extract_function_description(cursor):
    raw_comment = cursor.raw_comment
    if raw_comment:
        comment = (
            raw_comment.strip("/**")
            .strip("/*")
            .strip("//")
            .strip()
            .replace("*", "")
            .strip()
        )
        return comment
    else:
        return "No description available."


def extract_class_description(cursor):
    raw_comment = cursor.raw_comment
    if raw_comment:
        comment = (
            raw_comment.strip("/**")
            .strip("/*")
            .strip("//")
            .strip()
            .replace("*", "")
            .strip()
        )
        return comment
    else:
        return "No description available."


def extract_class_methods(class_cursor):
    methods = []
    for c in class_cursor.get_children():
        if c.kind == clang.cindex.CursorKind.CXX_METHOD:
            method_info = {
                "name": c.displayname,
                "snippet": extract_function_snippet(c),
                "description": extract_function_description(c),
            }
            methods.append(method_info)
    return methods


def generate_config(root_dir):
    index = clang.cindex.Index.create()
    config = {"directories": []}

    # Whitelist directories
    whitelist_dirs = [
        os.path.join("src", "ripple", "app"),
        os.path.join("src", "ripple", "consensus"),
        os.path.join("src", "ripple", "net"),
        "tests",
    ]

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirpath_rel = os.path.relpath(dirpath, root_dir)
        # Skip directories not in the whitelist
        if not any(dirpath_rel.startswith(wd) for wd in whitelist_dirs):
            continue

        dir_description = get_directory_description(dirpath_rel)
        directory = {
            "name": dirpath_rel,
            "description": dir_description,
            "classes": [],
            "files": [],
        }

        for filename in filenames:
            if (
                filename.endswith(".cpp")
                or filename.endswith(".h")
                or filename.endswith(".hpp")
            ):
                filepath = os.path.join(dirpath, filename)
                file_description = get_file_description(filepath)
                file_info = {
                    "name": filename,
                    "description": file_description,
                    "functions": [],
                }

                # Parse the code file
                try:
                    translation_unit = index.parse(filepath, args=["-std=c++14"])
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")
                    continue

                for cursor in translation_unit.cursor.get_children():
                    if cursor.location.file and os.path.samefile(
                        cursor.location.file.name, filepath
                    ):
                        if (
                            cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL
                            and cursor.is_definition()
                        ):
                            function_info = {
                                "name": cursor.displayname,
                                "snippet": extract_function_snippet(cursor),
                                "description": extract_function_description(cursor),
                            }
                            file_info.setdefault("functions", []).append(function_info)
                        elif (
                            cursor.kind == clang.cindex.CursorKind.CLASS_DECL
                            and cursor.is_definition()
                        ):
                            class_info = {
                                "name": cursor.displayname,
                                "description": extract_class_description(cursor),
                                "methods": extract_class_methods(cursor),
                            }
                            directory.setdefault("classes", []).append(class_info)
                directory["files"].append(file_info)

        if directory["files"] or directory["classes"]:
            config["directories"].append(directory)

    # Write the config to a JSON file
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


if __name__ == "__main__":
    # Check if the root directory is provided
    if len(sys.argv) < 2:
        print("Usage: python generate_config.py <root_directory>")
        sys.exit(1)
    root_directory = sys.argv[1]
    generate_config(root_directory)
