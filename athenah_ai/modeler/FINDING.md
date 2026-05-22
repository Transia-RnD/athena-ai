# Closing the LLM-Extracted-Formal-Model Gap on Real XRPL Consensus Code: An Empirical End-to-End Test

**One-line:** Closure-gated, staged LLM extraction can produce a *structurally
valid, closed, executable* formal model of real `rippled` consensus code in an
afternoon — but a differential fidelity gate against the C++ implementation
catches it as **semantically unfaithful** on rippled's own first test vectors.
Validation ≠ fidelity, demonstrated end-to-end with a reproducible harness.

## TL;DR (skim this)

**Receipt:** running the differential gate on rippled's own `LedgerTrie_test.cpp`
vectors produces these numbers (reproducible from disk in one command):

```
test_insert  : 0 /  4 steps match  ( 0.0%)
test_support : 4 / 31 steps match  (12.9%)
```

The 12.9% is *not* random failure — it is exactly the empty-trie reads
matching (`tip a`=0, `checkInvariants`=True), then divergence beginning the
instant `insert abc` runs, because the LLM-extracted `insert` silently elides
the divergence guard the real `LedgerTrie::insert` has. The model is closed,
validated, executable — and silently wrong.

**The cost is in the wrong place:**

| Workstream | Reality on this evidence | Closable? |
|---|---|---|
| Build an LLM-agent pipeline to *produce* a closed formal model | Weekend of careful Agent SDK plumbing (the pipeline is in this repo, running, with raw-output caching and a repair loop) | YES — already done here |
| *Validate* that the model matches the implementation | **0%/12.9% out of the box** on the first real test vector before any fuzzing | This is the actual research |
| Refinement proof (TLA+/C++) | Not addressed | seL4-class, not LLM-shaped |

**Net:** the headline deliverable (produce a closed model) is the cheap part;
the part everyone hand-waves — fidelity to the implementation — is what
actually resists. The receipt is below.

---

## The question

Two claims are routinely conflated when people talk about applying LLM-driven
formal methods to consensus protocols:

1. *Producing a formal model.* "An LLM reads the code and emits TLA+ / a state
   machine." Treated as the main engineering deliverable.
2. *That model being faithful enough to model-check meaningfully.* Usually
   waved away as "reconciliation with the implementation."

I wanted to know whether (1) implies (2) on a real consensus component:
`ripple::LedgerTrie` ([LedgerTrie.h][lt]) — the radix-trie at the heart of XRP
Ledger's no-fork preferred-branch logic. I chose it because it ships its own
in-code invariant oracle (`checkInvariants()`, [LedgerTrie.h:790-826][ci]) and
a comprehensive existing test suite ([LedgerTrie_test.cpp][lttest]) — i.e. a
fidelity oracle exists.

## What I built (and why each piece is here)

Four artefacts; the design point of each is to *not let the LLM be its own
judge*.

| Stage | Code | Role |
|---|---|---|
| Schema + closure gate | [schema.py](schema.py) | Rejects prose-in-JSON: every name in every expression must resolve to a declared state-var, param, step-bound local, or an enumerated primitive; attribute access restricted to a fixed `NODE_FIELDS`. Each operation/complex query must carry `transition_rules` drawn ONLY from a closed step vocabulary (`find`/`split`/`new_node`/`attach`/`add_tip`/`add_branch_path`/`compress`/`map_add`/`let`/`walk`/`guard_return`/`ret`). |
| Staged extractor | [extractor.py](extractor.py) | One small structure-pass + one focused per-unit pass per operation/query (parallelised). Forced by the SDK stream idle-timeout that killed monolithic extraction. Validator-driven repair loop. Raw-output cache so faithful units are not re-run while debugging the harness. |
| C++ ground-truth dumper | [harness/trace_dumper.cpp](harness/trace_dumper.cpp) | Compiles the unmodified [LedgerTrie.h][lt] against a 120-line `MockLedger` matching the documented Ledger contract; emits a structured JSON trace of every step's `tip`/`branch`/`getPreferred`/`empty`/`checkInvariants`. Plain `clang++ -std=c++20`, zero Conan, zero rippled build. |
| Differential gate + model | [fidelity.py](fidelity.py), [model_runner.py](model_runner.py) | Deterministic interpreter of the closed step vocabulary (one fixed implementation per primitive — *not* an agent porting C++). Same operation sequence runs through the C++ and the model; step-for-step diff with a 100%-or-fail gate. |

## The four findings, in the order I hit them

### Finding 1 — A loose schema accepts prose-in-JSON

First-pass schema requiring `effects` + closed predicates produced a "valid"
FSM whose effects called undefined helper methods:

```
"expr": "root.split_at_diff(ledger) if root.find(ledger).span_end > ... else root.extend_child(ledger, count)"
```

`split_at_diff`, `extend_child`, `decrement_and_compress`, `walk_preferred` —
none defined. The model *looks* formal; building from it would test the
model-writer, not the extraction. **Schema fix:** the closure gate
(`schema.py`), and a required `transition_rules` primitive-step vocabulary.

### Finding 2 — Forced operational decomposition breaks monolithic extraction

A single-agent run forced to decompose `LedgerTrie`'s real split/compress/walk
algorithm in one session blew the Claude Agent SDK's stream idle-timeout
(~16 min, 3 turns, `is_error=True`). No timeout knob exists.
**Architectural fix:** stage the work — one small structure call + one
focused per-unit call (parallelised). Structure now completes in ~2.5 min.

