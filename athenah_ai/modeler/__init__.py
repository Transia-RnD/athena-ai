"""
athenah_ai.modeler — Tier-A formal-model extraction & fidelity-gated checking.

Pipeline (see tasks/todo.md):
  extract    — schema-forced FSM extraction from real rippled C++
  model      — generate an executable Python model from the FSM
  fidelity   — HARD GATE: model must match real C++ step-for-step
  adversarial — adversarial questioner
  check      — explicit-state model checker (Python first)
  tla-port   — TLA+ port (credibility deliverable)

First Tier-A node: ripple::LedgerTrie (ships its own checkInvariants() oracle).
The C++ side lives in athenah_ai/modeler/harness/ as a *standalone* micro-harness
that compiles LedgerTrie.h against a hand-written MockLedger with plain clang++
(no Conan, no full rippled build) — see harness/README.md for the rationale.
"""

__all__: list[str] = []
