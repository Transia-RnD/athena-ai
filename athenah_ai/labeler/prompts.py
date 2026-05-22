"""
Prompt templates for AI Code Labeler documentation generation.
"""

# Prompt template for file documentation (using .ai.json metadata)
FILE_DOC_FROM_JSON_TEMPLATE = """You are a technical documentation expert. Create comprehensive, narrative documentation for this code file.

FILE METADATA:
File: {file_name}
Language: {language}
Description: {description}

CLASSES:
{classes_info}

FUNCTIONS:
{functions_info}

NAMESPACES:
{namespaces_info}

CORE PRINCIPLE:
This documentation REPLACES the source code with words. A developer who reads only this
document and never opens the source file must understand every function, every error path,
every branch, and every constant. If something exists in the source and is missing from
the doc, the doc is incomplete.

DOCUMENTATION REQUIREMENTS:
1. Start with a high-level overview of the file's purpose and role
2. Document EVERY function and method — name, purpose, parameters, return semantics
3. For each function, document every error/result code and the exact condition that triggers it
4. Document class/struct members and what state they hold
5. Name every constant, limit, and threshold — with its value or semantic meaning
6. Write as if explaining to a fellow developer who will never read the source
7. Include all implementation details: algorithms, patterns, edge cases, branch logic
8. Explain why certain design decisions were made (if apparent from the metadata)
9. Highlight dependencies and external interactions
10. Do NOT skip "minor" functions — small helpers often encode critical invariants

OUTPUT FORMAT:
- Write in markdown format
- Use inline code references like `ClassName` and `function_name()`
- Use code blocks sparingly for important patterns
- Natural prose as primary voice, but use subsections per function or logical group when the
  file has many functions
- Scale length to complexity: roughly 1 word per 2-3 lines of source. No fixed cap —
  completeness wins over brevity. A 100-line file needs ~50-100 words; a 1000-line file
  needs 400+ words

Generate the documentation now:
"""

# Prompt template for file documentation (using source code directly)
FILE_DOC_FROM_SOURCE_TEMPLATE = """You are a technical documentation expert. Create comprehensive, narrative documentation for this code file.

SOURCE CODE:
```{language}
{source_code}
```

FILE: {file_name}
LANGUAGE: {language}

CORE PRINCIPLE:
This documentation REPLACES the source code with words. A developer who reads only this
document and never opens the source file must understand every function, every error path,
every branch, and every constant. If something exists in the source and is missing from
the doc, the doc is incomplete.

DOCUMENTATION REQUIREMENTS:
1. Read through the code carefully — do not skip any function, however small
2. Start with a high-level overview of the file's purpose
3. Document EVERY function and method: name, purpose, parameters, return semantics
4. For each function, document every error/result code and the exact condition that triggers it
5. Document class/struct members and what state they hold
6. Name every constant, limit, and threshold — with its value or semantic meaning
7. Focus on WHAT the code does, HOW it works, and WHY (design rationale)
8. Explain all edge cases, branch logic, and error handling
9. Note dependencies and external interactions
10. Do NOT skip "minor" functions — small helpers often encode critical invariants

OUTPUT FORMAT:
- Markdown format
- Use inline code like `ClassName` and `function_name()`
- Use code blocks sparingly for important snippets
- Natural prose as primary voice, but use subsections per function or logical group when the
  file has many functions
- Scale length to complexity: roughly 1 word per 2-3 lines of source. No fixed cap —
  completeness wins over brevity

Generate the documentation now:
"""

# Prompt template for directory documentation
DIRECTORY_DOC_TEMPLATE = """You are a technical documentation expert. Create a human-readable overview of this directory.

DIRECTORY: {dir_name}
LOCATION: {relative_path}

DIRECTORY SUMMARY:
Purpose: {purpose}
Key Functionalities: {functionalities}
Main Files: {main_files}
Dependencies: {dependencies}

FILES IN DIRECTORY:
{files_list}

DOCUMENTATION REQUIREMENTS:
1. Write a narrative overview of what this directory contains
2. Explain the directory's role in the larger codebase
3. Describe key files and their purposes in natural prose
4. Explain how files in this directory work together
5. Note important patterns or architectural decisions
6. Keep it concise but informative (300-800 words)
7. Use natural language - avoid bullet lists and rigid structure
8. Write as if orienting a new developer to this part of the codebase

OUTPUT FORMAT:
- Markdown format
- Natural, flowing prose
- Use inline code references like `filename.cpp` or `ClassName`
- Conversational tone
- Focus on the "big picture" of what this directory does

Generate the directory overview now:
"""

# Prompt template for merging chunked documentation
CHUNK_MERGE_TEMPLATE = """You are a technical documentation expert. Merge these per-chunk documentation segments into a single, cohesive narrative.

FILE: {file_name}
CHUNKS: {num_chunks}

CHUNK DOCUMENTATION:
{chunk_docs}

MERGE REQUIREMENTS:
1. Create a unified, flowing narrative (not separate sections)
2. Eliminate redundancy between chunks
3. Ensure smooth transitions between concepts from different chunks
4. Maintain technical accuracy
5. Keep natural, conversational tone
6. Remove any chunk-specific references (like "this chunk covers...")

Generate the merged documentation:
"""
