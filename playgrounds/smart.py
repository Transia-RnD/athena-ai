#!/usr/bin/env python
# coding: utf-8

ATHENAH_CLIENT_NAME: str = "rippled-smart-core"


def main():
    # from athenah_ai.indexer import AthenahIndexer

    # path: str = "/Users/darkmatter/projects/ledger-works/rippled"
    # indexer = AthenahIndexer("local", "id", "dist", "rippled-smart-core", "v1")
    # indexer.build_from_dirs(path, ["include", "src/libxrpl", "src/xrpld"], False, True)

    from athenah_ai.client import AthenahClient

    ai_source: AthenahClient = AthenahClient(
        "id",
        # provider="anthropic",
        provider="openai",
        # provider="xai",
        model_group="dist",
        custom_model="rippled-smart-core",
        version="v1",
        # model_name="claude-4-sonnet",
        model_name="gpt-4.1",
        # model_name="grok-4",
        temperature=0,
        best_of=5,
    )
    # get file content from file list
    # content = ""
    # file_list = [
    #     "/Users/darkmatter/projects/ledger-works/rippled/src/xrpld/app/misc/ContractHostFuncImpl.cpp",
    #     "/Users/darkmatter/projects/ledger-works/rippled/src/libxrpl/protocol/STBase.cpp",
    #     "/Users/darkmatter/projects/ledger-works/rippled/src/libxrpl/protocol/STObject.cpp",
    # ]
    # for file_path in file_list:
    #     with open(file_path, "r") as f:
    #         content += f.read() + "\n\n"
    system_prompt: str = """
"""
    user_input: str = """
How many bytes are ltMPTOKEN_ISSUANCE and ltMPTOKEN? Return a break down of each field and its size in bytes. Return the total size in bytes. Return the answer in JSON format with field names and sizes.

Look up each field type in the sfields.macro file to get the size in bytes.

LEDGER_ENTRY(ltMPTOKEN_ISSUANCE, 0x007e, MPTokenIssuance, mpt_issuance, ({
    {sfIssuer,                   soeREQUIRED},
    {sfSequence,                 soeREQUIRED},
    {sfTransferFee,              soeDEFAULT},
    {sfOwnerNode,                soeREQUIRED},
    {sfAssetScale,               soeDEFAULT},
    {sfMaximumAmount,            soeOPTIONAL},
    {sfOutstandingAmount,        soeREQUIRED},
    {sfLockedAmount,             soeOPTIONAL},
    {sfMPTokenMetadata,          soeOPTIONAL},
    {sfPreviousTxnID,            soeREQUIRED},
    {sfPreviousTxnLgrSeq,        soeREQUIRED},
    {sfDomainID,                 soeOPTIONAL},
    {sfMutableFlags,             soeDEFAULT},
}))

/** A ledger object which tracks MPToken
    \sa keylet::mptoken
 */
LEDGER_ENTRY(ltMPTOKEN, 0x007f, MPToken, mptoken, ({
    {sfAccount,                  soeREQUIRED}, // 20 bytes
    {sfMPTokenIssuanceID,        soeREQUIRED}, // 24 bytes
    {sfMPTAmount,                soeDEFAULT}, // 8 bytes
    {sfLockedAmount,             soeOPTIONAL}, // 8 bytes
    {sfOwnerNode,                soeREQUIRED}, // 4 bytes
}))

// Total = 20 + 24 + 8 + 8 + 4 = 64 bytes

Compare with the ltRIPPLE_STATE

LEDGER_ENTRY(ltRIPPLE_STATE, 0x0072, RippleState, state, ({
    {sfBalance,              soeREQUIRED}, // 48 bytes
    {sfLowLimit,             soeREQUIRED}, // 48 bytes
    {sfHighLimit,            soeREQUIRED}, // 48 bytes
    {sfLowNode,              soeOPTIONAL},  // 4 bytes
    {sfHighNode,             soeOPTIONAL}, // 4 bytes
}))

// Total = 48 + 48 + 48 + 4 + 4 = 152 bytes

However this is the typical size for ripple state:

Amounts (Balance, LowLimit, HighLimit) should be counted as 48 bytes.

Balance:
{...}, // 3 items
Flags:
1179648,
HighLimit:
{...}, // 3 items
HighNode:
"4",
LedgerEntryType:
"RippleState",
LowLimit:
{...}, // 3 items
LowNode:
"0",
PreviousTxnID:
"C6879A1B873E00009C3FD6A0030219B703801DABC58F108155FCE411133B7446",
PreviousTxnLgrSeq:
89690340,
index:
"E158165BAF502A91654F6343535DC11D4764A602532F6F50CCB10EB4A37F5909"

Do not make things up. 

"""
    system_prompt = system_prompt + "\n" + user_input
    response = ai_source.agent_prompt("Developer", "Developer Coder", system_prompt)
    # write to a file
    with open("response.txt", "w") as f:
        f.write(response)


main()
