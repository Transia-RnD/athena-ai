#!/usr/bin/env python
# coding: utf-8

AGENT_MODEL = "gpt-4.1"
ATHENAH_CLIENT_NAME: str = "rippled-ai-core"


def main():
    from athenah_ai.client import AthenahClient

    ai_source: AthenahClient = AthenahClient(
        "id", "dist", ATHENAH_CLIENT_NAME, "v1", AGENT_MODEL, best_of=3
    )
    system_prompt: str = """
void
    testBatchCalculateBaseFee()
    {
        using namespace jtx;
        Env env(*this);
        Account const alice("alice");
        Account const bob("bob");
        env.fund(XRP(10000), alice, bob);
        env.close();

        auto const seq = env.seq(alice);
        auto const batchFee = batch::calcBatchFee(env, 0, 2);
        auto jtx = env.jt(batch::outer(alice, seq, batchFee, tfAllOrNothing),
            batch::inner(batch::outer(alice, seq, batchFee, tfAllOrNothing), seq),
            batch::inner(pay(alice, bob, XRP(1)), seq + 2),
            ter(telENV_RPC_FAILED));

        Serializer s;
        jtx.stx->add(s);

        // Calculate expected fee
        XRPAmount baseFee = Transactor::calculateBaseFee(*env.current(), *jtx.stx);
        std::cout << "Base fee: " << baseFee << std::endl;
        // XRPAmount fee1 = ripple::calculateBaseFee(*env.current(), *tx1.stx);
        // XRPAmount fee2 = ripple::calculateBaseFee(*env.current(), *tx2.stx);
        // XRPAmount expectedFee = env.current()->fees().base + baseFee + fee1 + fee2;

        // Call calculateBaseFee and check result
        XRPAmount actualFee = Batch::calculateBaseFee(*env.current(), *jtx.stx);
        std::cout << "Actual fee: " << actualFee << std::endl;
        BEAST_EXPECT(baseFee == actualFee);
    }

"""
    user_input: str = """
#19 failed: unhandled exception: Inner Batch transaction found

Make the test verify the throw. Return the test
"""
    response = ai_source.rag_prompt_v2(system_prompt, user_input)
    print(response)
main()
