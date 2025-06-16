import os
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
from athenah_ai.client import AthenahClient


def find_word_with_context(word: str, txt_folder: str, window=10):
    """
    For each occurrence of 'word' in .txt files, return the file, line number,
    and a context window (window lines before and after).
    """
    results = []
    for root, dirs, files in os.walk(txt_folder):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    if word in line:
                        start = max(i - window, 0)
                        end = min(i + window + 1, len(lines))
                        context = "".join(lines[start:end])
                        results.append(
                            {
                                "symbol": word,
                                "file_path": file_path,
                                "lineno": i + 1,
                                "line": line.strip(),
                                "context": context,
                            }
                        )
    return results


def classify_symbol_with_llm(llm: ChatOpenAI, word: str, context: str):
    prompt = f"""
Given the following code context, what is '{word}'? 
Is it a class, function, argument, variable, or something else? 
Just answer with one word (Class, Function, Argument, Variable, Other) and a short explanation.

Context:
{context}
"""
    response = llm.invoke(prompt)
    return response.content.strip()


def score_symbols(client: AthenahClient, word: str, context: str):
    prompt = f"""
Score all of the symbols symbol '{word}' based on its context in the code.
"""
    response = client.base_prompt(prompt, context)
    return response


def symbol_to_source_occurances(word: str, folder: str, window=10):
    occurrences = find_word_with_context(word, folder, window)

    # if the path of the occurrence is not in the hints, lower the score by %
    symbol_map = []
    for occurrence in occurrences:
        file_path = occurrence["file_path"]
        symbol_map.append(
            {
                "symbol": word,
                "file_path": file_path,
                "lineno": occurrence["lineno"],
                "line": occurrence["line"],
                "context": occurrence["context"],
                "score": 0,
            }
        )

    # Filter the map. We want to combine duplicates and then create an array of { "lineno": [1, 2, 3], "line": "line of code" }

    def filter_and_combine(symbol_map: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        combined_map = {}
        for entry in symbol_map:
            key = (entry["symbol"], entry["file_path"])
            if key not in combined_map:
                combined_map[key] = {
                    "symbol": entry["symbol"],
                    "file_path": entry["file_path"],
                    "lineno": [],
                    "line": entry["line"],
                    "context": entry["context"],
                    "score": 0,
                }
            combined_map[key]["lineno"].append(entry["lineno"])
        
        return [
            {
                "symbol": v["symbol"],
                "file_path": v["file_path"],
                "lineno": v["lineno"],
                "line": v["line"],
                "context": v["context"],
                "score": v["score"],
            }
            for v in combined_map.values()
        ]
    return filter_and_combine(symbol_map)
