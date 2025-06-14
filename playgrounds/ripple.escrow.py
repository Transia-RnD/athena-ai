#!/usr/bin/env python
# coding: utf-8

# from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/rippled"
# indexer = AthenahIndexer("local", "id", "dist", "rippled-escrow", "v1")
# indexer.build_from_dirs(
#     path,
#     ["include", "src/libxrpl", "src/test", "src/xrpld"],
#     True,
# )

from athenah_ai.client import AthenahClient

prompt: str = """
```
/** returns true if adding or subtracting results in less than or equal to
 * 0.01% precision loss **/
inline bool
isAddable(STAmount const& amt1, STAmount const& amt2)
{
    // special case: adding anything to zero is always fine
    if (amt1 == beast::zero || amt2 == beast::zero)
        return true;

    // special case: adding two xrp amounts together.
    // this is just an overflow check
    if (isXRP(amt1) && isXRP(amt2))
    {
        XRPAmount A = (amt1.signum() == -1 ? -(amt1.xrp()) : amt1.xrp());
        XRPAmount B = (amt2.signum() == -1 ? -(amt2.xrp()) : amt2.xrp());

        if ((B > XRPAmount{0} &&
             A > std::numeric_limits<XRPAmount::value_type>::max() - B) ||
            (B < XRPAmount{0} &&
             A < std::numeric_limits<XRPAmount::value_type>::min() - B))
        {
            return false;
        }

        XRPAmount finalAmt = A + B;
        return (finalAmt >= A && finalAmt >= B);
    }

    static const STAmount one{IOUAmount{1, 0}, noIssue()};
    static const STAmount maxLoss{IOUAmount{1, -4}, noIssue()};

    STAmount A = amt1;
    STAmount B = amt2;

    if (isXRP(A))
        A = STAmount{IOUAmount{A.xrp().drops(), -6}, noIssue()};

    if (isXRP(B))
        B = STAmount{IOUAmount{B.xrp().drops(), -6}, noIssue()};

    A.setIssue(noIssue());
    B.setIssue(noIssue());

    STAmount lhs = divide((A - B) + B, A, noIssue()) - one;
    STAmount rhs = divide((B - A) + A, B, noIssue()) - one;

    return ((rhs.negative() ? -rhs : rhs) + (lhs.negative() ? -lhs : lhs)) <=
        maxLoss;
}
```

we should also support MPT in this function as well if MPT is going to use it. MPT will be similar to XRP except it has a higher range at 61 bits. If this function is not meant for MPTs, then we should assert the the params aren't MPT and/or return false

"""
client = AthenahClient("id", "dist", "rippled-escrow", "v1", "gpt-4.1")
response = client.promptv1(prompt)
print(response)
