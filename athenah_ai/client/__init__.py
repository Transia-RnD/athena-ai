#!/usr/bin/env python
# coding: utf-8


import os
from typing import Dict, Any, List, Tuple, TypedDict

from dotenv import load_dotenv

import openai

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langgraph.graph import START, StateGraph
from langchain import hub
from langchain.agents import (
    AgentType,
    Tool,
    initialize_agent,
)
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.documents import Document
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.graph import CompiledGraph

from athenah_ai.utils.agent import build_agent_tools
from athenah_ai.client.vector_store import VectorStore
from athenah_ai.logger import logger

load_dotenv()

OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
OPENAI_API_MODEL: str = "gpt-4.1"

MODEL_MAP = {
    "gpt-4o-mini": 16383,
    "gpt-4o": 4095,
    "gpt-4-turbo": 4095,
    "gpt-4": 8191,
    "gpt-4.1": 32768,
    "o4-mini": 100000,
}


def get_max_tokens(model_name: str) -> int:
    """
    Get the maximum number of tokens for a given OpenAI model.

    Args:
        model_name (str): The name of the OpenAI model.

    Returns:
        int: The maximum number of tokens for the model.
    """
    return MODEL_MAP.get(model_name, 4096)  # Default to 4096 if model not found


def get_token_total(prompt: str) -> int:
    import tiktoken

    openai_model = "gpt-4o-mini"
    encoding = tiktoken.encoding_for_model(openai_model)
    print(f"Total tokens for model {openai_model}: {len(encoding.encode(prompt))}")
    return len(encoding.encode(prompt))


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


