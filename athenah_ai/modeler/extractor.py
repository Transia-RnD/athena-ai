"""
Extract phase (staged, query-decomposed FSM extractor).

The first closure-hardened extractor was a single monolithic agent call; it
blew the SDK stream idle-timeout. Fix is architectural, not a bigger timeout:
decompose into many small focused agent calls, each of which finishes well
under the idle threshold, and run the per-unit calls in parallel. This is
also just better engineering (one task per agent, localized failure/repair).

  Stage 1  extract_structure : component, state_vars, invariants, safety,
            and op/query SIGNATURES only.  (Fast, reliable in one call.)
  Stage 2  extract_rules     : ONE call per operation / per complex query,
            producing only that unit's transition_rules (or a trivial
            result_expr).  Parallel.
  Assemble : merge -> schema.validate() the whole -> localized per-unit repair.

Producing the model is NOT proving it faithful. That is the fidelity gate.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from athenah_ai.modeler.schema import (
    ALLOWED_TYPES,
    SCHEMA_DOC,
    _check_expr,
    validate,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("modeler.extract")

DEFAULT_MODEL = os.environ.get("MODELER_MODEL", "claude-sonnet-4-6")
MAX_TURNS = int(os.environ.get("MODELER_MAX_TURNS", "40"))
# Reuse cached raw agent outputs on the first pass (repair always forces fresh).
REUSE = os.environ.get("MODELER_REUSE_RAW", "1") == "1"
ARTIFACTS = Path(__file__).parent / "artifacts"


class UnitError(Exception):
    """A single unit failed to extract/parse; routed to localized repair."""

    def __init__(self, kind: str, name: str, msg: str):
        super().__init__(f"{kind} {name!r}: {msg}")
        self.kind, self.name, self.msg = kind, name, msg

_CLOSURE = """CLOSURE (machine-enforced): every name in every expression must
be a declared state_var, this unit's own param, a step-bound local, or an
allowed primitive: len sum all any min max abs range sorted get True False
None, plus the trie primitives `nodes` (every node reachable from the trie
root) and `ancestors(n)` (n + its parent chain to the root). Every attribute
must be a node field (span_start span_end tipSupport branchSupport children
parent tip_seq). Inventing any other helper like `root.split_at_diff(x)` is a
HARD validation failure — express the real algorithm in the step vocabulary
instead."""

STRUCTURE_PROMPT = f"""You are a formal-methods engineer. Read the target C++
component and emit ONLY its STRUCTURE as JSON — no algorithms yet.

Emit exactly:
{{
  "component": "<symbol>",
  "state_vars": [{{"name","type"(one of {sorted(ALLOWED_TYPES)}),"initial"<json>,"description"}}],
  "operations": [{{"name","params":[{{"name","type"}}],"returns","preconditions":["<closed expr>"],"description"}}],
  "queries": [{{"name","params":[...],"returns","description","complex": <true if it is an algorithm e.g. a trie walk, false if a one-line expression>}}],
  "invariants": [{{"name","predicate":"<closed python expr over state_vars>","description"}}],
  "safety_properties": [{{"name","kind":"safety|liveness","statement"}}]
}}

Model the ACTUAL state (trie of nodes, support counts, aux maps). Find the
in-code invariant checker — it is ground truth for `invariants`. Do NOT emit
transition_rules or result_expr here; signatures + invariants only.

{_CLOSURE}

