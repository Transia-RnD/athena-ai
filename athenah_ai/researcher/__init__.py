import os
import openai
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from athenah_ai.logger import logger

# --- Utility Functions ---

def safe_get_env(key: str, default: str = "") -> str:
    value = os.environ.get(key, default)
    if not value:
        logger.warning(f"Environment variable {key} not set, using default: {default}")
    return value

def safe_run(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}")
        return None

def get_token_total(prompt: str, model: str = "gpt-4o-mini") -> int:
    import tiktoken
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(prompt))
    except Exception as e:
        logger.error(f"Token count error: {e}")
        return 0

def get_max_tokens(model_name: str) -> int:
    MODEL_MAP = {
        "gpt-4o-mini": 16383,
        "gpt-4o": 4095,
        "gpt-4-turbo": 4095,
        "gpt-4": 8191,
        "gpt-4.1": 32768,
        "o4-mini": 100000,
    }
    return MODEL_MAP.get(model_name, 4096)

# --- AthenahClient (Refactored) ---

class AthenahClient:
    def __init__(
        self,
        model_name: str = "gpt-4.1",
        temperature: float = 0,
        max_tokens: int = 1200,
        best_of: int = 3,
    ):
        load_dotenv()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.best_of = best_of
        self.api_key = safe_get_env("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def base_prompt(self, system: str, prompt: str, *args) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if prompt:
            messages.append({"role": "user", "content": prompt})
        for arg in args:
            if isinstance(arg, dict):
                messages.append(arg)
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                n=self.best_of,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"base_prompt error: {e}")
            return f"Error: {e}"

# --- ResearcherClient (New) ---

class ResearcherClient:
    def __init__(self, athenah_client: Optional[AthenahClient] = None):
        self.athenah = athenah_client or AthenahClient()
        self.llm = ChatOpenAI(
            openai_api_key=self.athenah.api_key,
            model_name=self.athenah.model_name,
            temperature=self.athenah.temperature,
            max_tokens=get_max_tokens(self.athenah.model_name),
            n=self.athenah.best_of,
        )

    def find_place_info(self, place: str) -> str:
        system = "You are a world-class researcher. Find all relevant information about the given place."
        prompt = f"Research and summarize all important facts, people, and events related to: {place}"
        return self.athenah.base_prompt(system, prompt)

    def extract_threads(self, info: str) -> List[str]:
        system = "Extract all unique names, organizations, or leads from the following text. Return as a list."
        prompt = info
        result = self.athenah.base_prompt(system, prompt)
        # Try to parse as list, fallback to splitting lines
        try:
            import ast
            leads = ast.literal_eval(result)
            if isinstance(leads, list):
                return [str(x) for x in leads]
        except Exception:
            return [line.strip() for line in result.splitlines() if line.strip()]
        return []

    def research_thread(self, thread: str) -> str:
        system = "You are a research assistant. Deeply investigate the following lead and provide a detailed summary."
        prompt = thread
        return self.athenah.base_prompt(system, prompt)

    def research_place(self, place: str) -> Dict[str, Any]:
        info = safe_run(self.find_place_info, place)
        if not info:
            return {"error": "Failed to find place info."}
        threads = safe_run(self.extract_threads, info)
        if not threads:
            return {"info": info, "threads": [], "results": {}}
        results = {}
        for thread in threads:
            results[thread] = safe_run(self.research_thread, thread)
        return {"info": info, "threads": threads, "results": results}

    def agent_research(self, place: str) -> Dict[str, Any]:
        # Use langchain agent tools if needed, fallback to LLM
        info = self.find_place_info(place)
        threads = self.extract_threads(info)
        results = {}
        for thread in threads:
            tools = [
                Tool(
                    name="LLM Research",
                    func=lambda q: self.athenah.base_prompt(
                        "You are a research assistant.", q
                    ),
                    description="Use LLM to research any topic.",
                )
            ]
            agent = initialize_agent(
                tools,
                self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False,
                handle_parsing_errors=True,
            )
            try:
                results[thread] = agent.invoke(thread)
            except Exception as e:
                logger.error(f"Agent error for thread '{thread}': {e}")
                results[thread] = f"Agent error: {e}"
        return {"info": info, "threads": threads, "results": results}

# --- Example Usage ---

# if __name__ == "__main__":
#     researcher = ResearcherClient()
#     place = "Silicon Valley"
#     result = researcher.research_place(place)
#     print(result)