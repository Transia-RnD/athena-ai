#!/usr/bin/env python3
"""
Diff Chunker for AI Models
Splits large diffs into manageable chunks while preserving context and structure.
Filters to only process C++ source and header files.
"""

import ast
import re
from typing import List, Tuple, Optional
from dataclasses import dataclass
from athenah_ai.utils.tokens import get_token_total


@dataclass
class DiffChunk:
    """Represents a chunk of a diff with metadata."""

    content: str
    file_path: Optional[str]
    chunk_index: int
    total_chunks: int
    token_count: int
    char_count: int


class DiffChunker:
    """Chunks diffs into sizes suitable for AI model processing."""

    def __init__(
        self,
        max_tokens: int = 4000,
        chars_per_token: float = 4.0,
        preserve_file_boundaries: bool = True,
        include_context_lines: int = 3,
    ):
        """
        Initialize the DiffChunker.

        Args:
            max_tokens: Maximum tokens per chunk (default 4000 for most models)
            chars_per_token: Approximate characters per token ratio
            preserve_file_boundaries: If True, try not to split individual file diffs
            include_context_lines: Number of context lines to include when splitting
        """
        self.max_tokens = max_tokens
        self.max_chars = int(max_tokens * chars_per_token)
        self.preserve_file_boundaries = preserve_file_boundaries
        self.include_context_lines = include_context_lines

        # Regex patterns for diff parsing
        self.file_header_pattern = re.compile(r"^(diff --git|Index:|===|---|\+\+\+)")
        self.hunk_header_pattern = re.compile(r"^@@\s+-\d+,?\d*\s+\+\d+,?\d*\s+@@")

        # C++ file extensions
        self.cpp_extensions = {".cpp", ".hpp", ".h", ".hh", ".cc", ".cxx", ".c++"}

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return get_token_total(text)

    def is_cpp_file(self, file_path: str) -> bool:
        """Check if a file path is a C++ source or header file."""
        if not file_path or file_path == "unknown":
            return False

        # Extract the file extension
        import os

        _, ext = os.path.splitext(file_path.lower())
        return ext in self.cpp_extensions

    def chunk_diff(self, diff_text: str) -> List[DiffChunk]:
        """
        Chunk a diff into manageable pieces, filtering for C++ files only.

        Args:
            diff_text: The complete diff text

        Returns:
            List of DiffChunk objects
        """
        if not diff_text.strip():
            return []

        # Split into file diffs if preserving boundaries
        if self.preserve_file_boundaries:
            file_diffs = self._split_by_files(diff_text)
            chunks = []

            # Filter for C++ files only
            cpp_file_diffs = [
                (file_path, file_diff)
                for file_path, file_diff in file_diffs
                if self.is_cpp_file(file_path)
            ]

            if not cpp_file_diffs:
                print("No C++ files found in the diff")
                return []

            print(
                f"Processing {len(cpp_file_diffs)} C++ files out of {len(file_diffs)} total files"
            )

            for file_path, file_diff in cpp_file_diffs:
                file_chunks = self._chunk_file_diff(file_diff, file_path)
                chunks.extend(file_chunks)
        else:
            # Treat entire diff as one unit (but still filter for C++ files)
            # This mode is less useful when filtering, so we'll still split by files first
            file_diffs = self._split_by_files(diff_text)
            cpp_diffs = [
                file_diff
                for file_path, file_diff in file_diffs
                if self.is_cpp_file(file_path)
            ]

            if not cpp_diffs:
                print("No C++ files found in the diff")
                return []

            combined_diff = "\n\n".join(cpp_diffs)
            chunks = self._chunk_file_diff(combined_diff, None)

        # Update chunk indices and totals
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i + 1
            chunk.total_chunks = total_chunks

        return chunks

    def _split_by_files(self, diff_text: str) -> List[Tuple[str, str]]:
        """Split diff into individual file diffs."""
        lines = diff_text.split("\n")
        file_diffs = []
        current_file = None
        current_diff = []

        for line in lines:
            # Check if this is a new file header
            if self.file_header_pattern.match(line):
                # Save previous file diff if exists
                if current_diff:
                    file_diffs.append((current_file, "\n".join(current_diff)))

                # Extract file path from header
                current_file = self._extract_file_path(line)
                current_diff = [line]
            else:
                current_diff.append(line)

        # Add last file diff
        if current_diff:
            file_diffs.append((current_file, "\n".join(current_diff)))

        return file_diffs

    def _extract_file_path(self, header_line: str) -> str:
        """Extract file path from diff header."""
        # Try to extract from git-style diff
        match = re.search(r"diff --git a/(.*?) b/", header_line)
        if match:
            return match.group(1)

        # Try to extract from unified diff
        match = re.search(r"(---|\+\+\+)\s+(.+?)(\s+|\t|$)", header_line)
        if match:
            path = match.group(2)
            # Remove timestamps and revision info
            path = re.sub(r"\s+\d{4}-\d{2}-\d{2}.*$", "", path)
            path = re.sub(r"\s+\(.*?\)$", "", path)
            return path

        return "unknown"

    def _chunk_file_diff(
        self, diff_text: str, file_path: Optional[str]
    ) -> List[DiffChunk]:
        """Chunk a single file's diff."""
        chunks = []
        lines = diff_text.split("\n")

        if self.estimate_tokens(diff_text) <= self.max_tokens:
            # Entire diff fits in one chunk
            chunk = DiffChunk(
                content=diff_text,
                file_path=file_path,
                chunk_index=1,
                total_chunks=1,
                token_count=self.estimate_tokens(diff_text),
                char_count=len(diff_text),
            )
            return [chunk]

        # Need to split the diff
        current_chunk_lines = []
        current_size = 0

        # Try to keep file headers in each chunk
        header_lines = []
        i = 0
        while i < len(lines) and self.file_header_pattern.match(lines[i]):
            header_lines.append(lines[i])
            i += 1

        header_text = "\n".join(header_lines)
        header_size = self.estimate_tokens(header_text)

        for line in lines[len(header_lines) :]:
            line_size = self.estimate_tokens(line)

            # Check if adding this line would exceed limit
            if (
                current_size + line_size + header_size > self.max_tokens
                and current_chunk_lines
            ):
                # Create chunk with header
                chunk_content = header_text + "\n" + "\n".join(current_chunk_lines)
                chunk = DiffChunk(
                    content=chunk_content.strip(),
                    file_path=file_path,
                    chunk_index=0,  # Will be updated later
                    total_chunks=0,  # Will be updated later
                    token_count=self.estimate_tokens(chunk_content),
                    char_count=len(chunk_content),
                )
                chunks.append(chunk)

                # Reset for next chunk
                current_chunk_lines = []
                current_size = 0

                # Add context lines from end of previous chunk
                if self.include_context_lines > 0 and len(chunks) > 0:
                    prev_lines = chunks[-1].content.split("\n")
                    context = prev_lines[-self.include_context_lines :]
                    current_chunk_lines.extend(context)
                    current_size += sum(self.estimate_tokens(l) for l in context)

            current_chunk_lines.append(line)
            current_size += line_size

        # Add remaining lines as final chunk
        if current_chunk_lines:
            chunk_content = header_text + "\n" + "\n".join(current_chunk_lines)
            chunk = DiffChunk(
                content=chunk_content.strip(),
                file_path=file_path,
                chunk_index=0,
                total_chunks=0,
                token_count=self.estimate_tokens(chunk_content),
                char_count=len(chunk_content),
            )
            chunks.append(chunk)

        return chunks

    def format_chunk_header(self, chunk: DiffChunk) -> str:
        """Format a header for a chunk."""
        header = f"=== Chunk {chunk.chunk_index}/{chunk.total_chunks} ==="
        if chunk.file_path:
            header += f"\nFile: {chunk.file_path}"
        header += f"\nTokens: ~{chunk.token_count} | Characters: {chunk.char_count}"
        return header

    def get_processed_files(self, diff_text: str) -> Tuple[List[str], List[str]]:
        """
        Get lists of C++ files and filtered files from the diff.

        Returns:
            Tuple of (cpp_files, filtered_files)
        """
        file_diffs = self._split_by_files(diff_text)
        cpp_files = []
        filtered_files = []

        for file_path, _ in file_diffs:
            if self.is_cpp_file(file_path):
                cpp_files.append(file_path)
            else:
                filtered_files.append(file_path)

        return cpp_files, filtered_files


