"""
FSM schema + validator (operational closure).

An earlier iteration surfaced the failure mode the hard way: an LLM will pass
a structural schema by emitting effect expressions full of *undefined helper
methods* (`root.split_at_diff(ledger)`). Structurally valid, semantically
prose. A model built from that tests the model-writer, not the extraction.

This version closes that hole. Two hard gates:

  1. CLOSURE — every name used in any expression must resolve to a declared
     state_var, an operation/query param, a comprehension-bound local, or a
     fixed allowed-primitive set. No undefined helpers, ever. Attribute access
     is restricted to a fixed NODE_FIELDS set.

  2. OPERATIONAL — each operation must carry `transition_rules`: an ordered
     list of steps drawn ONLY from a fixed primitive vocabulary (STEP_OPS).
     The algorithm must be expressed in those primitives, not prose. This is
     what makes the FSM executable without inventing logic downstream, which
     is what makes the fidelity number mean something.
"""

from __future__ import annotations

import ast
from typing import Any

ALLOWED_TYPES = {
    "int", "uint", "bool", "set", "map", "list", "tree", "ledger", "id",
    "seq", "optional",
}

# The only callables/builtins an expression may reference. Beyond Python
# builtins this includes a SMALL fixed set of trie-traversal primitives with
# one documented meaning each (implemented once by the executable model):
#   nodes         -> every node reachable from the trie root
#   ancestors(n)  -> n and its parent chain up to (and including) the root
ALLOWED_PRIMS = {
    "len", "sum", "all", "any", "min", "max", "abs", "range", "sorted",
    "get", "True", "False", "None", "nodes", "ancestors",
}

# The only attributes addressable on a node/tree value.
NODE_FIELDS = {
    "span_start", "span_end", "tipSupport", "branchSupport", "children",
    "parent", "tip_seq", "nodes",
}

# The fixed transition-step vocabulary. Each step is a dict {"op": <one of>,
# ...typed args}. This is a tiny radix-trie mutation DSL — closed and finite,
# so every step has exactly one meaning the model interpreter implements once.
STEP_OPS: dict[str, set[str]] = {
    # locate a node; bind it to a local name. mode in exact|longest_prefix|root
    "find": {"of", "mode", "bind"},
    # create a node; bind to a local
    "new_node": {"span_start", "span_end", "tipSupport", "bind"},
    # split node's span at seq `at`; lower part stays, upper part -> bind_new
    "split": {"node", "at", "bind_new"},
    "attach": {"parent", "child"},
    "detach": {"parent", "child"},
    # tipSupport += delta on `node`
    "add_tip": {"node", "delta"},
    # add delta to branchSupport of `node` and every ancestor up to root
    "add_branch_path": {"node", "delta"},
    # if `node` is non-root, tipSupport==0, exactly one child -> merge
    "compress": {"node"},
    # map[key] += delta; drop key when it reaches 0
    "map_add": {"map", "key", "delta"},
    # bind a closed intermediate value to a local
    "let": {"bind", "expr"},
    # trie walk: cursor `bind` starts at `start`; while `while` holds, reassign
    # cursor := `choose`; on exit `bind` is the final node. `while`/`choose`
    # are closed exprs that may reference the cursor (the bind name itself).
    "walk": {"start", "while", "choose", "bind"},
    # early return `expr` when `cond` holds
    "guard_return": {"cond", "expr"},
    # final return
    "ret": {"expr"},
}

REQUIRED_TOP = ("component", "state_vars", "operations", "queries",
                "invariants", "safety_properties")


def _expr_names(s: str) -> tuple[set[str], set[str], bool]:
    """(free_names, attr_names, parsed_ok) for a Python expression string.

    free_names excludes comprehension-bound targets (those are legal locals).
    """
    try:
        tree = ast.parse(s, mode="eval")
    except SyntaxError:
        return set(), set(), False
    bound: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.GeneratorExp,
                          ast.DictComp)):
            for g in n.generators:
                for t in ast.walk(g.target):
                    if isinstance(t, ast.Name):
                        bound.add(t.id)
        elif isinstance(n, ast.Lambda):
            for a in n.args.args:
                bound.add(a.arg)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    return names - bound, attrs, True


