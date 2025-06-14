import os
from langchain_openai import ChatOpenAI


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
                                "file": file_path,
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


def map_and_classify_symbols(word: str, folder: str, llm: ChatOpenAI, window=10):
    occurrences = find_word_with_context(word, folder, window)
    # for occ in occurrences:
    #     occ["classification"] = classify_symbol_with_llm(llm, word, occ["context"])
    return occurrences
