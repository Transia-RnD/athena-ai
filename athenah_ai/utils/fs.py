#!/usr/bin/env python
# coding: utf-8

import os
from typing import Dict, Any, List  # noqa: F401
import json


def read_json(path: str) -> Dict[str, object]:
    """Read Json

     # noqa: E501

    :param path: Path to json
    :type path: str

    :rtype: Dict[str, object]
    """
    with open(path) as json_file:
        return json.load(json_file)


def write_json(data: Dict[str, object], path: str):
    """Write Json

     # noqa: E501

    :param path: Path to json
    :type path: str

    :rtype: None
    """
    with open(path, "w") as json_file:
        json.dump(data, json_file)


def write_file(path: str, data: Any) -> str:
    """Write File

     # noqa: E501

    :param path: Path to file
    :type path: str

    :rtype: str
    """
    with open(path, "w") as f:
        return f.write(data)


def read_file(path: str) -> str:
    """Read File

     # noqa: E501

    :param path: Path to file
    :type path: str

    :rtype: str
    """
    with open(path, "r") as f:
        return f.read()


def get_top_level_directories(source_path: str) -> List[str]:
    """
    Lists all directories under source_path, excluding any in ignore_folders.

    Args:
        ignore_folders (List[str]): List of directory names to ignore.
        only_toplevel (bool): If True, only return top-level directories.

    Returns:
        List[str]: List of directory paths to be indexed.
    """
    base_path = os.path.abspath(source_path)
    # Generate a set of absolute paths of the folders to ignore
    ignore_folders_paths = set()
    ignore_folders: List[str] = [
        "xahau",
        "node_modules",
        "dist",
        "build",
        ".github",
        ".git",
        ".venv",
        ".vscode",
        "__pycache__",
        "poetry.lock",
    ]
    for folder in ignore_folders:
        ignore_path = os.path.abspath(os.path.join(base_path, folder))
        ignore_folders_paths.add(ignore_path)

    for root, dirs, files in os.walk(source_path):
        root_path = os.path.abspath(root)
        # print(dirs)
        # Filter out directories we want to ignore
        dirs[:] = [
            d
            for d in dirs
            if os.path.abspath(os.path.join(root_path, d)) not in ignore_folders_paths
        ]
        print(dirs)
        # all_directories.append(root_path)
        return dirs
    return []


def list_all_files_dir(source_path: str) -> List[str]:
    """
    Lists all file paths in a directory and its subdirectories.

    Args:
        source_path (str): Path to the source directory.

    Returns:
        List[str]: List of file paths.
    """
    file_list = []
    # Walk through the directory tree
    for root, dirs, files in os.walk(source_path):
        # Iterate over the files in the current directory
        for file in files:
            # Construct the full file path
            file_path = os.path.join(root, file)
            # Add the file path to the list
            file_list.append(file_path)
    return file_list
