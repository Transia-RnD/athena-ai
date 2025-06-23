#!/usr/bin/env python
# coding: utf-8

import os
from typing import Dict, Any, List, Tuple
import shutil
import faiss
import pickle

from basedir import basedir
from dotenv import load_dotenv

from unstructured.file_utils.filetype import FileType, detect_filetype
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import Language
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from google.cloud.storage.bucket import Bucket, Blob
from athenah_ai.libs.google.storage import GCPStorageClient

from athenah_ai.client import AthenahClient
from athenah_ai.indexer.splitters import code_splitter, text_splitter
from athenah_ai.logger import logger

load_dotenv()

OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")
EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL")
CHUNK_SIZE: int = int(os.environ.get("CHUNK_SIZE", 2000))
GCP_INDEX_BUCKET: str = os.environ.get("GCP_INDEX_BUCKET", "athenah-ai-indexes")
chunk_overlap: int = 0


def summarize_file(content: str):
    client = AthenahClient(id="id", model_name="gpt-3.5-turbo-16k")
    response = client.base_prompt(
        """
            Describe and summarize what this document says.
            Be very specific.
            Everything must be documented.
            Keep it very short and concise,
            this will be used for labeling a vector search.
            """,
        content,
    )
    return response


# def extract_functions(content: str, file_type: str):
#         client = AthenahClient(id='id', model_name="gpt-3.5-turbo-16k")
#         response = client.base_prompt(
#             f"""
#             Describe what each function in this {file_type} code does.
#             Be very specific.
#             Every function must be documented.
#             If there are no actual functions then return "None"
#             """,
#             content,
#         )
#         return response


def prepare_dir(
    root: str, save_path: str = None, recursive: bool = False
) -> Tuple[List[str], List[str]]:
    splited_docs: List[str] = []
    splited_metadatas: List[str] = []

    logger.debug(f"PREPARE DIR: {root}")
    logger.debug(f"PREPARE DIR: {recursive}")
    loader = DirectoryLoader(
        root,
        silent_errors=True,
        recursive=recursive,
        exclude=["**/node_modules/**", "**/*.ai.json"],
    )
    docs = loader.load()

    def load_ai_json_metadata(root):
        ai_metadata = {}
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith(".ai.json"):
                    path = os.path.join(dirpath, filename)
                    with open(path, "r") as f:
                        import json

                        data = json.load(f)
                    # The real file this metadata describes
                    real_file = data.get("file_path")
                    if real_file:
                        ai_metadata[os.path.abspath(real_file)] = data
        return ai_metadata

    ai_metadata = load_ai_json_metadata(root)

    for doc in docs:
        real_path = os.path.abspath(
            doc.metadata.get("source", doc.metadata.get("file_path", ""))
        )
        if real_path in ai_metadata:
            # Merge the ai.json metadata into the document's metadata
            doc.metadata.update(ai_metadata[real_path])

    for doc in docs:
        doc.metadata["source"] = doc.metadata["source"].strip(".txt")

    logger.debug(f"DOCS #: {len(docs)}")
    for doc in docs:
        language = None
        file_summary = None
        functions = None
        file_name: str = doc.metadata["source"]
        logger.debug(file_name)

        if ".cpp" in file_name or ".h" in file_name:
            file_type = "cpp"
            language = Language.CPP
        elif ".js" in file_name:
            file_type = "js"
            language = Language.JS
        elif ".ts" in file_name:
            file_type = "ts"
            language = Language.TS
        elif ".py" in file_name:
            file_type = "py"
            language = Language.PYTHON
        else:
            file_type = "text"

        if language:
            splitter: RecursiveCharacterTextSplitter = code_splitter(
                language,
                chunk_size=CHUNK_SIZE,
                chunk_overlap=chunk_overlap,
            )
        else:
            splitter: RecursiveCharacterTextSplitter = text_splitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=chunk_overlap,
            )

        splits = splitter.split_text(doc.page_content)
        for index, split in enumerate(splits):
            if split.strip():
                chunk_metadata = {
                    "file_path": file_name,
                    "file_name": file_name.split("/")[-1],
                    "file_type": file_type,
                    "chunk_index": index,
                    "total_chunks": len(splits),
                }
                if file_summary:
                    chunk_metadata["file_summary"] = file_summary
                if functions:
                    chunk_metadata["functions"] = functions

                splited_docs.append(split)
                splited_metadatas.append(chunk_metadata)
                # Save split to file: cls.name_version_path
                if save_path:
                    split_file_path = os.path.join(save_path, f"split_{index}.txt")
                    with open(split_file_path, "w") as split_file:
                        split_file.write(split)

    return splited_docs, splited_metadatas


def prepare_file(file: str, save_path: str = None) -> Dict[str, Any]:
    logger.debug(f"PREPARE FILE: {file}")
    language = None
    file_summary = None
    functions = None
    file_name: str = file.split("/")[-1]

    if ".h" in file_name:
        file_type = "h"
        language = Language.CPP
    if ".cpp" in file_name:
        file_type = "cpp"
        language = Language.CPP
    elif ".js" in file_name:
        file_type = "js"
        language = Language.JS
    elif ".ts" in file_name:
        file_type = "ts"
        language = Language.TS
    elif ".py" in file_name:
        file_type = "py"
        language = Language.PYTHON
    else:
        file_type = "text"

    if language:
        splitter: RecursiveCharacterTextSplitter = code_splitter(
            language,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=chunk_overlap,
        )
    else:
        splitter: RecursiveCharacterTextSplitter = text_splitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=chunk_overlap,
        )

    with open(file, "r") as f:
        content = f.read()
    splits = splitter.split_text(content)
    splited_docs: List[str] = []
    splited_metadatas: List[str] = []
    for index, split in enumerate(splits):
        if split.strip():
            chunk_metadata = {
                "file_name": file_name,
                "file_path": file,
                "file_type": file_type,
                "chunk_index": index,
                "total_chunks": len(splits),
            }
            if file_summary:
                chunk_metadata["file_summary"] = file_summary
            if functions:
                chunk_metadata["functions"] = functions

            splited_docs.append(split)
            splited_metadatas.append(chunk_metadata)
            # Save split to file: cls.name_version_path
            if save_path:
                split_file_path = os.path.join(save_path, f"split_{index}.txt")
                with open(split_file_path, "w") as split_file:
                    split_file.write(split)

    return splited_docs, splited_metadatas