def _check_expr(s: str, scope: set[str], where: str,
                errs: list[str]) -> None:
    names, attrs, ok = _expr_names(s)
    if not ok:
        errs.append(f"{where}: not a Python expression (prose): {s!r}")
        return
    unknown = names - scope - ALLOWED_PRIMS
    if unknown:
        errs.append(f"{where}: undefined name(s) {sorted(unknown)} "
                    f"(closure violation — invented helper?)")
    bad_attr = attrs - NODE_FIELDS
    if bad_attr:
        errs.append(f"{where}: attribute(s) {sorted(bad_attr)} not in "
                    f"NODE_FIELDS — opaque helper method, not a state field")


def _validate_rules(rules: list, scope: set[str], state_names: set[str],
                    where: str, errs: list[str]) -> None:
    """Validate an ordered transition_rules list (ops AND complex queries).

    Tracks step-bound locals. Closure is enforced on every expr arg. `walk`
    binds its cursor before its own while/choose are checked (the cursor is
    the bind name and is referenceable in those expressions).
    """
    locals_: set[str] = set()
    for i, st in enumerate(rules):
        tag = f"{where} step[{i}]"
        sop = st.get("op")
        if sop not in STEP_OPS:
            errs.append(f"{tag}: op {sop!r} not in STEP_OPS vocabulary")
            continue
        extra = set(st) - {"op"} - STEP_OPS[sop]
        if extra:
            errs.append(f"{tag} ({sop}): unexpected args {sorted(extra)}")
        # Bind names first so same-step exprs (walk cursor) resolve. A bind
        # MUST be a single identifier string — the LLM sometimes emits a list
        # (wanting multi-bind the vocabulary does not have); that is a
        # validation error, never a crash.
        for bk in ("bind", "bind_new"):
            if bk in st:
                bv = st[bk]
                if isinstance(bv, str) and bv.isidentifier():
                    locals_.add(bv)
                else:
                    errs.append(f"{tag}: {bk}={bv!r} must be a single "
                                f"identifier (no multi-bind in the vocabulary)")
        for k, v in st.items():
            if k in ("op", "bind", "bind_new"):
                continue
            if k == "map":
                if not (isinstance(v, str) and v in state_names):
                    errs.append(f"{tag}: map {v!r} is not a state_var")
                continue
            if k == "mode":
                if v not in ("exact", "longest_prefix", "root"):
                    errs.append(f"{tag}: mode {v!r} invalid")
                continue
            if k in ("node", "parent", "child", "start") \
                    and isinstance(v, str) and v.isidentifier():
                if v not in locals_ and v not in state_names:
                    errs.append(f"{tag}: {k}={v!r} is neither a bound local "
                                f"nor a state_var")
                continue
            _check_expr(str(v), scope | locals_, f"{tag} arg {k!r}", errs)


