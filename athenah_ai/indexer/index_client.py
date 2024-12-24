#!/usr/bin/env python
# coding: utf-8

import os
from typing import List, Union
import shutil
from shutil import ignore_patterns

from basedir import basedir

from langchain_community.vectorstores import FAISS

from athenah_ai.indexer.cleaner import AthenahCleaner
from athenah_ai.indexer.base_index_client import BaseIndexClient
from athenah_ai.logger import logger


class IndexClient(BaseIndexClient):
    storage_type: str = "local"  # local or gcs
    id: str = ""
    dir: str = ""
    name: str = ""
    version: str = ""

    def __init__(
        cls, storage_type: str, id: str, dir: str, name: str, version: str = "v1"
    ) -> None:
        cls.storage_type = storage_type
        cls.id = id
        cls.dir = dir
        cls.name = name
        cls.version = version
        cls.dist_path: str = os.path.join(basedir, "dist")
        cls.base_path: str = os.path.join(basedir, dir)
        cls.name_path: str = os.path.join(cls.base_path, cls.name)
        cls.name_version_path: str = os.path.join(
            cls.base_path, f"{cls.name}-{cls.version}"
        )
        os.makedirs(cls.base_path, exist_ok=True)
        os.makedirs(cls.name_path, exist_ok=True)
        super().__init__(cls.storage_type, cls.id, cls.dir, cls.name, cls.version)

    def remove(cls, dest: str, is_dir: bool = False):
        if is_dir:
            shutil.rmtree(dest, ignore_errors=True)
        else:
            os.remove(dest)

    def copy(cls, source: str, dest: str, is_dir: bool = False):
        if is_dir:
            shutil.copytree(
                source,
                dest,
                dirs_exist_ok=True,
                ignore=ignore_patterns(
                    "node_modules*",
                    "dist*",
                    "build*",
                    ".git*",
                    ".venv*",
                    ".vscode*",
                    "__pycache__*",
                    "poetry.lock",
                ),
            )
        else:
            os.makedirs(dest, exist_ok=True)
            file_name: str = source.split("/")[-1]
            shutil.copyfile(source, f"{dest}/{file_name}")

    # def build_from_ignore(
    #     cls,
    #     name: str,
    #     ignore: Union[List[str], str] = None,
    # ):
    #     raise ValueError("unimplemented")
    #     _docs, _metadata = cls.build_from_dirs(ignore)
    #     store: FAISS = cls.store_from_docs(_docs, _metadata)
    #     cls.save(store)
    #     return store

    def prepare_whitelist(cls, source: str, dest_filepath: str):
        logger.info(f"DEST PATH: {dest_filepath}")
        cls.remove(dest_filepath, True)
        cls.copy(source, dest_filepath, True)

    def build_whitlist_from_dir(
        cls,
        source: str,
    ):
        source_name: str = f"{cls.name}-source"
        dest_filepath: str = os.path.join(cls.name_path, source_name)
        cls.prepare_whitelist(
            source,
            dest_filepath,
        )
        build_paths: List[str] = [f"{cls.name_path}/{source_name}"]
        [AthenahCleaner().clean_directory(filepath) for filepath in build_paths]
        _docs, _metadata = cls.build_from_dirs(build_paths)
        store: FAISS = cls.store_from_docs(_docs, _metadata)
        cls.save(store)
        return store

    def build_whitlist_from_dirs(
        cls,
        source: str,
        folders: Union[List[str], str] = None,
    ):
        source_name: str = f"{cls.name}-source"
        dest_filepath: str = os.path.join(cls.name_path, source_name)
        cls.prepare_whitelist(
            source,
            dest_filepath,
        )
        build_paths: List[str] = [f"{cls.name_path}/{source_name}/{f}" for f in folders]
        [AthenahCleaner().clean_directory(filepath) for filepath in build_paths]
        _docs, _metadata = cls.build_from_dirs(build_paths)
        store: FAISS = cls.store_from_docs(_docs, _metadata)
        cls.save(store)
        return store

    def build_from_file(cls, name: str, file_path: str):
        _docs, _metadata = cls.build_from_file(file_path)
        store: FAISS = cls.store_from_docs(_docs, _metadata)
        cls.save(store)
        return store