def main():
    """Example usage of the DiffChunker for C++ memory leak detection."""

    with open("/Users/darkmatter/projects/ledger-works/xrpl-guides/new.diff", "r") as f:
        diff_content = f.read()

    # Initialize chunker with typical AI model limits
    chunker = DiffChunker(
        max_tokens=20000, preserve_file_boundaries=True  # GPT-3.5/4 typical context
    )

    # Show which files will be processed and which will be filtered
    cpp_files, filtered_files = chunker.get_processed_files(diff_content)

    if filtered_files:
        print(f"Filtering out {len(filtered_files)} non-C++ files:")
        for f in filtered_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(filtered_files) > 10:
            print(f"  ... and {len(filtered_files) - 10} more")
        print()

    if cpp_files:
        print(f"Processing {len(cpp_files)} C++ files:")
        for f in cpp_files[:10]:  # Show first 10
            print(f"  + {f}")
        if len(cpp_files) > 10:
            print(f"  ... and {len(cpp_files) - 10} more")
        print()

    # Process chunks
    chunks = chunker.chunk_diff(diff_content)

    if not chunks:
        print("No C++ files to process for memory leak detection.")
        return

    from athenah_ai.client import AthenahClient

    ai_source: AthenahClient = AthenahClient(
        "id",
        provider="openai",
        model_group="dist",
        custom_model="rippled-smart-core",
        version="v1",
        model_name="gpt-4.1",
        temperature=0,
        best_of=3,
    )

    # Send each chunk to AI model
    responses: list[dict] = []
    # 188
    for i in range(188, len(chunks)):
        chunk = chunks[i]
        print(f"Processing chunk {chunk.chunk_index}/{chunk.total_chunks}")
        if chunk.file_path:
            print(f"  File: {chunk.file_path}")

        # response = ai_model.process(chunk.content)
        template_response: str = """
        [{"file_name": string, "line_number": number, "reason": string}]
        """
        user_prompt: str = f"""
        {chunk.content}
        """
        system_prompt: str = f"""
        Your job is to check the C++ diffs for any potential memory leaks.
        Focus on:
        - new/delete mismatches
        - malloc/free mismatches
        - Missing delete[] for array allocations
        - Smart pointer issues
        - Resource acquisition without proper RAII

        Use the following template response:
        {template_response}

        RULES YOU MUST FOLLOW:
    
        - DO NOT INCLUDE CODE FENCES: ie: ```json or ```
        - Return a list of files and line numbers where leaks are found. If none are found return an empty array.
        """
        response = ai_source.rag_prompt_v2(system_prompt, user_prompt)
        import ast

        try:
            response = ast.literal_eval(response)
        except Exception as e:
            print(f"Error parsing response: {response} {e}")
            response = []

        if len(response) > 0:
            print(f"  Found {len(response)} potential leaks")
            print(response)
            responses.append(response)

    # Combine all responses into a single list
    all_leaks = [item for sublist in responses for item in sublist]

    print(f"\nTotal potential memory leaks found: {len(all_leaks)}")

    # save to file
    import json

    with open("leaks.json", "w") as f:
        json.dump(all_leaks, f)

    print("Results saved to leaks.json")


if __name__ == "__main__":
    main()
