"""
Model phase — executable model = deterministic interpreter of the FSM.

The model is NOT bespoke code an agent wrote by reading LedgerTrie.h (that
would make the fidelity gate measure the code-writer, not the extraction). It
is a fixed interpreter of the STEP_OPS vocabulary: every primitive has ONE
implementation here, defined to the vocabulary contract in schema.py. The
ONLY LLM-derived input is the FSM's transition_rules. So the fidelity gate
measures exactly one thing — is the LLM's decomposition, executed under the
agreed primitive semantics, faithful to the real C++?

Ledger semantics are byte-identical to harness/mock_ledger.hpp (a ledger IS
its history string) so the C++ ground truth and this model are apples-to-apples.

CLI: `python model_runner.py <fsm.json> <ops>` emits the SAME JSON trace shape
as harness/trace_dumper, so fidelity.py can diff them step-for-step.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ledger model — identical to harness/mock_ledger.hpp
# ---------------------------------------------------------------------------
_REGISTRY: dict[str, int] = {}
_NEXT = [1]  # id 0 reserved = unknown; "" (genesis) registers first -> 1


def _id_of(history: str) -> int:
    if history not in _REGISTRY:
        _REGISTRY[history] = _NEXT[0]
        _NEXT[0] += 1
    return _REGISTRY[history]


class Ledger:
    def __init__(self, history: str = ""):
        self.history = history

    @property
    def tip_seq(self) -> int:          # the ledger's own sequence number
        return len(self.history)

    @property
    def span_start(self) -> int:
        return 0

    @property
    def span_end(self) -> int:
        return len(self.history) + 1

    def seq(self) -> int:
        return len(self.history)

    def id(self) -> int:
        return _id_of(self.history)

    def ancestor_id(self, s: int) -> int:
        return 0 if s > len(self.history) else _id_of(self.history[:s])


# ---------------------------------------------------------------------------
# Trie node
# ---------------------------------------------------------------------------
class Node:
    __slots__ = ("ledger", "span_start", "span_end", "tipSupport",
                 "branchSupport", "children", "parent")

    def __init__(self, ledger: Ledger, span_start: int, span_end: int,
                 tipSupport: int = 0):
        self.ledger = ledger
        self.span_start = span_start
        self.span_end = span_end
        self.tipSupport = tipSupport
        self.branchSupport = tipSupport
        self.children: list[Node] = []
        self.parent: Node | None = None

    @property
    def tip_seq(self) -> int:
        return self.span_end - 1


def _all_nodes(root: Node) -> list[Node]:
    out, stack = [], [root]
    while stack:
        n = stack.pop()
        out.append(n)
        stack.extend(n.children)
    return out


def _ancestors(n: Node) -> list[Node]:
    out = []
    while n is not None:
        out.append(n)
        n = n.parent
    return out


def _shared(a: str, b: str) -> int:
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    return i


# ---------------------------------------------------------------------------
# Closed-expression evaluator (names were closure-validated upstream)
# ---------------------------------------------------------------------------
class _CallList(list):
    """`nodes` is documented as a collection but the FSM also writes it as
    `nodes()`. Support both spellings so the interpreter contract — not an
    accidental call-vs-value mismatch — is what the fidelity gate measures."""

    def __call__(self):
        return self


def _make_ns(state: dict, extra: dict) -> dict:
    root = state["root"]
    ns = {
        "len": len, "sum": sum, "all": all, "any": any, "min": min,
        "max": max, "abs": abs, "range": range, "sorted": sorted,
        "True": True, "False": False, "None": None,
        "get": lambda d, k, default=0: d.get(k, default),
        "nodes": _CallList(_all_nodes(root)),
        "ancestors": _ancestors,
    }
    ns.update(state)
    ns.update(extra)
    return ns


def _ev(expr, state: dict, extra: dict):
    if not isinstance(expr, str):
        return expr
    # Namespace MUST be globals (single dict): comprehension/generator scopes
    # cannot see eval()'s locals, only its globals. Passing it as locals was a
    # bug that silently broke every comprehension over state.
    g = _make_ns(state, extra)
    g["__builtins__"] = {}
    return eval(expr, g)  # noqa: S307


# ---------------------------------------------------------------------------
# STEP_OPS primitives — ONE fixed implementation each (the contract)
# ---------------------------------------------------------------------------
class _Return(Exception):
    def __init__(self, value):
        self.value = value


def _find(state, of_ledger: Ledger, mode: str) -> Node:
    root = state["root"]
    if mode == "root":
        return root
    cur = root
    while True:
        nxt = None
        for c in cur.children:
            if _shared(c.ledger.history, of_ledger.history) >= c.span_end - 1 \
                    and c.span_end - 1 <= of_ledger.tip_seq:
                nxt = c
                break
        if nxt is None:
            break
        cur = nxt
    if mode == "longest_prefix":
        return cur
    if mode == "exact":
        if cur.ledger.history[:cur.tip_seq] == of_ledger.history[:cur.tip_seq] \
                and cur.tip_seq == of_ledger.tip_seq:
            return cur
        return None
    raise ValueError(f"bad find mode {mode!r}")


def _split(node: Node, at: int) -> Node:
    """node keeps [span_start, at); a new upper node takes [at, span_end)
    with node's tip + children; upper is attached as node's only child."""
    upper = Node(node.ledger, at, node.span_end, node.tipSupport)
    upper.branchSupport = node.branchSupport
    upper.children = node.children
    for ch in upper.children:
        ch.parent = upper
    upper.parent = node
    node.span_end = at
    node.tipSupport = 0
    node.children = [upper]
    return upper


def run_rules(rules: list, state: dict, params: dict):
    """Execute an ordered transition_rules list; returns the ret/guard value
    (None if it falls off the end, i.e. a void operation)."""
    loc: dict = dict(params)
    try:
        for st in rules:
            op = st["op"]
            if op == "find":
                loc[st["bind"]] = _find(state, _ev(st["of"], state, loc),
                                        st["mode"])
            elif op == "new_node":
                lg = loc.get("ledger") or params.get("ledger") or Ledger()
                n = Node(lg, int(_ev(st["span_start"], state, loc)),
                         int(_ev(st["span_end"], state, loc)),
                         int(_ev(st["tipSupport"], state, loc)))
                loc[st["bind"]] = n
            elif op == "split":
                tgt = loc.get(st["node"], state.get(st["node"]))
                loc[st["bind_new"]] = _split(tgt,
                                             int(_ev(st["at"], state, loc)))
            elif op == "attach":
                p = loc.get(st["parent"], state.get(st["parent"]))
                c = loc.get(st["child"], state.get(st["child"]))
                if c not in p.children:
                    p.children.append(c)
                c.parent = p
            elif op == "detach":
                p = loc.get(st["parent"], state.get(st["parent"]))
                c = loc.get(st["child"], state.get(st["child"]))
                if c in p.children:
                    p.children.remove(c)
                c.parent = None
            elif op == "add_tip":
                n = loc.get(st["node"], state.get(st["node"]))
                if n is not None:
                    n.tipSupport += int(_ev(st["delta"], state, loc))
            elif op == "add_branch_path":
                n = loc.get(st["node"], state.get(st["node"]))
                d = int(_ev(st["delta"], state, loc))
                for a in _ancestors(n) if n is not None else []:
                    a.branchSupport += d
            elif op == "compress":
                n = loc.get(st["node"], state.get(st["node"]))
                while (n is not None and n.parent is not None
                       and n.tipSupport == 0 and len(n.children) == 1):
                    ch = n.children[0]
                    n.span_end = ch.span_end
                    n.tipSupport = ch.tipSupport
                    n.ledger = ch.ledger
                    n.children = ch.children
                    for g in n.children:
                        g.parent = n
            elif op == "map_add":
                m = state[st["map"]]
                k = _ev(st["key"], state, loc)
                m[k] = m.get(k, 0) + int(_ev(st["delta"], state, loc))
                if m[k] == 0:
                    del m[k]
            elif op == "let":
                loc[st["bind"]] = _ev(st["expr"], state, loc)
            elif op == "walk":
                cur = loc.get(st["start"], state.get(st["start"]))
                loc[st["bind"]] = cur
                guard = 0
                while _ev(st["while"], state, loc):
                    loc[st["bind"]] = _ev(st["choose"], state, loc)
                    guard += 1
                    if guard > 10000:
                        break
            elif op == "guard_return":
                if _ev(st["cond"], state, loc):
                    raise _Return(_ev(st["expr"], state, loc))
            elif op == "ret":
                raise _Return(_ev(st["expr"], state, loc))
            else:
                raise ValueError(f"unknown step op {op!r}")
    except _Return as r:
        return r.value
    return None


# ---------------------------------------------------------------------------
# FSM-driven LedgerTrie model
# ---------------------------------------------------------------------------
class Model:
    def __init__(self, fsm: dict):
        self.fsm = fsm
        self.ops = {o["name"]: o for o in fsm["operations"]}
        self.queries = {q["name"]: q for q in fsm["queries"]}
        gen = Ledger("")
        self.state = {"root": Node(gen, 0, 1, 0), "seqSupport": {}}

    def _apply(self, name: str, **params):
        return run_rules(self.ops[name]["transition_rules"], self.state,
                         params)

    def _query(self, name: str, **params):
        q = self.queries[name]
        if "transition_rules" in q:
            return run_rules(q["transition_rules"], self.state, params)
        return _ev(q["result_expr"], self.state, params)

    # public surface matching trace_dumper
    def insert(self, hist, count):
        self._apply("insert", ledger=Ledger(hist), count=count)

    def remove(self, hist, count):
        return bool(self._apply("remove", ledger=Ledger(hist), count=count))

    def tip(self, hist):
        return int(self._query("tipSupport", ledger=Ledger(hist)) or 0)

    def branch(self, hist):
        return int(self._query("branchSupport", ledger=Ledger(hist)) or 0)

    def empty(self):
        return bool(self._query("empty"))

    def invariants(self):
        try:
            return bool(self._query("checkInvariants"))
        except Exception:
            return False

    def pref(self, largest):
        try:
            r = self._query("getPreferred", largestIssued=largest)
        except Exception:
            r = None
        if r is None:
            return None
        if isinstance(r, dict):
            return {"seq": r.get("seq"), "id": r.get("id")}
        return {"seq": int(r), "id": 0}  # id ignored by fidelity._norm


def main() -> None:
    fsm = json.loads(Path(sys.argv[1]).read_text())
    ops_file = sys.argv[2]
    m = Model(fsm)
    out = []
    for line in Path(ops_file).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        cmd = parts[0]
        rec = {"op": cmd}
        if cmd in ("insert", "remove"):
            hist = "" if parts[1] == "GENESIS" else parts[1]
            cnt = int(parts[2]) if len(parts) > 2 else 1
            rec["arg"] = hist
            rec["count"] = cnt
            rec["result"] = None if cmd == "insert" else m.remove(hist, cnt)
            if cmd == "insert":
                m.insert(hist, cnt)
        elif cmd == "pref":
            largest = int(parts[1])
            rec["arg"] = largest
            rec["result"] = m.pref(largest)
        elif cmd in ("tip", "branch"):
            hist = "" if parts[1] == "GENESIS" else parts[1]
            rec["arg"] = hist
            rec["result"] = m.tip(hist) if cmd == "tip" else m.branch(hist)
        else:
            continue
        rec["empty"] = m.empty()
        rec["invariants"] = m.invariants()
        out.append(rec)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