Final assistant message = the JSON object only (optionally ```json fenced)."""

RULES_PROMPT = f"""You are a formal-methods engineer decomposing ONE function
into a closed primitive step list so it can be executed and model-checked.

You are given the STATE MODEL (state_vars) and the name of the single
operation/query to decompose. Read ONLY that function in the target file
(plus the minimal helpers it calls) — do not read the whole codebase.

Emit ONLY this JSON for that one unit:
  operation      -> {{"name": "<op>", "transition_rules": [ <steps> ]}}
  complex query  -> {{"name": "<q>",  "transition_rules": [ <steps> ]}}
  trivial query  -> {{"name": "<q>",  "result_expr": "<closed python expr>"}}

Step vocabulary and rules:
{SCHEMA_DOC}

{_CLOSURE}

Decompose the REAL algorithm faithfully — the radix-trie span split / compress
/ walk logic must appear as concrete steps, not be summarized away. Final
assistant message = the single JSON object only."""


def _first_json_object(s: str) -> dict | None:
    """First parseable JSON object in s (tolerates trailing data/prose)."""
    dec = json.JSONDecoder()
    i = 0
    while True:
        b = s.find("{", i)
        if b == -1:
            return None
        try:
            obj, _ = dec.raw_decode(s[b:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
        i = b + 1


def _extract_json(text: str) -> dict:
    # Prefer fenced blocks (most reliable), then fall back to whole text.
    cands: list[str] = []
    if "```" in text:
        parts = text.split("```")
        cands = [p[4:] if p.lower().startswith("json") else p
                 for p in parts[1::2]]
    for chunk in sorted(cands, key=len, reverse=True) + [text]:
        obj = _first_json_object(chunk)
        if obj is not None:
            return obj
    raise ValueError("no parseable JSON object in final message")


async def _run_agent(prompt: str, system: str, source_root: str,
                     model: str, tag: str, reuse: bool = False) -> str:
    """Run the agent, or return a cached raw_<tag>.txt when reuse=True and a
    non-empty one exists. The expensive faithful extractions are not re-run
    just because an unrelated unit or my own assembly code was buggy."""
    cache = ARTIFACTS / f"raw_{tag}.txt"
    if reuse and cache.exists() and cache.read_text().strip():
        logger.info("[%s] using cached raw output", tag)
        return cache.read_text()
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    options = ClaudeAgentOptions(
        model=model,
        system_prompt=system,
        allowed_tools=["Read", "Glob", "Grep"],
        max_turns=MAX_TURNS,
        cwd=source_root,
        permission_mode="bypassPermissions",
        env={"IS_SANDBOX": "1"},
    )
    last, saw_result = "", False
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            buf = [b.text for b in message.content
                   if isinstance(b, TextBlock)]
            if buf:
                last = "\n".join(buf)
        elif isinstance(message, ResultMessage):
            saw_result = True
            logger.info("[%s] done: subtype=%s is_error=%s num_turns=%s", tag,
                        getattr(message, "subtype", None),
                        getattr(message, "is_error", None),
                        getattr(message, "num_turns", None))
            break
    if not saw_result:
        logger.warning("[%s] stream ended WITHOUT ResultMessage", tag)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / f"raw_{tag}.txt").write_text(last)
    return last


async def extract_structure(source_root: str, target: str,
                            model: str) -> dict:
    msg = (f"Target component file: {target}\nRepository root: {source_root}\n"
           f"Read it and emit the STRUCTURE JSON.")
    fsm = _extract_json(await _run_agent(msg, STRUCTURE_PROMPT, source_root,
                                         model, "structure", reuse=REUSE))
    # Light structural gate (full validate() runs post-assembly).
    errs: list[str] = []
    for sv in fsm.get("state_vars", []):
        if sv.get("type") not in ALLOWED_TYPES:
            errs.append(f"state_var {sv.get('name')!r}: bad type")
    sn = {s["name"] for s in fsm.get("state_vars", [])}
    for inv in fsm.get("invariants", []):
        _check_expr(inv.get("predicate", ""), sn,
                    f"invariant {inv.get('name')!r}", errs)
    if errs:
        raise ValueError("structure stage invalid:\n" +
                         "\n".join(f"  - {e}" for e in errs))
    logger.info("structure: %d state_vars, %d ops, %d queries, %d invariants",
                len(fsm["state_vars"]), len(fsm["operations"]),
                len(fsm["queries"]), len(fsm["invariants"]))
    return fsm