class BaseIndexClient(object):
    storage_type: str = "local"  # local or gcs
    id: str = ""
    name: str = ""
    version: str = ""

    splited_docs: List[str] = []
    splited_metadatas: List[str] = []

    def __init__(
        cls, storage_type: str, id: str, dir: str, name: str, version: str = "v1"
    ) -> None:
        cls.storage_type = storage_type
        cls.id = id
        cls.name = name
        cls.version = version
        cls.base_path: str = os.path.join(basedir, dir)
        cls.name_path: str = os.path.join(cls.base_path, cls.name)
        cls.name_source_path: str = os.path.join(cls.name_path, f"{cls.name}-source")
        cls.name_version_path: str = os.path.join(
            cls.base_path, f"{cls.name}-{cls.version}"
        )
        os.makedirs(cls.name_version_path, exist_ok=True)
        cls.splited_docs: List[str] = []
        cls.splited_metadatas: List[str] = []
        if cls.storage_type == "gcs":
            cls.storage_client: GCPStorageClient = GCPStorageClient().add_client()
            cls.bucket: Bucket = cls.storage_client.init_bucket(GCP_INDEX_BUCKET)
        pass

    def copy(cls, source: str, destination: str, is_dir: bool = False):
        if is_dir:
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copyfile(source, destination)

    # def build_one(cls):
    #     embedder = OpenAIEmbeddings(
    #         openai_api_key=OPENAI_API_KEY,
    #         model=EMBEDDING_MODEL,
    #         chunk_size=CHUNK_SIZE,
    #     )

    #     return FAISS.from_texts(
    #         cls.splited_docs, embedding=embedder, metadatas=cls.splited_metadatas
    #     )

    def _build_from_dirs(
        cls, source: str, dirs: List[str], include_root: bool
    ) -> Tuple[List[str], List[str]]:
        _splitted_docs: List[str] = []
        _splited_metadatas: List[str] = []
        for dir in dirs:
            splited_docs, splited_metadatas = prepare_dir(
                dir, cls.name_version_path, True
            )
            logger.debug(f"Adding Splitted Docs #: {len(splited_docs)}")
            logger.debug(f"Adding Splitted Metadatas #: {len(splited_metadatas)}")
            _splitted_docs.extend(splited_docs)
            _splited_metadatas.extend(splited_metadatas)
            logger.debug(f"Total Splitted Docs #: {len(_splitted_docs)}")
            logger.debug(f"Total Splitted Metadatas #: {len(_splited_metadatas)}")
        # if include_root:
        #     splited_docs, splited_metadatas = prepare_dir(
        #         source, cls.name_version_path, False
        #     )

        return _splitted_docs, _splited_metadatas

    def _build_from_files(cls, file_paths: List[str]) -> Tuple[List[str], List[str]]:
        _splitted_docs: List[str] = []
        _splited_metadatas: List[str] = []
        for file_path in file_paths:
            splited_docs, splited_metadatas = prepare_file(
                file_path, cls.name_version_path
            )
            logger.debug(f"Adding Splitted Docs #: {len(splited_docs)}")
            logger.debug(f"Adding Splitted Metadatas #: {len(splited_metadatas)}")
            _splitted_docs.extend(splited_docs)
            _splited_metadatas.extend(splited_metadatas)
            logger.debug(f"Total Splitted Docs #: {len(_splitted_docs)}")
            logger.debug(f"Total Splitted Metadatas #: {len(_splited_metadatas)}")

        return _splitted_docs, _splited_metadatas

    def store_from_docs(cls, splited_docs: List[str], splited_metadatas: List[str]):
        embedder = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY,
            model=EMBEDDING_MODEL,
            chunk_size=CHUNK_SIZE,
        )
        logger.debug(f"Splitted Docs #: {len(splited_docs)}")
        logger.debug(f"Splitted Metadatas #: {len(splited_metadatas)}")
        return FAISS.from_texts(
            splited_docs, embedding=embedder, metadatas=splited_metadatas
        )

    def save(
        cls,
        store: FAISS = None,
    ) -> bool:
        if cls.storage_type == "local":
            logger.debug("SAVING LOCAL FAISS")
            store.save_local(cls.name_version_path)
            return True

        if cls.storage_type == "gcs":
            logger.debug("SAVING GCS FAISS")
            data_byte_array = pickle.dumps((store.docstore, store.index_to_docstore_id))
            blob: Blob = cls.bucket.blob(f"{cls.name}/{cls.version}/index.pkl")
            blob.upload_from_string(data_byte_array)
            temp_file_name = "/tmp/index.faiss"
            faiss.write_index(store.index, temp_file_name)
            blob: Blob = cls.bucket.blob(f"{cls.name}/{cls.version}/index.faiss")
            blob.upload_from_filename(temp_file_name)
            return True
