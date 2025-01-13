#!/usr/bin/env python
# coding: utf-8

import os
from typing import List

from basedir import basedir
from dotenv import load_dotenv

from athenah_ai.indexer.index_client import IndexClient
from athenah_ai.logger import logger

from langchain_community.vectorstores import FAISS

load_dotenv()


class AthenahIndexer(IndexClient):
    storage_type: str = "local"  # local or gcs
    id: str = ""
    dir: str = ""
    name: str = ""
    version: str = ""

    def __init__(
        cls,
        storage_type: str,
        id: str,
        dir: str,
        name: str,
        version: str,
    ):
        cls.storage_type = storage_type
        cls.id = id
        cls.dir = dir
        cls.name = name
        cls.version = version
        super().__init__(cls.storage_type, cls.id, cls.dir, cls.name, cls.version)
        pass

    def index_file(cls, file_path: str, name: str, full: bool = False):
        source_name: str = f"{name}-source"
        dest_filepath: str = os.path.join(basedir, f"dist/{name}/{source_name}")
        logger.debug(f"STORAGE: {cls.storage_type}")
        logger.debug(f"NAME: {name}")
        logger.debug(f"FILE PATH: {file_path}")
        logger.debug(f"DEST PATH: {dest_filepath}")
        cls.remove(dest_filepath, True)
        cls.copy(file_path, dest_filepath, False)
        cls.build(source_name, dest_filepath, full)

    def index_whitelist(
        cls,
        source: str,
        dirs: List[str],
        name: str,
    ):
        logger.debug(f"STORAGE: {cls.storage_type}")
        logger.debug(f"NAME: {name}")
        logger.debug(f"SOURCE: {source}")
        if dirs == ["."]:
            cls.build_whitlist_from_dir(source, dirs)
            return

        cls.build_whitlist_from_dirs(source, dirs)
