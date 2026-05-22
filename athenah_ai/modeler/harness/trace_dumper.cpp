// trace_dumper — applies an operation sequence to the REAL ripple::LedgerTrie
// (compiled from rippled's unmodified LedgerTrie.h) and emits, after every
// operation, a JSON record of the observable result + empty() + the built-in
// checkInvariants() oracle. This is the ground-truth side of the fidelity
// gate: the Python model is replayed against this exact trace.
//
// Input  : path to an ops file (argv[1]); one command per line:
//            insert <history> [count]
//            remove <history> [count]
//            pref   <largestIssuedSeq>
//            tip    <history>
//            branch <history>
//          blank lines and lines starting with '#' are ignored.
// Output : a JSON array of per-step records on stdout.

#include "mock_ledger.hpp"

#include "/Users/infinityworks/projects/xrplf/xrpld/src/xrpld/consensus/LedgerTrie.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

int
main(int argc, char** argv)
{
    if (argc < 2)
    {
        std::cerr << "usage: trace_dumper <ops-file>\n";
        return 2;
    }
    std::ifstream in(argv[1]);
    if (!in)
    {
        std::cerr << "cannot open " << argv[1] << "\n";
        return 2;
    }

    xrpl::LedgerTrie<mock::Ledger> trie;
    mock::History H;

    auto jstr = [](std::string const& s) {
        std::string o = "\"";
        for (char c : s)
            o += (c == '"' || c == '\\') ? std::string("\\") + c
                                         : std::string(1, c);
        return o + "\"";
    };
    auto jbool = [](bool b) { return std::string(b ? "true" : "false"); };

    std::cout << "[\n";
    std::string line;
    bool first = true;
    while (std::getline(in, line))
    {
        std::istringstream ls(line);
        std::string cmd;
        if (!(ls >> cmd) || cmd.empty() || cmd[0] == '#')
            continue;

        std::ostringstream rec;
        rec << "  {\"op\":" << jstr(cmd);

        if (cmd == "insert" || cmd == "remove")
        {
            std::string hist;
            std::uint32_t count = 1;
            ls >> hist;
            if (hist == "GENESIS")
                hist.clear();
            ls >> count;  // optional; leaves count=1 if absent
            rec << ",\"arg\":" << jstr(hist) << ",\"count\":" << count;
            if (cmd == "insert")
            {
                trie.insert(H[hist], count);
                rec << ",\"result\":null";
            }
            else
            {
                bool r = trie.remove(H[hist], count);
                rec << ",\"result\":" << jbool(r);
            }
        }
        else if (cmd == "pref")
        {
            std::uint32_t largest = 0;
            ls >> largest;
            rec << ",\"arg\":" << largest;
            auto p = trie.getPreferred(largest);
            if (p)
                rec << ",\"result\":{\"seq\":" << p->seq
                    << ",\"id\":" << p->id << "}";
            else
                rec << ",\"result\":null";
        }
        else if (cmd == "tip" || cmd == "branch")
        {
            std::string hist;
            ls >> hist;
            if (hist == "GENESIS")
                hist.clear();
            rec << ",\"arg\":" << jstr(hist);
            std::uint32_t v = (cmd == "tip") ? trie.tipSupport(H[hist])
                                             : trie.branchSupport(H[hist]);
            rec << ",\"result\":" << v;
        }
        else
        {
            continue;  // unknown command: skip silently
        }

        rec << ",\"empty\":" << jbool(trie.empty())
            << ",\"invariants\":" << jbool(trie.checkInvariants()) << "}";

        std::cout << (first ? "" : ",\n") << rec.str();
        first = false;
    }
    std::cout << "\n]\n";
    return 0;
}