class AthenahClient(VectorStore):
    """
    A client for interacting with the Athenah AI chat model.

    Attributes:
        id (str): The ID of the client.
        model_group (str): The model group to use for the chat model.
        custom_model (str): The custom model to use for the chat model.
        version (str): The version of the chat model.
        model_name (str): The name of the chat model.
        temperature (float): The temperature parameter for generating responses.
        max_tokens (int): The maximum number of tokens for generating responses.
        top_p (int): The top-p parameter for generating responses.
        best_of (int): The best-of parameter for generating responses.
        frequency_penalty (float): The frequency penalty parameter for generating
        responses.
        presence_penalty (float): The presence penalty parameter for generating
        responses.
        stop (List[str]): The list of stop words for generating responses.
        has_history (bool): Whether the client has chat history.
        chat_history (List[str]): The chat history of the client.
        db (FAISS): The FAISS vector store for document retrieval.
    """

    id: str = ""
    model_group: str = "dist"
    custom_model: str = ""
    version: str = "v1"
    model_name: str = OPENAI_API_MODEL
    temperature: float = 0
    max_tokens: int = 600
    top_p: int = 1
    best_of: int = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0
    stop: List[str] = []

    has_history: bool = False
    chat_history: List[Tuple[str, str]] = []
    memory: ConversationBufferMemory = None
    db: FAISS = None
    llm: ChatOpenAI = None

    def __init__(
        cls,
        id: str,
        model_group: str = "dist",
        custom_model: str = "",
        version: str = "v1",
        model_name: str = OPENAI_API_MODEL,
        temperature: float = 0,
        max_tokens: int = 1200,
        top_p: int = 1,
        best_of: int = 3,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop: List[str] = [],
    ):
        """
        Initializes the AthenahClient.

        Args:
            id (str): The ID of the client.
            model_group (str): The model group to use for the chat model.
            custom_model (str): The custom model to use for the chat model.
            version (str): The version of the chat model.
            model_name (str): The name of the chat model.
            temperature (float): The temperature parameter for generating responses.
            max_tokens (int): The maximum number of tokens for generating responses.
            top_p (int): The top-p parameter for generating responses.
            best_of (int): The best-of parameter for generating responses.
            frequency_penalty (float): The frequency penalty parameter for generating
            responses.
            presence_penalty (float): The presence penalty parameter for generating
            responses.
            stop (List[str]): The list of stop words for generating responses.
        """
        cls.id = id
        cls.model_group = model_group
        cls.custom_model = custom_model
        cls.version = version
        cls.model_name = model_name
        cls.temperature = temperature
        cls.max_tokens = max_tokens
        cls.top_p = top_p
        cls.best_of = best_of
        cls.frequency_penalty = frequency_penalty
        cls.presence_penalty = presence_penalty
        cls.stop = stop

        cls.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        super().__init__(storage_type="local" if model_group == "dist" else "gcs")

        if cls.model_group and cls.custom_model:
            cls.db = cls.load(cls.custom_model, cls.model_group, cls.version)

        pass

    def get_relevant_file_names(
        client: "AthenahClient", query: str, min_score: float = 0.5, max_files: int = 20
    ) -> List[str]:
        """
        Returns a list of file names (paths) of the most relevant documents in the vector index for a given query.

        Args:
            client (AthenahClient): The client instance with a loaded FAISS db.
            query (str): The search query or functionality description.
            min_score (float): Minimum similarity score (0-1) to consider a document relevant.
            max_files (int): Maximum number of files to return.

        Returns:
            List[str]: List of file paths for the most relevant documents.
        """
        try:
            # Run similarity search with scores
            results = client.db.similarity_search(query, k=500)
            import json

            results = json.loads(results) if isinstance(results, str) else results
            # print(results[0])
            # results: List[Tuple[Document, float]]
            # Filter by min_score and sort by score descending
            # filtered = [
            #     (doc)
            #     for doc in results
            #     # if score >= min_score
            #     and hasattr(doc.metadata, "get")
            #     and doc.metadata.get("source")
            # ]
            # Sort by score descending
            # results.sort(key=lambda x: x[1], reverse=True)
            # Extract file paths (assuming 'source' in metadata is the file path)
            file_paths = []
            for doc in results:
                # print(doc)
                file_path = doc.metadata.get("file_path")
                if file_path and file_path not in file_paths:
                    file_paths.append(
                        {
                            "path": file_path,
                            "content": doc.page_content,
                        }
                    )
                if len(file_paths) >= max_files:
                    break
            return file_paths
        except Exception as e:
            logger.error(f"Error in get_relevant_file_names: {e}")
            return []

    def init_llm(cls):
        # Initialize the OpenAI LLM with the adjusted parameters
        cls.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature if cls.model_name != 'o4-mini' else 1,
            max_tokens=get_max_tokens(cls.model_name),
            n=cls.best_of,
            # You can include other model kwargs if necessary
        )

    def conversation(cls, prompt: str) -> str:
        """
        Generates a response to the given prompt, using conversational memory.

        Args:
            prompt (str): The prompt to generate a response to.

        Returns:
            str: The generated response.
        """

        # Adjust the model if necessary based on token limits
        if get_token_total(prompt) > MODEL_MAP[cls.model_name]:
            print('Using o4-mini model due to token limit.')
            cls.model_name = "o4-mini"

        # Initialize the OpenAI LLM with the adjusted parameters
        cls.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature if cls.model_name != 'o4-mini' else 1,
            max_tokens=get_max_tokens(cls.model_name),
            n=cls.best_of,
            # You can include other model kwargs if necessary
        )

        retriever = cls.db.as_retriever()

        # Create a ConversationalRetrievalChain that uses the memory
        chain = ConversationalRetrievalChain.from_llm(
            llm=cls.llm,
            retriever=retriever,
            memory=cls.memory,
            verbose=True,  # Set to False if you don't want verbose output
        )

        # Generate the response using the chain
        response = chain({"question": prompt})
        assistant_reply = response["answer"]

        # Append the user prompt and assistant's reply to the chat history
        cls.chat_history.append((prompt, assistant_reply))

        # The memory is automatically updated within the chain
        return assistant_reply

    def promptv1(cls, prompt: str) -> str:
        """
        Generates a response to the given prompt.

        Args:
            prompt (str): The prompt to generate a response to.

        Returns:
            str: The generated response.
        """

        if get_token_total(prompt) > MODEL_MAP[cls.model_name]:
            print('PROMPT V1: Using o4-mini model due to token limit.')
            cls.model_name = "o4-mini"

        cls.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature if cls.model_name != 'o4-mini' else 1,
            max_tokens=get_max_tokens(cls.model_name),
            n=cls.best_of,
            # model_kwargs={
            #     "top_p": cls.top_p,
            #     "frequency_penalty": cls.frequency_penalty,
            #     "presence_penalty": cls.presence_penalty,
            # },
        )

        num_indexs = cls.db.index_to_docstore_id
        logger.debug(f"DB INDEXS: {len(num_indexs)}")
        retriever = cls.db.as_retriever()

        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        question_answer_chain = create_stuff_documents_chain(
            cls.llm, retrieval_qa_chat_prompt
        )
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        response = rag_chain.invoke({"input": prompt})
        return response["answer"]

    def prompt(cls, prompt: str) -> str:
        """
        Generates a response to the given prompt.

        Args:
            prompt (str): The prompt to generate a response to.

        Returns:
            str: The generated response.
        """

        if get_token_total(prompt) > MODEL_MAP[cls.model_name]:
            print('PROMPT: Using o4-mini model due to token limit.')
            cls.model_name = "o4-mini"

        cls.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature if cls.model_name != 'o4-mini' else 1,
            max_tokens=get_max_tokens(cls.model_name),
            n=cls.best_of,
            # model_kwargs={
            #     "top_p": cls.top_p,
            #     "frequency_penalty": cls.frequency_penalty,
            #     "presence_penalty": cls.presence_penalty,
            # },
        )

        num_indexs = cls.db.index_to_docstore_id
        logger.debug(f"DB INDEXS: {len(num_indexs)}")
        # retriever = cls.db.as_retriever()

        # similar_docs = cls.db.similarity_search_with_relevance_scores(
        #     "invoke_calculateBaseFee", k=3
        # )
        # print(similar_docs)
        rag_prompt = hub.pull("rlm/rag-prompt")

        def retrieve(state: State):
            retrieved_docs = cls.db.similarity_search(state["question"])
            return {"context": retrieved_docs}

        def generate(state: State):
            docs_content = "\n\n".join(doc.page_content for doc in state["context"])
            messages = rag_prompt.invoke(
                {"question": state["question"], "context": docs_content}
            )
            response = cls.llm.invoke(messages)
            return {"answer": response.content}

        graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        response = graph.invoke({"question": prompt})
        return response["answer"]

    def base_prompt(cls, system: str = None, prompt: str = None, *args) -> str:
        """
        Generates a response to the given system and prompt.

        Args:
            system (str): The system message.
            prompt (str): The user prompt.

        Returns:
            str: The generated response.
        """
        try:
            messages: List[Dict[str, Any]] = []
            if isinstance(system, str) and system != "":
                messages.append({"role": "system", "content": system})
            if isinstance(prompt, str) and prompt != "":
                messages.append({"role": "user", "content": prompt})

            for arg in args:
                if isinstance(arg, dict):
                    messages.append(arg)

            response = openai.chat.completions.create(
                model=cls.model_name,
                messages=messages,
                temperature=cls.temperature if cls.model_name != 'o4-mini' else 1,
                max_tokens=cls.max_tokens,
                # top_p=cls.top_p,
                n=cls.best_of,
                # frequency_penalty=cls.frequency_penalty,
                # presence_penalty=cls.presence_penalty,
            )
            assistant_reply = response.choices[0].message.content
            return assistant_reply
        except Exception as e:
            raise ValueError(f"failed to generate a prompt completion: {str(e)}")

    def _base_prompt(cls, messages) -> str:
        """
        Generates a response to the given system and prompt.

        Args:
            system (str): The system message.
            prompt (str): The user prompt.

        Returns:
            str: The generated response.
        """
        try:
            response = openai.chat.completions.create(
                model=cls.model_name,
                messages=messages,
                temperature=cls.temperature if cls.model_name != 'o4-mini' else 1,
                max_tokens=cls.max_tokens,
                # top_p=cls.top_p,
                n=cls.best_of,
                # frequency_penalty=cls.frequency_penalty,
                # presence_penalty=cls.presence_penalty,
            )
            assistant_reply = response.choices[0].message.content
            return assistant_reply
        except Exception as e:
            raise ValueError(f"failed to generate a prompt completion: {str(e)}")

    def agent_prompt(
        cls,
        name: str,
        description: str,
        prompt: str,
        tools: List[Tool] = [],
        add_default_tools: bool = True,
    ) -> str:
        """
        Runs an agent with the provided tools and prompt.

        Args:
            prompt (str): The user prompt.
            tools (List[Tool], optional): List of langchain Tool objects. If None, will use default tools.
            name (str, optional): Name for the agent tool (if using RetrievalQA).
            description (str, optional): Description for the agent tool.
            add_default_tools (bool, optional): Whether to add default tools (vector search, Google, file read).

        Returns:
            str: The agent's response.
        """
        try:
            cls.llm = ChatOpenAI(
                openai_api_key=OPENAI_API_KEY,
                model_name=cls.model_name,
                temperature=cls.temperature if cls.model_name != 'o4-mini' else 1,
                max_tokens=get_max_tokens(cls.model_name),
                n=cls.best_of,
            )

            def read_file(path: str) -> str:
                try:
                    with open(path, "r") as f:
                        return f.read()
                except Exception as e:
                    logger.error(f"Error reading file {path}: {e}")
                    return ""

            default_tools = []
            if add_default_tools:
                default_tools.extend(
                    [
                        Tool(
                            name="Read a file",
                            func=read_file,
                            description="Read a file from a path. Include the full path to the file.",
                        ),
                    ]
                )
                if cls.custom_model:
                    try:
                        chain = RetrievalQA.from_llm(
                            llm=cls.llm,
                            retriever=cls.db.as_retriever(),
                        )
                        default_tools.append(
                            Tool(
                                name=name,
                                func=chain.run,
                                description=description,
                            )
                        )
                        default_tools.append(
                            Tool(
                                name="Search",
                                func=cls.db.similarity_search,
                                description="Search the vector store for relevant documents.",
                            )
                        )
                    except Exception as e:
                        logger.error(f"Error initializing RetrievalQA: {e}")
                else:
                    default_tools.extend(
                        [
                            Tool(
                                name="AI LLM",
                                func=cls.base_prompt,
                                description="Use the AI llm to generate a response based on the provided prompt.",
                            ),
                        ]
                    )

            all_tools = []
            if tools is not None:
                all_tools.extend(tools)
            if add_default_tools:
                all_tools.extend(default_tools)

            if not all_tools:
                raise ValueError("No tools provided to the agent.")

            agent = initialize_agent(
                all_tools,
                cls.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
            )
            return agent.invoke(prompt)
        except Exception as e:
            logger.error(f"Error in agent_prompt: {e}")
            return f"Agent failed: {e}"

    def agent_promptv2(
        cls,
        system: str,
        user_input: str,
    ) -> str:
        try:
            def callback(graph, data):
                ai_response: str = data.content
                print(f"AI Response: {ai_response}")

            # jarvis_response = brain.response_classifier.invoke(user_input)

            tools = build_agent_tools(["read_file"], "athenah_ai/utils")
            graph = create_react_agent(cls.llm, tools, checkpointer=MemorySaver())

            config = {"configurable": {"thread_id": "thread-1", "user_id": "1"}}

            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user_input},
            ]

            def from_messages_to_tuple(messages: List[Any]) -> Tuple[str, str]:
                    return [(m['type'], m['content']) for m in messages]
            
            inputs = {"messages": from_messages_to_tuple(messages)}
            print("START STREAM")

            def stream(
                graph: CompiledGraph,
                inputs: Any,
                config: Dict[str, Any],
                callback: Any = None,
            ):
                for s in graph.stream(inputs, config, stream_mode="values"):
                    try:
                        callback(graph, s["messages"][-1])
                    except Exception as e:
                        logger.error(f"Error in do stream: {e}")
                        pass
            while True:
                stream(graph, inputs, config, callback)
                break
            print("END STREAM")
        except Exception as e:
            logger.error(f"Error in agent_prompt: {e}")
            return f"Agent failed: {e}"

    def promptv3(system_prompt, user_prompt, *args):
        messages = []
        messages.append({"role": "system", "content": system_prompt})
        get_token_total(system_prompt)
        messages.append({"role": "user", "content": user_prompt})
        get_token_total(user_prompt)
        # loop thru each arg and add it to messages alternating role between "assistant" and "user"
        # role = "assistant"
        # {"role": role, "content": value}
        # role = "user" if role == "assistant" else "assistant"
        for value in args:
            messages.append(value)
            get_token_total(value["content"])

        params = {
            "model": OPENAI_API_MODEL,
            "messages": messages,
            "max_tokens": get_max_tokens(OPENAI_API_MODEL),
            "temperature": 1 if OPENAI_API_MODEL == 'o4-mini' else 0,
        }

        # Send the API request
        keep_trying = True
        while keep_trying:
            try:
                response = openai.ChatCompletion.create(**params)
                keep_trying = False
            except Exception as e:
                # e.g. when the API is too busy, we don't want to fail everything
                print("Failed to generate response. Error: ", e)
                import time

                time.sleep(30)
                print("Retrying...")

        # Get the reply from the API response
        reply = response.choices[0]["message"]["content"]
        return reply

    def rag_prompt_v2(cls, system_prompt, user_prompt, *args):
        messages = []
        messages.append({"role": "system", "content": system_prompt})
        print(f"System prompt: {system_prompt}")
        get_token_total(system_prompt)
        messages.append({"role": "user", "content": user_prompt})
        print(f"User prompt: {user_prompt}")
        get_token_total(user_prompt)
        # loop thru each arg and add it to messages alternating role between "assistant" and "user"
        # role = "assistant"
        # {"role": role, "content": value}
        # role = "user" if role == "assistant" else "assistant"
        for value in args:
            messages.append(value)
            get_token_total(value["content"])

        print(f"# Messages: {len(messages)}")

        question_w_system: str = " ".join([msg["content"] for msg in messages])
        total_tokens: int = get_token_total(question_w_system)
        if total_tokens > MODEL_MAP[cls.model_name]:
            print('RAG PROMPT V2: Using o4-mini model due to token limit.')
            cls.model_name = "o4-mini"

        cls.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            # temperature=cls.temperature if cls.model_name != 'o4-mini' else 1,
            max_tokens=get_max_tokens(cls.model_name),
            n=cls.best_of,
            # model_kwargs={
            #     "top_p": cls.top_p,
            #     "frequency_penalty": cls.frequency_penalty,
            #     "presence_penalty": cls.presence_penalty,
            # },
        )

        # Send the API request
        keep_trying = True
        retry_count = 0
        retry_limit = 10
        while keep_trying:
            try:
                rag_prompt = hub.pull("rlm/rag-prompt")

                def retrieve(state: State):
                    retrieved_docs = cls.db.similarity_search(state["question"])
                    return {"context": retrieved_docs}

                def generate(state: State):
                    docs_content = "\n\n".join(
                        doc.page_content for doc in state["context"]
                    )
                    messages = rag_prompt.invoke(
                        {"question": state["question"], "context": docs_content}
                    )
                    response = cls.llm.invoke(messages)
                    return {"answer": response.content}

                graph_builder = StateGraph(State).add_sequence([retrieve, generate])
                graph_builder.add_edge(START, "retrieve")
                graph = graph_builder.compile()
                response = graph.invoke({"question": question_w_system})
                keep_trying = False
            except Exception as e:
                # e.g. when the API is too busy, we don't want to fail everything
                print("Failed to generate response. Error: ", e)
                print(OPENAI_API_MODEL)

                if retry_count > retry_limit:
                    raise ValueError("Failed to generate response after 10 retries.")

                import time

                time.sleep(30)
                print("Retrying...")

        # Get the reply from the API response
        reply = response["answer"]
        return reply
