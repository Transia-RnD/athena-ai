#!/usr/bin/env bash
# One-command reproduction of athenah_ai/modeler/FINDING.md.
#
# Does NOT re-run the LLM extraction (the validated FSM artefact is committed
# at artifacts/ledger_trie.fsm.json). Builds the standalone C++ ground-truth
# dumper if needed, then runs the differential fidelity gate on rippled's own
# LedgerTrie_test.cpp vectors.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x harness/trace_dumper ]; then
    echo "[reproduce] building standalone C++ harness (plain clang++, no Conan)..."
    bash harness/build.sh
fi

echo "[reproduce] differential fidelity gate vs real ripple::LedgerTrie:"
for v in test_insert test_support; do
    poetry run python -m athenah_ai.modeler.fidelity \
        --ops "harness/vectors/${v}.ops" 2>&1 | head -1 || true
done

cat <<'EOF'

Expected (matches FINDING.md):
  test_insert  : 0 / 4   ( 0.0%)
  test_support : 4 / 31  (12.9%)

The model is closed, validated, executable — and silently wrong starting at
`insert abc`. See FINDING.md for the full write-up.
EOF
