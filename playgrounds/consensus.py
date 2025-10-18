#!/usr/bin/env python
# coding: utf-8

AGENT_MODEL = "gpt-4.1"
ATHENAH_CLIENT_NAME: str = "rippled-ai-consensus"
root_path: str = "/Users/darkmatter/projects/ledger-works/rippled"


def index():
    # from athenah_ai.indexer import AthenahIndexer
    # indexer = AthenahIndexer("local", "id", "dist", "rippled-ai-consensus", "v1")
    # indexer.build_from_dirs(path, ["src/xrpld/app/consensus", "src/xrpld/consensus", "src/xrpld/ledger", "src/xrpld/app/ledger"], False, True)
    pass


def theory():
    from athenah_ai.client import AthenahClient
    from athenah_ai.utils.fs import get_files_in_dir
    from typing import List, Any

    dirs: List[str] = [
        "src/xrpld/app/consensus",
        "src/xrpld/consensus",
    ]
    files: List[Any] = []
    for dir in dirs:
        files.extend(get_files_in_dir(root_path, dir, None))

    # ai_source: AthenahClient = AthenahClient(
    #     "id", model_name=AGENT_MODEL, best_of=1, temperature=1
    # )
    ai_source: AthenahClient = AthenahClient(
        "id", "dist", ATHENAH_CLIENT_NAME, "v1", AGENT_MODEL, best_of=3, temperature=1
    )

    system_prompt: str = f"""
    Context: {files}
"""

    user_input: str = """
We need to analyze the consensus algorithm in the XRPL codebase and theorize how it can be improved to allow for multithreading and parallel transaction processing.

Create a step by step plan to make the conensus algorithm multithreaded and allow for parallel transaction processing.
"""
    response = ai_source.rag_prompt_v2("", user_input)
    with open("consensus_analysis.txt", "w") as f:
        f.write(response)


def main():
    root_path: str = "/Users/darkmatter/projects/ledger-works/rippled"
    from athenah_ai.client import AthenahClient
    from athenah_ai.utils.fs import get_files_in_dir
    from typing import List, Any

    # dirs: List[str] = [
    #     # "src/xrpld/app/consensus",
    #     # "src/xrpld/consensus",
    #     "src/xrpld/ledger",
    #     "src/xrpld/app/ledger",
    # ]
    # files: List[Any] = []
    # for dir in dirs:
    #     files.extend(get_files_in_dir(root_path, dir, None))

    # ai_source: AthenahClient = AthenahClient(
    #     "id", model_name=AGENT_MODEL, best_of=3, temperature=0
    # )
    ai_source: AthenahClient = AthenahClient(
        "id",
        # provider="anthropic",
        provider="openai",
        # provider="xai",
        model_group="dist",
        custom_model=ATHENAH_CLIENT_NAME,
        version="v1",
        # model_name="claude-4-sonnet-20250514",
        model_name="gpt-4.1",
        # model_name="grok-4",
        temperature=1,
        best_of=3,
    )

    system_prompt: str = f"""
    """

    user_input: str = """
We need to make consensus a parallel process. We want to be able to process transactions in parallel and reach consensus on them. We want to be able to process 1000's or 100k transactions in a single ledger.

### 1. `src/xrpld/consensus/Consensus.h`

**Changes:**
- Add thread pool management for parallel transaction processing
- Add atomic variables for thread-safe state management
- Add mutex protection for critical consensus state
- Add work queue system for distributing transaction validation
- Modify `ConsensusResult` to include thread-safe transaction processing results
- Add parallel processing configuration parameters
- Add thread-safe dispute resolution mechanisms

### 2. `src/xrpld/consensus/Consensus.cpp`

**Changes:**
- Implement parallel transaction validation in `gotTxSet()`
- Add thread pool initialization and management
- Modify `createDisputes()` to handle concurrent dispute creation
- Update `updateOurPositions()` to use parallel processing for position updates
- Add synchronization barriers for consensus phases
- Implement lock-free data structures where possible for performance

### 3. `src/xrpld/app/consensus/RCLConsensus.h`

**Changes:**
- Add thread pool member variables to the Adaptor class
- Add configuration for number of worker threads
- Add thread-safe caching mechanisms for transaction sets
- Modify validation processing to be parallelizable
- Add atomic counters for tracking parallel operations

### 4. `src/xrpld/app/consensus/RCLConsensus.cpp`

**Changes:**
- Implement parallel transaction application in `buildLCL()`
- Add thread-safe transaction sharing mechanisms
- Modify `onClose()` to distribute transaction processing across threads
- Update `doAccept()` to coordinate parallel ledger building
- Add parallel validation of disputed transactions
- Implement work-stealing queue for load balancing

### 5. `src/xrpld/app/consensus/RCLCxTx.h`

**Changes:**
- Add thread-safe transaction set operations
- Implement concurrent insert/erase operations for `MutableTxSet`
- Add atomic reference counting for transaction items
- Add parallel comparison methods for transaction sets

### 6. `src/xrpld/consensus/DisputedTx.h`

**Changes:**
- Add mutex protection for vote tracking
- Implement atomic vote counting operations
- Add thread-safe dispute state management
- Modify `updateVote()` to be thread-safe with lock-free operations where possible

### 7. `src/xrpld/consensus/ConsensusParms.h`

**Changes:**
- Add parameters for thread pool configuration
- Add timing parameters for parallel processing coordination
- Add configuration for maximum concurrent transaction processing
- Add parameters for work queue sizes and thread priorities

### 8. `src/xrpld/consensus/ConsensusTypes.h`

**Changes:**
- Add thread-safe timer implementation
- Modify `ConsensusResult` to include parallel processing metrics
- Add atomic state variables for consensus phases
- Add thread-safe close time tracking

### 9. `src/xrpld/app/consensus/RCLValidations.h`

**Changes:**
- Add thread-safe validation storage and retrieval
- Implement concurrent validation processing
- Add parallel validation verification
- Modify validation trust updates to be thread-safe

### 10. `src/xrpld/app/consensus/RCLValidations.cpp`

**Changes:**
- Implement parallel validation handling in `handleNewValidation()`
- Add thread-safe validation caching
- Modify validation expiration to work with concurrent access
- Add parallel ledger acquisition and validation

List the steps and the files we need to change. Then finally write the changes and return the code. The code must be valid. Use the consensus files.

/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/src/xrpld/consensus


"""
    response = ai_source.agent_prompt(
        "Consensus Developer", "Consensus Coder", system_prompt + user_input
    )
    with open("consensus_analysis.txt", "w") as f:
        f.write(response)


# index()
# theory()
main()
