#!/usr/bin/env bash
# Standalone build: real LedgerTrie.h + MockLedger, plain clang++, no Conan,
# no rippled build tree. The only rippled file touched is LedgerTrie.h itself
# (included by absolute path in trace_dumper.cpp); its 3 xrpl/* includes are
# satisfied by stubs/.
set -euo pipefail
cd "$(dirname "$0")"
clang++ -std=c++20 -O1 -Wall -Wextra \
    -I stubs \
    trace_dumper.cpp -o trace_dumper
echo "built: $(pwd)/trace_dumper"
