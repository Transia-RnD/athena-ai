#pragma once
// MockLedger — a standalone re-implementation of rippled's csf::Ledger DSL,
// using exactly the model the real LedgerTrie_test.cpp uses: a ledger IS its
// history string. h["abc"] is a seq-3 ledger with ancestry a -> ab -> abc;
// the empty string is genesis; a shared string prefix == shared ancestors,
// which is precisely the "unique history" invariant documented at
// LedgerTrie.h:308-318.
//
// This satisfies the Ledger contract at LedgerTrie.h:274-306. It is a
// deliberate hand-written mock: reusing csf::Ledger would drag boost +
// xrpl/basics back in. Its fidelity is proven separately by a ONE-TIME
// golden run of `rippled --unittest=ripple.consensus.LedgerTrie`
// (see tasks/todo.md).

#include <cstdint>
#include <map>
#include <string>

namespace mock {

// The contract only requires Seq/ID to be equality-comparable and copyable,
// and Seq additionally ordered (LedgerTrie keeps a std::map<Seq,...>). Plain
// uint32 satisfies both with identical integer semantics to csf's
// TaggedInteger; ID{0} is the reserved "unknown ancestor" value.
using Seq = std::uint32_t;
using ID = std::uint32_t;

// Global prefix -> ID registry so equal histories (and equal prefixes of
// different ledgers) always resolve to the same ID. ID 0 is reserved/unknown;
// genesis ("") is registered first and gets ID 1.
inline ID
idOf(std::string const& history)
{
    static std::map<std::string, ID> registry;
    static ID next = 1;
    auto [it, inserted] = registry.try_emplace(history, next);
    if (inserted)
        ++next;
    return it->second;
}

class Ledger
{
public:
    using Seq = mock::Seq;
    using ID = mock::ID;

    struct MakeGenesis
    {
    };

    Ledger(MakeGenesis) : history_{}
    {
    }
    explicit Ledger(std::string history) : history_{std::move(history)}
    {
    }

    Ledger() : history_{} {}
    Ledger(Ledger const&) = default;
    Ledger&
    operator=(Ledger const&) = default;

    // Sequence number == length of the history chain.
    Seq
    seq() const
    {
        return static_cast<Seq>(history_.size());
    }

    // ID of this ledger's ancestor at sequence number s, or ID{0} if unknown
    // (s beyond this ledger's own sequence).
    ID
    operator[](Seq s) const
    {
        if (s > seq())
            return ID{0};
        return idOf(history_.substr(0, s));
    }

    // ID of this ledger itself.
    ID
    id() const
    {
        return idOf(history_);
    }

    std::string const&
    history() const
    {
        return history_;
    }

private:
    std::string history_;
};

// First sequence number at which the two ledgers' ancestry can differ.
// Found by ADL from LedgerTrie's unqualified mismatch(a, b) calls.
inline Seq
mismatch(Ledger a, Ledger b)
{
    Seq const m = a.seq() < b.seq() ? a.seq() : b.seq();
    for (Seq s = 1; s <= m; ++s)
        if (a[s] != b[s])
            return s;
    return m + 1;
}

// Test-DSL builder: H["abc"] -> Ledger with history "abc"; H[""] -> genesis.
struct History
{
    Ledger
    operator[](std::string const& h) const
    {
        return Ledger{h};
    }
};

}  // namespace mock
