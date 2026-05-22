#pragma once
// Standalone stub of xrpl/beast/utility/instrumentation.h.
// Mirrors the real macro surface (see rippled include/xrpl/beast/utility/
// instrumentation.h) so LedgerTrie.h's XRPL_ASSERT / UNREACHABLE compile and
// behave identically (assert-on-false) with zero rippled coupling.
#include <cassert>

#define ALWAYS_OR_UNREACHABLE(cond, message) assert((message) && (cond))
#define UNREACHABLE(message, ...) assert((message) && false)
#define XRPL_ASSERT ALWAYS_OR_UNREACHABLE
#define XRPL_ASSERT_PARTS(cond, function, description, ...) \
    XRPL_ASSERT(cond, function " : " description)
