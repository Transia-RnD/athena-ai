#pragma once
// Standalone stub of xrpl/basics/ToString.h.
// LedgerTrie.h includes this only for to_string() used on debug/getJson paths,
// which are template members and are NOT instantiated by the trace dumper.
// An empty header is therefore sufficient and keeps the harness rippled-free.
