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
from athenah_ai.client.vector_store import VectorStore
from athenah_ai.logger import logger
from langchain.agents import (
    AgentType,
    Tool,
    initialize_agent,
)
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.documents import Document

load_dotenv()

OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
OPENAI_API_MODEL: str = "gpt-4o"
MAX_TOKENS: int = 2000

MODEL_MAP = {
    "gpt-4o-mini": 16383,
    "gpt-4o": 4095,
    "gpt-4-turbo": 4095,
    "gpt-4": 8191,
}


def get_token_total(prompt: str) -> int:
    import tiktoken

    openai_model = OPENAI_API_MODEL
    encoding = tiktoken.encoding_for_model(openai_model)
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

    def conversation(cls, prompt: str) -> str:
        """
        Generates a response to the given prompt, using conversational memory.

        Args:
            prompt (str): The prompt to generate a response to.

        Returns:
            str: The generated response.
        """

        # Adjust the model if necessary based on token limits
        if MAX_TOKENS + get_token_total(prompt) > MODEL_MAP[cls.model_name]:
            cls.model_name = "gpt-4o"

        # Initialize the OpenAI LLM with the adjusted parameters
        cls.openai = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature,
            max_tokens=MAX_TOKENS + get_token_total(prompt),
            n=cls.best_of,
            # You can include other model kwargs if necessary
        )

        retriever = cls.db.as_retriever()

        # Create a ConversationalRetrievalChain that uses the memory
        chain = ConversationalRetrievalChain.from_llm(
            llm=cls.openai,
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

        if MAX_TOKENS + get_token_total(prompt) > MODEL_MAP[cls.model_name]:
            cls.model_name = "gpt-4o"

        cls.openai = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature,
            max_tokens=MAX_TOKENS + get_token_total(prompt),
            n=cls.best_of,
            # model_kwargs={
            #     "top_p": cls.top_p,
            #     "frequency_penalty": cls.frequency_penalty,
            #     "presence_penalty": cls.presence_penalty,
            # },
        )

        num_indexs = cls.db.index_to_docstore_id
        logger.info(f"DB INDEXS: {len(num_indexs)}")
        retriever = cls.db.as_retriever()

        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        question_answer_chain = create_stuff_documents_chain(
            cls.openai, retrieval_qa_chat_prompt
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

        if MAX_TOKENS + get_token_total(prompt) > MODEL_MAP[cls.model_name]:
            cls.model_name = "gpt-4o"

        cls.openai = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature,
            max_tokens=MAX_TOKENS + get_token_total(prompt),
            n=cls.best_of,
            # model_kwargs={
            #     "top_p": cls.top_p,
            #     "frequency_penalty": cls.frequency_penalty,
            #     "presence_penalty": cls.presence_penalty,
            # },
        )

        num_indexs = cls.db.index_to_docstore_id
        logger.info(f"DB INDEXS: {len(num_indexs)}")
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
            response = cls.openai.invoke(messages)
            return {"answer": response.content}

        graph_builder = StateGraph(State).add_sequence([retrieve, generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        response = graph.invoke({"question": prompt})
        return response["answer"]

    def base_prompt(cls, system: str = None, prompt: str = None) -> str:
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

            response = openai.chat.completions.create(
                model=cls.model_name,
                messages=messages,
                temperature=cls.temperature,
                max_tokens=cls.max_tokens,
                top_p=cls.top_p,
                n=cls.best_of,
                frequency_penalty=cls.frequency_penalty,
                presence_penalty=cls.presence_penalty,
            )
            assistant_reply = response.choices[0].message.content
            return assistant_reply
        except Exception as e:
            raise ValueError(f"failed to generate a prompt completion: {str(e)}")

    def agent_prompt(cls, name: str, description: str, prompt: str):
        tools = []
        cls.openai = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature,
            max_tokens=MAX_TOKENS + get_token_total(prompt),
            n=cls.best_of,
        )
        chain = RetrievalQA.from_llm(
            llm=cls.openai,
            retriever=cls.db.as_retriever(),
        )
        tools.append(
            Tool(
                name=name,
                func=chain.run,
                description=description,
            )
        )
        agent = initialize_agent(
            tools,
            cls.openai,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
        )
        return agent.run(prompt)

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
            "max_tokens": MAX_TOKENS,
            "temperature": 0,
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

        question_w_system: str = " ".join([msg["content"] for msg in messages])
        total_tokens: int = get_token_total(question_w_system)
        if MAX_TOKENS + total_tokens > MODEL_MAP[cls.model_name]:
            cls.model_name = "gpt-4o"

        cls.openai = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=cls.model_name,
            temperature=cls.temperature,
            max_tokens=MAX_TOKENS + total_tokens,
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
                    response = cls.openai.invoke(messages)
                    return {"answer": response.content}

                graph_builder = StateGraph(State).add_sequence([retrieve, generate])
                graph_builder.add_edge(START, "retrieve")
                graph = graph_builder.compile()
                response = graph.invoke({"question": question_w_system})
                keep_trying = False
            except Exception as e:
                # e.g. when the API is too busy, we don't want to fail everything
                print("Failed to generate response. Error: ", e)

                if retry_count > retry_limit:
                    raise ValueError("Failed to generate response after 10 retries.")

                import time

                time.sleep(30)
                print("Retrying...")

        # Get the reply from the API response
        reply = response["answer"]
        return reply
