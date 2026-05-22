"""
Fidelity gate (differential test).

Runs the SAME operation sequence through:
  * the C++ trace_dumper  (the real ripple::LedgerTrie — GROUND TRUTH)
  * the Python model       (deterministic interpreter of the extracted FSM)
and diffs them step-for-step. The model only earns the right to be
model-checked if it matches the real implementation EXACTLY on the real
rippled test vectors. Anything less means checking fiction.

This file is FSM-independent: it is the measuring instrument, usable the
moment a model.py exists, and also usable standalone to emit the C++
ground-truth trace for the one-time golden cross-check.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).parent / "harness"


def _build_dumper(harness_dir: Path) -> Path:
    binp = harness_dir / "trace_dumper"
    if not binp.exists():
        subprocess.run(["bash", str(harness_dir / "build.sh")], check=True)
    return binp


def _run(cmd: list[str]) -> list[dict]:
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"{cmd!r} failed rc={out.returncode}\n{out.stderr}")
    return json.loads(out.stdout)


# Only these keys define observable behaviour; raw ids may differ between the
# C++ id-registry and the model's, so getPreferred results are compared
# structurally (present/seq) not on the absolute id integer.
def _norm(step: dict) -> tuple:
    r = step.get("result")
    if isinstance(r, dict):  # getPreferred -> {seq,id}
        r = ("pref", r.get("seq"))
    return (step.get("op"), step.get("arg"), step.get("count"),
            r, step.get("empty"), step.get("invariants"))


def diff(truth: list[dict], model: list[dict]) -> tuple[int, int, list[str]]:
    n = max(len(truth), len(model))
    ok = 0
    notes: list[str] = []
    for i in range(n):
        t = truth[i] if i < len(truth) else None
        m = model[i] if i < len(model) else None
        if t is None or m is None:
            notes.append(f"step {i}: length mismatch (truth={t}, model={m})")
            continue
        if _norm(t) == _norm(m):
            ok += 1
        else:
            notes.append(f"step {i}: op={t.get('op')} arg={t.get('arg')!r}\n"
                         f"    C++   : {_norm(t)}\n"
                         f"    model : {_norm(m)}")
    return ok, n, notes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ops", required=True, help="ops vector file")
    ap.add_argument("--fsm", default=str(Path(__file__).parent /
                    "artifacts" / "ledger_trie.fsm.json"))
    ap.add_argument("--model", default=str(Path(__file__).parent /
                    "model_runner.py"))
    ap.add_argument("--harness-dir", default=str(HARNESS))
    ap.add_argument("--emit-truth", action="store_true",
                    help="only print the C++ ground-truth trace and exit")
    args = ap.parse_args()

    dumper = _build_dumper(Path(args.harness_dir))
    truth = _run([str(dumper), args.ops])

    if args.emit_truth:
        print(json.dumps(truth, indent=2))
        return

    if not Path(args.model).exists():
        print(f"[fidelity] model not found: {args.model}")
        sys.exit(2)

    model = _run([sys.executable, args.model, args.fsm, args.ops])
    ok, n, notes = diff(truth, model)
    pct = 100.0 * ok / n if n else 0.0
    print(f"[fidelity] {args.ops}: {ok}/{n} steps match ({pct:.1f}%)")
    for nt in notes[:20]:
        print("  " + nt)
    # The gate: 100% or it does not pass.
    sys.exit(0 if ok == n and n > 0 else 1)


if __name__ == "__main__":
    main()
