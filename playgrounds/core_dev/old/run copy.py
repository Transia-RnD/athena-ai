# What is the thing I'm trying to teach?

# You will have access to whatever repo you are trying to teach.
# Tools:
# - Find Function, Class or Variable in Folders/Files
# - Read File Content
# - Step through Code: You will need to step through the code to understand how it works. Stepping through the code means executing it line by line, understanding the flow, and identifying how different parts interact with each other. We need to create a list or json to map out how the flow of the code works.

from athenah_ai.client import AthenahClient
from playgrounds.core_dev.utils import build_agent_tools, collect_ai_v1_descriptions

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from athenah_ai.utils.fs import read_file, write_file

# REMOVE
from playgrounds.core_dev.tools import map_and_classify_symbols


def run_agent():
    user_input: str = ""

    athenah = AthenahClient("id", "dist")
    athenah.init_llm()

    def callback(graph, data):
        ai_response: str = data.content
        print(f"AI Response: {ai_response}")

    # jarvis_response = brain.response_classifier.invoke(user_input)

    tools = build_agent_tools(["get_user_pull_requests"])
    graph = create_react_agent(athenah.llm, tools, checkpointer=MemorySaver())

    config = {"configurable": {"thread_id": "thread-1", "user_id": "1"}}

    # messages = [
    #     {"role": "system", "content": case_prompt(jarvis_response)},
    #     {"role": "user", "content": user_input},
    # ]
    # inputs = {"messages": from_messages_to_tuple(messages)}
    # print("START STREAM")
    # while True:
    #     case_do_stream(graph, inputs, config, callback)
    #     break
    # print("END STREAM")


