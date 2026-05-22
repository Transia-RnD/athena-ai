#!/usr/bin/env python
# athenah_client.py - Simplified multi-LLM client with automatic RAG

from typing import Dict, Any, List, TypedDict, Union

from dotenv import load_dotenv

from langgraph.graph import START, StateGraph
from langsmith import Client as LangSmithClient
from langchain_core.documents import Document

from .llm_adapters import LLMProvider, LLMFactory, BaseLLMAdapter
from athenah_ai.client.vector_store import VectorStore
from athenah_ai.logger import logger

load_dotenv()


# Define state for RAG
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


class AthenahClient(VectorStore):
    """
    A simplified client for interacting with LLMs with automatic RAG support.

    Attributes:
        id (str): The ID of the client.
        provider (LLMProvider): The LLM provider to use.
        model_group (str): The model group directory for vector store.
        custom_model (str): The custom model name for vector store.
        version (str): The version of the vector store.
        model_name (str): The name of the LLM model.
        temperature (float): The temperature parameter for generating responses.
        max_tokens (int): The maximum number of tokens for generating responses.
        llm_adapter (BaseLLMAdapter): The LLM adapter instance.
        db: The vector store for document retrieval (None if not loaded).
    """

    def __init__(
        self,
        id: str,
        provider: Union[LLMProvider, str] = LLMProvider.OPENAI,
        model_group: str = "workspace",
        custom_model: str = "",
        version: str = "v1",
        model_name: str = None,
        temperature: float = 0,
        max_tokens: int = 8000,
        **kwargs,
    ):
        """
        Initialize the AthenahClient.

        Args:
            id (str): The ID of the client.
            provider (Union[LLMProvider, str]): The LLM provider to use.
            model_group (str): The model group directory for vector store.
            custom_model (str): The custom model name for vector store.
            version (str): The version of the vector store.
            model_name (str): The name of the LLM model.
            temperature (float): The temperature parameter for generating responses.
            max_tokens (int): The maximum number of tokens for generating responses.
            **kwargs: Additional arguments.
        """
        self.id = id
        self.provider = (
            LLMProvider(provider.lower()) if isinstance(provider, str) else provider
        )
        self.model_group = model_group
        self.custom_model = custom_model
        self.version = version
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Create LLM adapter
        self.llm_adapter = LLMFactory.create_adapter(
            self.provider, self.model_name, self.temperature, self.max_tokens
        )

        # Initialize parent class
        super().__init__(storage_type="local" if model_group == "workspace" else "gcs")

        # Initialize db to None
        self.db = None
        self._collection = None

        # Load vector store if custom model is provided
        if self.model_group and self.custom_model:
            try:
                self.db = self.load(self.custom_model, self.model_group, self.version)
                logger.info(f"Vector store loaded for {self.custom_model}")
            except Exception as e:
                logger.warning(f"Could not load vector store: {e}. Will use base LLM without RAG.")
                self.db = None

        # Initialize LangChain LLM
        self.llm = self.llm_adapter.get_langchain_llm()

    def ask(self, prompt: str, system: str = None) -> str:
        """
        Generate a response. Automatically uses RAG if vector store is available.

        Args:
            prompt (str): The question or prompt to respond to.
            system (str): Optional system message.

        Returns:
            str: The generated response.
        """
        # Check if vector store is available
        if self.db and self._collection:
            try:
                return self._ask_with_rag(prompt)
            except Exception as e:
                logger.warning(f"RAG failed: {e}. Falling back to base LLM.")
                return self._ask_base(system, prompt)
        else:
            return self._ask_base(system, prompt)

    def _ask_with_rag(self, prompt: str) -> str:
        """
        Generate a response using RAG (Retrieval-Augmented Generation).

        Args:
            prompt (str): The prompt to generate a response to.

        Returns:
            str: The generated response.
        """
        logger.info(f"Using RAG with {self._collection.count()} indexed documents")

        # Update LLM instance
        self.llm = self.llm_adapter.get_langchain_llm()

        # Pull RAG prompt from hub using LangSmith
        langsmith_client = LangSmithClient()
        rag_prompt = langsmith_client.pull_prompt("rlm/rag-prompt")

        def retrieve(state: State):
            # Manually compute query embedding using the same embedder
            query_embedding = self._embedder.embed_query(state["question"])

            retrieved_docs = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=4
            )

            # Convert ChromaDB results to Document objects
            documents = []
            if retrieved_docs and retrieved_docs['documents']:
                for doc_text in retrieved_docs['documents'][0]:
                    documents.append(Document(page_content=doc_text))

            return {"context": documents}

        def generate(state: State):
            docs_content = "\n\n".join(doc.page_content for doc in state["context"])
            messages = rag_prompt.invoke(
                {"question": state["question"], "context": docs_content}
            )
            response = self.llm.invoke(messages)
            return {"answer": response.content}

        # Create and run the graph
        graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()

        response = graph.invoke({"question": prompt})
        return response["answer"]

    def _ask_base(self, system: str = None, prompt: str = None) -> str:
        """
        Generate a response using the base LLM without RAG.

        Args:
            system (str): The system message (optional).
            prompt (str): The user prompt.

        Returns:
            str: The generated response.
        """
        logger.info("Using base LLM (no RAG)")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if prompt:
            messages.append({"role": "user", "content": prompt})

        return self.llm_adapter.create_completion(messages)
