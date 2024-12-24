#!/usr/bin/env python
# coding: utf-8

from athenah_ai.utils.fs import get_top_level_directories
from athenah_ai.indexer import AthenahIndexer
from typing import List

# path: str = "/Users/darkmatter/projects/ledger-works/xhs-library"
# indexer = AthenahIndexer("local", "id", "dist", "xhs-library", "v1")
# dirs: List[str] = get_top_level_directories(path)
# indexer.index_whitelist(path, dirs, "xhs-library")

from athenah_ai.client import AthenahClient

client = AthenahClient("id", "dist", "xhs-library")

prompt: str = """

You are a coding agent. You have been tasked with writing a hook function that will be called when a user requests their account balance. The hook function will be called with a reserved parameter. The hook function should return the account balance as an integer.

Rules:

- Hooks are written in c.
- Hook for loops must include the GUARD.
- All hooks must include a GUARD. If there are no for loops then the _g(1,1) must be included.
- Hooks are not turing complete:
 - they must use the accept and reject.
 - they must use a MACRO for all outside functions.
 - they must use TRACESTR, TRACEHEX, TRACEVAR for logging.
 - they must use SBUF for all string buffers.
 - they cannot use memcpy, memset, or any other memory manipulation functions.
 - they cannot use any functions that are not defined in the hookapi.h file.
- Return the full code. 
- The code must compile and work.
 
MACRO:
```
#define ACCOUNT_TO_BUF(buf_raw, i)\
{\
    unsigned char* buf = (unsigned char*)buf_raw;\
    *(uint64_t*)(buf + 0) = *(uint64_t*)(i +  0);\
    *(uint64_t*)(buf + 8) = *(uint64_t*)(i +  8);\
    *(uint32_t*)(buf + 16) = *(uint32_t*)(i + 16);\
}
```

```Hook.c

#include <stdint.h>
#include "hookapi.h"

#define DONE(x)\
    return accept(SBUF(x), __LINE__)

#define NOPE(x)\
    return rollback(SBUF(x), __LINE__)

#define LOAD_BALANCE(accid, kl, slot_num, field) { \
    util_keylet(SBUF(kl), KEYLET_ACCOUNT, accid, 48, 0,0,0,0); \
    if (slot_set(SBUF(kl), slot_num) != 20) \
        accept(SBUF("MACROS: Could not load `AccountRoot` Ledger Entry"), __LINE__); \
    if (slot_subfield(slot_num, field, 1) != 20) \
        accept(SBUF("MACROS: Could not load `Field` on AccountRoot"), __LINE__); \
}

#define RETURN_BALANCE_WITH_RESERVE() \
{ \
    int64_t balance = slot_float(1); \
    int64_t account_reserve = 2; \
    int64_t object_reserve = 0.02; \
    int64_t object_count = 10; \
    int64_t adjusted_balance = balance - reserve - (object_count * object_reserve); \
    if (adjusted_balance < 0) \
        reject(SBUF("Insufficient balance after reserve deduction"), __LINE__); \
    return adjusted_balance; \
}

#define sfAmounts 0xF005C
#define ttREMIT 95U
#define HASH256_SIZE 32U
#define AMT_SIZE 8U
#define ACCID_SIZE 20U
#define SEQ_SIZE 4U


// clang-format off
uint8_t txn[6000] =
{
/* size,upto */
/*   3,   0 */   0x12U, 0x00U, 0x5FU,                                                           /* tt = Remit       */
/*   5,   3 */   0x22U, 0x80U, 0x00U, 0x00U, 0x00U,                                          /* flags = tfCanonical */
/*   5,   8 */   0x24U, 0x00U, 0x00U, 0x00U, 0x00U,                                                 /* sequence = 0 */
/*   5,  13 */   0x99U, 0x99U, 0x99U, 0x99U, 0x99U,                                                /* dtag, flipped */
/*   6,  18 */   0x20U, 0x1AU, 0x00U, 0x00U, 0x00U, 0x00U,                                      /* first ledger seq */
/*   6,  24 */   0x20U, 0x1BU, 0x00U, 0x00U, 0x00U, 0x00U,                                       /* last ledger seq */
/*   9,  30 */   0x68U, 0x40U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U,                         /* fee      */
/*  35,  39 */   0x73U, 0x21U, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,       /* pubkey   */
/*  22,  74 */   0x81U, 0x14U, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                                  /* srcacc  */
/*  22,  96 */   0x83U, 0x14U, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                                  /* dstacc  */
/* 116, 118 */   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,    /* emit detail */
                 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
/*   2, 234 */   0xF0U, 0x5CU,                                                               /* lead-in amount array */
/*   2, 236 */   0xE0U, 0x5BU,                                                              /* lead-in amount entry A*/
/*  49, 238 */   0x61U,0,0,0,0,0,0,0,0,
                 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,                                                /* amount A */
                 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
/*   2, 287 */   0xE1U, 0xF1U,                                                 /* lead out, may also appear at end of A */
/*   0, 289 */                
};
// clang-format on

// TX BUILDER
#define FLS_OUT (txn + 20U)
#define LLS_OUT (txn + 26U)
#define DTAG_OUT (txn + 14U)
#define FEE_OUT (txn + 31U)
#define HOOK_ACC (txn + 76U)
#define OTX_ACC (txn + 98U)
#define EMIT_OUT (txn + 118U)
#define AMOUNT_OUT (txn + 238U)

// master_ns: 32 bytes
uint8_t master_ns[32] = {
    0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,0xCAU,0xF8U,0xB2U,0x97U,
    0xCFU,0xF8U,0xF2U,0xF9U,0x37U,0xE8U,0xB5U,0xF7U,0x62U,0x79U,
    0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,0xCAU,0xF8U,0xB2U,0x97U,
    0xCFU,0xF8U,0xF2U,0xF9U};

// master_accid: 20 bytes
uint8_t master_accid[20] =
    {0xB5U,0xF7U,0x62U,0x79U,0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,
     0xCAU,0xF8U,0xB2U,0x97U,0xCFU,0xF8U,0xF2U,0xF9U,0x37U,0xE8U};

// offers_ns: 32 bytes
uint8_t offers_ns[32] = {
    0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,0xCAU,0xF8U,0xB2U,0x97U,
    0xCFU,0xF8U,0xF2U,0xF9U,0x37U,0xE8U,0xB5U,0xF7U,0x62U,0x79U,
    0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,0xCAU,0xF8U,0xB2U,0x97U,
    0xCFU,0xF8U,0xF2U,0xF9U};

// sell_offers_ns: 32 bytes
uint8_t sell_offers_ns[32] = {
    0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,0xCAU,0xF8U,0xB2U,0x97U,
    0xCFU,0xF8U,0xF2U,0xF9U,0x37U,0xE8U,0xB5U,0xF7U,0x62U,0x79U,
    0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,0xCAU,0xF8U,0xB2U,0x97U,
    0xCFU,0xF8U,0xF2U,0xF9U};

// buy_offers_ns: 32 bytes
uint8_t buy_offers_ns[32] = {
    0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,0xCAU,0xF8U,0xB2U,0x97U,
    0xCFU,0xF8U,0xF2U,0xF9U,0x37U,0xE8U,0xB5U,0xF7U,0x62U,0x79U,
    0x8AU,0x53U,0xD5U,0x43U,0xA0U,0x14U,0xCAU,0xF8U,0xB2U,0x97U,
    0xCFU,0xF8U,0xF2U,0xF9U};

#define OFFER_MODEL 20U


int64_t cbak(uint32_t f)
{
    // TODO track withdrawal txns to see if they successfully executed
    return 0;
}

int64_t hook(uint32_t r)
{
    _g(1,1);

    hook_account(HOOK_ACC, ACCID_SIZE);
    otxn_field(OTX_ACC, ACCID_SIZE, sfAccount);

    uint8_t seq[4];
    otxn_field(SBUF(seq), sfSequence);

    if (BUFFER_EQUAL_20(HOOK_ACC, OTX_ACC))
        DONE("001-Broker: passing outgoing txn");

    int64_t tt = otxn_type();
    if (tt != ttINVOKE && tt != ttREMIT)
        NOPE("001-Broker: Rejecting non-Invoke, non-Remit txn.");

    uint8_t issuer_accid[ACCID_SIZE];
    if (hook_param(SBUF(issuer_accid), "I", 1) != ACCID_SIZE)
        NOPE("001-Broker: Misconfigured. Missing `I` install parameter.");

    uint8_t op;
    if (otxn_param(&op, 1, "OP", 2) != 1)
        NOPE("001-Broker: Missing OP parameter.");

    // sanity check - ttREMIT
    if ((op == 'C') && tt != ttREMIT)
        NOPE("001-Broker: Create operation must be a remit transaction.");
    
    // sanity check - ttINVOKE
    if ((op == 'R' || op == 'D') && tt != ttINVOKE)
        NOPE("001-Broker: Remove/Distribute operations must be an invoke transaction.");

    // enforced pausedness
    if (op != 'U')
    {
        uint8_t paused;
        state_foreign(&paused, 1, "P", 1, SBUF(master_ns), SBUF(master_accid));
        if (paused)
            NOPE("001-Broker: Paused.");
    }

    otxn_slot(1);

    // action
    switch (op)
    {
        case 'C':
        {
            // Create Offer
            uint8_t tid[HASH256_SIZE];
            if (otxn_param(SBUF(tid), "TID", 3) == HASH256_SIZE)
                NOPE("001-Broker: Missing `TID` parameter.");

            // TODO: Validate OTXN Account is URIToken Owner

            // check how many currencies were sent
            int64_t sent_currency_count =
                slot_subfield(1, sfAmounts, 2) == 2
                ? slot_count(2)
                : 0;

            if (sent_currency_count != 1)
                NOPE("001-Broker: Only one currency allowed.");

            uint8_t sent_cur[49];
            if (slot_subarray(2, 0, 3) != 3)
                NOPE("001-Broker: Error slotting currency");

            slot_subfield(3, sfAmount, 3);
            int64_t sent_xah = (slot_type(3, 1) == 1);

            slot(SBUF(sent_cur), 3);
            uint8_t sent_amt_buf[AMT_SIZE];
            slot(SBUF(sent_amt_buf), 3);

            uint8_t offer_id[HASH256_SIZE];
            otxn_param(SBUF(offer_id), "OID", 3);

            uint8_t offer_key[ACCID_SIZE + SEQ_SIZE];
            for (int i = 0; GUARD(ACCID_SIZE), i < ACCID_SIZE; ++i) {
                offer_key[i] = OTX_ACC[i];
            }
            for (int i = 0; GUARD(SEQ_SIZE), i < SEQ_SIZE; ++i) {
                offer_key[i + ACCID_SIZE] = seq[i];
            }
            uint8_t offer_hash[HASH256_SIZE];
            util_sha512h(SBUF(offer_hash), SBUF(offer_key));

            uint8_t offer_model[ACCID_SIZE + AMT_SIZE];
            for (int i = 0; GUARD(ACCID_SIZE), i < ACCID_SIZE; ++i) {
                offer_model[i] = OTX_ACC[i];
            }
            for (int i = 0; GUARD(AMT_SIZE), i < AMT_SIZE; ++i) {
                offer_model[i + ACCID_SIZE] = sent_amt_buf[i];
            }
            TRACEHEX(offer_model);

            state_foreign_set(SBUF(offer_hash), SBUF(offer_model), SBUF(offers_ns), SBUF(issuer_accid));
            state_foreign_set(SBUF(tid), SBUF(offer_hash), SBUF(sell_offers_ns), SBUF(issuer_accid));
            DONE("001-Broker: Offer Created.");
        }

        case 'R':
        {
            uint8_t oid[HASH256_SIZE];
            if (otxn_param(SBUF(oid), "OID", 3) == 32)
                NOPE("001-Broker: Missing `OID` parameter.");

            TRACEHEX(oid);
            state_foreign_set(SBUF(offer_hash), SBUF(offer_model), SBUF(offers_ns), SBUF(issuer_accid));
            state_foreign_set(SBUF(tid), SBUF(offer_hash), SBUF(sell_offers_ns), SBUF(issuer_accid));
            DONE("001-Broker: Offer Removed.");
        }

        case 'D':
        {
            // Distribute
            if (!BUFFER_EQUAL_20(HOOK_ACC, issuer_accid))
                NOPE("001-Broker: Issuer must distribute.");

            uint8_t acct_root_kl[34];
            LOAD_BALANCE(issuer_accid, acct_root_kl, 1, sfBalance);
            int64_t balance_xfl = RETURN_BALANCE_WITH_RESERVE();
            
            int64_t broker_fee_xfl;
            state_foreign(SVAR(broker_fee_xfl), "FEE", 3, SBUF(master_ns), SBUF(master_accid));
            int64_t broker_amt_xfl = float_multiply(balance_xfl, broker_fee_xfl);
            TRACEVAR(broker_amt_xfl);

            DONE("001-Broker: Offer Distributed.");
        }

        default:
        {
            NOPE("001-Broker: Unknown operation.");
        }
    }

    return 0;
}
```

Fix this. Balance is returned in a MACRO. We cant do that.


"""
response = client.prompt(prompt)
print(response)