def test():
    # athenah = AthenahClient("id", "dist")
    # athenah.init_llm()
    # response = map_and_classify_symbols(
    #     "Transactor",
    #     "/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source",
    #     athenah.llm,
    # )
    # print(response)

    # client = AthenahClient("id", "dist", "rippled-ai-core", "v1", "gpt-4.1")
    # response = client.agent_prompt(
    #     "Code Stepper",
    #     "Step through Code: You will need to step through the code to understand how it works. Stepping through the code means executing it line by line, understanding the flow, and identifying how different parts interact with each other. We need to create a list or json to map out how the flow of the code works.",
    #     "When a transaction is submitted to the XRPL, it is processed by the Transactor class? What is the full process?",
    # )
    # print(response)
    response = """
When a transaction is submitted to the XRPL, it is processed by the Transactor class through a structured, multi-step process:

1. The transaction is submitted by a client and undergoes preliminary checks (syntax, signature, fee, etc.).
2. The Transactor class (or a subclass for the specific transaction type) is instantiated with the transaction context.
3. The main processing flow is:
   - Preflight: Static checks (syntax, signature, fee) using methods like checkSeqProxy and checkSign.
   - Preclaim: Ledger-dependent checks (account existence, sequence number) via the preclaim method.
   - Apply: 
     - Deducts the transaction fee (payFee).
     - Increments the sequence number (consumeSeqProxy).
     - Executes the transaction-specific logic in doApply (implemented by the subclass, e.g., PaymentTransactor for payments).
     - Updates the ledger state.
4. The process is orchestrated by the operator() method, which calls these steps in order.
5. The result is either successful application of the transaction or a specific error code if any check fails.

In summary, the Transactor class provides a consistent, extensible framework for transaction validation and application, ensuring all necessary checks and state changes are performed securely and in the correct order. Each transaction type customizes the core logic by implementing its own doApply method.    
"""

    final = collect_ai_v1_descriptions(
        "/Users/darkmatter/projects/transia/athena-ai/dist/rippled-ai-core/rippled-ai-core-source/src/xrpld/app/tx/detail"
    )
    relevent_info = ""
    for entry in final:
        relevent_info += (
            f"\nFile: {entry['file']}\nDescription: {entry['description']}\n"
        )

    client = AthenahClient("id", "dist", "rippled-ai-core", "v1", "gpt-4.1")
    # step_responsev2 = client.agent_prompt(
    #     "Code Stepper",
    #     "Step through Code: You will need to step through the code to understand how it works. Stepping through the code means executing it line by line, understanding the flow, and identifying how different parts interact with each other. We need to create a list or json to map out how the flow of the code works.",
    #     "Create a json map of the process. Use exact function names in the exact order. For each function step into the function and describe it in an agnostic way: "
    #     + response.strip()
    #     + relevent_info,
    # )
    # print(step_responsev2)
    step_responsev2 = """
{
  "XRPL_Transaction_Processing_Flow": [
    {
      "function": "Transactor::operator()",
      "description": "Main entry point for processing a transaction. Orchestrates the entire transaction lifecycle, calling each major step in order."
    },
    {
      "function": "Transactor::preflight",
      "description": "Performs static, context-free checks on the transaction. Validates syntax, required fields, flags, signature, and fee structure. May call helper methods such as checkSeqProxy, checkSign, and checkFee."
    },
    {
      "function": "Transactor::preclaim",
      "description": "Performs ledger-dependent checks that require access to the current ledger state. Validates account existence, sequence number, and other preconditions that depend on the ledger."
    },
    {
      "function": "Transactor::apply",
      "description": "Executes the main transaction logic, including fee deduction, sequence number consumption, and transaction-specific application. This step is only reached if preflight and preclaim succeed."
    },
    {
      "function": "Transactor::payFee",
      "description": "Deducts the transaction fee from the source account. Ensures the account has sufficient balance and updates the ledger accordingly."
    },
    {
      "function": "Transactor::consumeSeqProxy",
      "description": "Increments the account's sequence number or consumes a ticket, depending on the transaction type. Ensures correct ordering and uniqueness of transactions."
    },
    {
      "function": "Transactor::doApply",
      "description": "Executes the transaction-specific logic. This is a virtual method implemented by each subclass (e.g., PaymentTransactor, SetTrust, etc.) to perform the actual state changes required by the transaction."
    },
    {
      "function": "ApplyContext::checkInvariants",
      "description": "After the transaction is applied, runs a set of invariant checks (from InvariantCheck classes) to ensure the ledger's integrity has not been violated (e.g., no XRP created, no negative balances, etc.)."
    },
    {
      "function": "ApplyContext::apply",
      "description": "Commits the transaction's changes to the ledger if all previous steps succeed and invariants are not violated. If any step fails, rolls back changes and returns an error code."
    }
  ],
  "Notes": [
    "Each transaction type (e.g., Payment, SetTrust, NFTokenMint) is implemented as a subclass of Transactor and overrides doApply to provide custom logic.",
    "If any step fails, the process is aborted and an appropriate error code is returned.",
    "Invariant checks are performed after the transaction logic but before final ledger commit.",
    "Batch transactions and special transaction types may have additional orchestration, but follow the same general pattern."
  ]
}
"""

    functionality = "Transactors"
    template: str = read_file(
        "/Users/darkmatter/projects/transia/athena-ai/playgrounds/core_dev/template.md"
    )
    prompt: str = f"""
Our goal is to create documentation for the XRPL source code, specifically focusing on the {functionality} functionaltiy. We will use this template to break down the functionality into its components and describe how they work together.

Template: 
{template}

Agent Response:
{step_responsev2}

Relevant Information:
{relevent_info}
"""
    teach_response = client.agent_prompt(
        "Source Code Teacher",
        "Teach the functionality of the XRPL source code in a structured way, using the provided template. The goal is to break down the functionality into its components and describe how they work together.",
        prompt,
    )
    print(teach_response)
    write_file(
        f"/Users/darkmatter/projects/transia/athena-ai/playgrounds/core_dev/results/{functionality}",
        teach_response,
    )


test()