async def extract_unit(kind: str, name: str, state_vars: list, source_root: str,
                       target: str, model: str, prior_errs: str = "") -> dict:
    sv = json.dumps(state_vars, indent=1)
    msg = (f"Target file: {target}\nRepository root: {source_root}\n\n"
           f"STATE MODEL (state_vars):\n{sv}\n\n"
           f"Decompose this {kind}: {name!r}\n"
           f"Read only its function body (+minimal helpers) and emit its "
           f"single-unit JSON.")
    if prior_errs:
        msg += (f"\n\nYour previous attempt failed validation:\n{prior_errs}\n"
                f"Fix every error. Output ONLY the single JSON object — no "
                f"prose, no ```cpp. closure + step vocabulary are enforced.")
    tag = f"{kind}_{name}"
    # First pass may reuse cache; repair (prior_errs) always forces a fresh run.
    reuse = REUSE and not prior_errs
    text = await _run_agent(msg, RULES_PROMPT, source_root, model, tag,
                            reuse=reuse)
    try:
        return _extract_json(text)
    except ValueError as e:
        if reuse:  # bad cache — retry once with a fresh agent call
            text = await _run_agent(msg, RULES_PROMPT, source_root, model,
                                    tag, reuse=False)
            try:
                return _extract_json(text)
            except ValueError as e2:
                raise UnitError(kind, name, str(e2)) from e2
        raise UnitError(kind, name, str(e)) from e


async def extract_fsm(source_root: str, target: str,
                      model: str = DEFAULT_MODEL) -> dict:
    struct = await extract_structure(source_root, target, model)

    units: list[tuple[str, str]] = [("operation", o["name"])
                                    for o in struct["operations"]]
    units += [("query", q["name"]) for q in struct["queries"]]

    kind_of = {n: k for k, n in units}  # name -> kind

    def _attach(r: dict) -> None:
        tgt = next((o for o in struct["operations"]
                    if o["name"] == r["name"]), None) \
              or next((q for q in struct["queries"]
                       if q["name"] == r["name"]), None)
        if tgt is None:
            return
        tgt.pop("result_expr", None)
        tgt.pop("transition_rules", None)
        tgt.pop("complex", None)
        if "transition_rules" in r:
            tgt["transition_rules"] = r["transition_rules"]
        else:
            tgt["result_expr"] = r.get("result_expr", "")

    # Fault-tolerant: one bad unit must not abort the others.
    results = await asyncio.gather(*[
        extract_unit(k, n, struct["state_vars"], source_root, target, model)
        for k, n in units
    ], return_exceptions=True)

    pending: dict[str, str] = {}  # name -> prior-error text to repair against
    for res in results:
        if isinstance(res, UnitError):
            pending[res.name] = res.msg
        elif isinstance(res, BaseException):
            raise res  # genuine bug, not a unit-level failure
        else:
            _attach(res)

    for rnd in range(3):
        errs = validate(struct)
        for k, n in units:
            mine = [e for e in errs if f"{k} {n!r}" in e]
            if mine:
                pending[n] = "\n".join(f"  - {e}" for e in mine)
        if not pending:
            return struct
        logger.warning("repair round %d: %d unit(s) %s", rnd + 1,
                        len(pending), sorted(pending))
        fixed = await asyncio.gather(*[
            extract_unit(kind_of[n], n, struct["state_vars"], source_root,
                         target, model, prior_errs=pe)
            for n, pe in pending.items()
        ], return_exceptions=True)
        pending = {}
        for res in fixed:
            if isinstance(res, UnitError):
                pending[res.name] = res.msg
            elif isinstance(res, BaseException):
                raise res
            else:
                _attach(res)

    errs = validate(struct)
    if errs or pending:
        raise ValueError(
            "FSM still invalid after repair rounds:\n"
            + "\n".join(f"  - {e}" for e in errs)
            + ("\n  unrecovered units: " + ", ".join(sorted(pending))
               if pending else ""))
    return struct


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root",
                    default="/Users/infinityworks/projects/xrplf/xrpld")
    ap.add_argument("--target", default="src/xrpld/consensus/LedgerTrie.h")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out",
                    default=str(ARTIFACTS / "ledger_trie.fsm.json"))
    args = ap.parse_args()

    fsm = asyncio.run(extract_fsm(args.source_root, args.target, args.model))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fsm, indent=2))
    logger.info("valid FSM written: %s", out)
    logger.info("state_vars=%d operations=%d queries=%d invariants=%d safety=%d",
                len(fsm["state_vars"]), len(fsm["operations"]),
                len(fsm["queries"]), len(fsm["invariants"]),
                len(fsm["safety_properties"]))


if __name__ == "__main__":
    main()