### Finding 3 — Closure exposed a *schema* gap, not just a model gap

Complex queries (e.g. `getPreferred`'s trie walk) are themselves algorithms,
not closed expressions. The closure rule made them unrepresentable. **Schema
fix:** queries may carry `transition_rules` too; vocabulary extended with
`walk`/`let` (and `nodes`/`ancestors` as documented closed traversal
primitives).

### Finding 4 — Even after all of that, the model fails the fidelity gate

After schema-hardening, staging, and one repair round, the staged pipeline
produced a fully closed, validated FSM: `insert` 9 steps, `remove` 8,
`getPreferred` 6, `checkInvariants` 10. No `split_at_diff` anywhere.

Then I ran the differential gate on real rippled vectors transcribed
verbatim from `LedgerTrie_test.cpp::testInsert` / `testSupport`:

```
test_support : 4 / 31 steps match  (12.9%)
test_insert  : 0 /  4 steps match  ( 0.0%)
```

Steps 0–3 of `test_support` (reads on the empty trie) match exactly,
**including `checkInvariants=True`** — confirming the extracted invariants
are faithful (they are essentially the in-code oracle, independently
recovered).

Divergence begins precisely at step 4: `insert abc`. The extracted `insert`
calls `split(loc, at=diff_seq)` *unconditionally*, lacking the divergence
guard real `LedgerTrie::insert` has — producing a degenerate trie:

```
TRIE after `insert abc`:
  span[0,1) tip=0 br=1 hist=''   kids=2
    span[1,1) tip=0 br=0 hist=''   kids=0     <-- junk node
    span[1,4) tip=1 br=1 hist='abc' kids=0
```

That junk node violates the compression invariant that the *same FSM*
correctly specifies, so `checkInvariants` flips False; `find exact` for
`abc` descends into the junk node first and returns `None`, so
`tipSupport(abc)` returns 0 instead of 1. The model is closed, validated,
executable — **and silently wrong**, in a way no purely structural check on
the FSM could have caught.

This precisely matches a prediction I recorded *before* running the fidelity
gate ([tasks/todo.md](../../tasks/todo.md): "insert binds suf_node from split
but never re-attaches → split sequences should diverge").

### Disclosed confound

Two **interpreter** bugs initially contaminated the fidelity number (eval/
comprehension scoping; `nodes` call-vs-value). They were diagnosed and fixed
*before* attributing failure to the extraction — fixing them moved
`test_support` from 0% → 12.9%, recovering exactly the empty-trie reads.
The remaining 27/31 divergence is genuinely the extraction. The interpreter
fixes are in [model_runner.py](model_runner.py) and were made strictly toward
the vocabulary contract documented in [schema.py](schema.py), never toward
making the FSM pass.

## What this proves

- The *agentic extraction* is a solved-with-care engineering exercise on real consensus code.
- A schema can structurally force closure (no undefined helpers, fixed step
  vocabulary), and an LLM **can** decompose real radix-trie operations into
  it — given hardening, staging, and a feedback repair round. **The gap is
  closable for "produce a closed model."**
- That closed model **is not faithful** out of the box. The extracted
  `insert` silently elides a guard the real algorithm has. The defect was
  caught only by differential execution against the real C++ — not by any
  property of the model itself.
- Therefore the hard, unsolved part is the one everyone hand-waves:
  **the refinement / conformance step between the extracted model and the
  implementation**. The 12.9% fidelity number on the *first* rippled test
  vector, before any adversarial fuzzing, is the receipt.

## What this does NOT prove

- The fidelity-gate-to-extractor repair loop *might* converge to 100% fidelity
  with several feedback cycles. I chose to bank rather than grind, so I did
  not run that test.
- Other consensus components may decompose more or less faithfully than
  `LedgerTrie`.
- A bounded model-check is not a refinement proof; the genuinely hard
  proof-vs-C++ step is not addressed here at all.

## Reproduction

```bash
# 0. one-time C++ harness build (plain clang++; no Conan)
cd athenah_ai/modeler/harness && ./build.sh

# 1. run the staged FSM extractor (uses raw_*.txt cache after first success)
poetry run python -m athenah_ai.modeler.extractor \
    --out athenah_ai/modeler/artifacts/ledger_trie.fsm.json

# 2. run the differential fidelity gate on real rippled test vectors
poetry run python -m athenah_ai.modeler.fidelity \
    --ops athenah_ai/modeler/harness/vectors/test_support.ops
poetry run python -m athenah_ai.modeler.fidelity \
    --ops athenah_ai/modeler/harness/vectors/test_insert.ops
```

The vectors in `harness/vectors/` are transcribed verbatim from
[`src/test/consensus/LedgerTrie_test.cpp`][lttest]; the C++ run on them is the
fidelity oracle.

[lt]: /Users/infinityworks/projects/xrplf/xrpld/src/xrpld/consensus/LedgerTrie.h
[ci]: /Users/infinityworks/projects/xrplf/xrpld/src/xrpld/consensus/LedgerTrie.h#L790
[lttest]: /Users/infinityworks/projects/xrplf/xrpld/src/test/consensus/LedgerTrie_test.cpp