def validate(fsm: dict[str, Any]) -> list[str]:
    """Return human-readable errors; empty == valid, closed, executable FSM."""
    errs: list[str] = []
    for k in REQUIRED_TOP:
        if k not in fsm:
            errs.append(f"missing top-level section: {k}")
    if errs:
        return errs

    state_names: set[str] = set()
    for sv in fsm["state_vars"]:
        name, typ = sv.get("name"), sv.get("type")
        if not name:
            errs.append("state_var with no name")
            continue
        state_names.add(name)
        if typ not in ALLOWED_TYPES:
            errs.append(f"state_var {name!r}: bad type {typ!r}")
        if "initial" not in sv:
            errs.append(f"state_var {name!r}: missing 'initial'")

    op_names = {o.get("name") for o in fsm["operations"]}
    q_names = {q.get("name") for q in fsm["queries"]}
    callable_scope = state_names | op_names | q_names

    if not fsm["operations"]:
        errs.append("operations is empty — no state machine")
    for op in fsm["operations"]:
        oname = op.get("name", "<unnamed>")
        params = {p.get("name") for p in op.get("params", [])}
        scope = state_names | params | callable_scope

        for pc in op.get("preconditions", []):
            _check_expr(pc, scope, f"op {oname!r} precondition", errs)

        rules = op.get("transition_rules")
        if not rules:
            errs.append(f"op {oname!r}: no transition_rules — algorithm is "
                        f"prose, not executable")
            continue
        _validate_rules(rules, scope, state_names, f"op {oname!r}", errs)

    for q in fsm["queries"]:
        qn = q.get("name", "<unnamed>")
        params = {p.get("name") for p in q.get("params", [])}
        scope = state_names | params | callable_scope
        rexpr = q.get("result_expr")
        qrules = q.get("transition_rules")
        if qrules:
            # Complex query (e.g. getPreferred trie-walk): decomposed, not prose.
            _validate_rules(qrules, scope, state_names, f"query {qn!r}", errs)
        elif rexpr is not None:
            _check_expr(rexpr, scope, f"query {qn!r} result_expr", errs)
        else:
            errs.append(f"query {qn!r}: needs result_expr OR transition_rules")

    if not fsm["invariants"]:
        errs.append("invariants is empty — nothing to check")
    for inv in fsm["invariants"]:
        iname = inv.get("name", "<unnamed>")
        pred = inv.get("predicate", "")
        names, _, ok = _expr_names(pred)
        if not ok:
            errs.append(f"invariant {iname!r}: predicate is prose: {pred!r}")
            continue
        if not (names & state_names):
            errs.append(f"invariant {iname!r}: references no state_var — "
                        f"not about state")
        _check_expr(pred, state_names | callable_scope,
                    f"invariant {iname!r}", errs)

    for sp in fsm["safety_properties"]:
        spn = sp.get("name", "<unnamed>")
        if sp.get("kind") not in ("safety", "liveness"):
            errs.append(f"safety_property {spn!r}: kind must be safety|liveness")
        if len((sp.get("statement") or "").split()) < 4:
            errs.append(f"safety_property {spn!r}: statement too thin")

    return errs


_STEP_DOC = "\n".join(
    f'    {{"op": "{k}", {", ".join(sorted(f0+":<...>" for f0 in v))}}}'
    for k, v in STEP_OPS.items()
)

SCHEMA_DOC = f"""{{
  "component": "<symbol, e.g. xrpl::LedgerTrie>",
  "state_vars": [
    {{"name": "<id>", "type": "<int uint bool set map list tree ledger id seq optional>",
     "initial": <json>, "description": "<state held>"}}
  ],
  "operations": [
    {{"name": "<id>", "params": [{{"name": "<id>", "type": "<type>"}}],
     "returns": "<type|null>",
     "preconditions": ["<closed python expr>"],
     "transition_rules": [ <ordered steps, ONLY from the vocabulary below> ],
     "description": "<one line>"}}
  ],
  "queries": [
    {{"name": "<id>", "params": [...], "returns": "<type>",
     // trivial query: a closed expr. complex query (e.g. a trie walk like
     // getPreferred): OMIT result_expr and give "transition_rules" instead,
     // using the SAME step vocabulary (walk/let/find/...), ending in `ret`.
     "result_expr": "<closed python expr>  (XOR transition_rules)",
     "description": "<one line>"}}
  ],
  "invariants": [
    {{"name": "<id>", "predicate": "<closed python expr over state_vars>",
     "description": "<meaning>"}}
  ],
  "safety_properties": [
    {{"name": "<id>", "kind": "<safety|liveness>", "statement": "<precise words>"}}
  ]
}}

TRANSITION-STEP VOCABULARY (the ONLY ops allowed in transition_rules; express
the real algorithm in these — no invented method names anywhere):
{_STEP_DOC}

  find.mode ∈ exact | longest_prefix | root ; find.of = a closed expr (e.g. a
    param ledger). new_node/find/split bind a local name reusable later.
  Node fields you may read: {sorted(NODE_FIELDS)}.
  Allowed call primitives only: {sorted(ALLOWED_PRIMS)}.

CLOSURE RULE (machine-enforced): every name in every expression must be a
declared state_var, this op/query's param, a step-bound local, or an allowed
primitive. Every attribute must be a node field above. An undefined helper =
hard validation failure."""
