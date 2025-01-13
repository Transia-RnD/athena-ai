#!/usr/bin/env python
# coding: utf-8

from athenah_ai.indexer import AthenahIndexer

# path: str = "/Users/darkmatter/projects/ledger-works/app-xah"
# indexer = AthenahIndexer("local", "id", "dist", "app-xah", "v1")
# indexer.index_whitelist(
#     path,
#     ["src/xah"],
#     "app-xah",
# )

from athenah_ai.client import AthenahClient

prompt: str = """
I want to create a function that takes in parameters and then encodes them. The context repo you have is what decodes them. The xah_parse.c file does this. It does it from a hex encoded string. Like 1200... 

What I need to build is sort of the opposite. I will have a c smart contract, and only variables. I will need to encode them into different transactions. I'm thinking of doing it like prepare(transactionType, etc, etc, etc) but each transaction type will have different parameters.

Return the entire file with all the functions required to achomplish the task.

Because its a hook I need to create 2 files a header and a c file or it wont work.

```
/*******************************************************************************
 *   XAH Wallet
 *   (c) 2020 Towo Labs
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 ********************************************************************************/

#ifndef LEDGER_APP_XAH_FIELDS_H
#define LEDGER_APP_XAH_FIELDS_H

#include <stdint.h>
#include <stdbool.h>

#include "limitations.h"

typedef enum {
    // Normal field types
    STI_UINT16 = 0x01,
    STI_UINT32 = 0x02,
    STI_HASH128 = 0x04,
    STI_HASH256 = 0x05,
    STI_AMOUNT = 0x06,
    STI_VL = 0x07,
    STI_ACCOUNT = 0x08,
    STI_OBJECT = 0x0E,
    STI_ARRAY = 0x0F,
    STI_UINT8 = 0x10,
    STI_PATHSET = 0x12,
    STI_VECTOR256 = 0x13,

    // Custom field types
    STI_CURRENCY = 0xF0,
} field_type_t;

// Small collection of used field IDs
// UINT8
#define XAH_UINT8_TICK_SIZE 0x10
// UINT16
#define XAH_UINT16_TRANSACTION_TYPE 0x02
#define XAH_UINT16_SIGNER_WEIGHT    0x03
#define XAH_UINT16_TRANSFER_FEE     0x04
#define XAH_UINT16_HOOK_API_VERSION 0x14
// UINT32
#define XAH_UINT32_NETWORK_ID            0x01
#define XAH_UINT32_FLAGS                 0x02
#define XAH_UINT32_SOURCE_TAG            0x03
#define XAH_UINT32_SEQUENCE              0x04
#define XAH_UINT32_EXPIRATION            0x0A
#define XAH_UINT32_TRANSFER_RATE         0x0B
#define XAH_UINT32_WALLET_SIZE           0x0C
#define XAH_UINT32_DESTINATION_TAG       0x0E
#define XAH_UINT32_QUALITY_IN            0x14
#define XAH_UINT32_QUALITY_OUT           0x15
#define XAH_UINT32_OFFER_SEQUENCE        0x19
#define XAH_UINT32_FIRST_LEDGER_SEQUENCE 0x1A
#define XAH_UINT32_LAST_LEDGER_SEQUENCE  0x1B
#define XAH_UINT32_OPERATION_LIMIT       0x1D
#define XAH_UINT32_SET_FLAG              0x21
#define XAH_UINT32_CLEAR_FLAG            0x22
#define XAH_UINT32_SIGNER_QUORUM         0x23
#define XAH_UINT32_CANCEL_AFTER          0x24
#define XAH_UINT32_FINISH_AFTER          0x25
#define XAH_UINT32_SETTLE_DELAY          0x27
#define XAH_UINT32_TICKET_COUNT          0x28
#define XAH_UINT32_TICKET_SEQUENCE       0x29
#define XAH_UINT32_NFTOKEN_TAXON         0x2A
// HASH128
#define XAH_HASH128_EMAIL_HASH 0x01
// HASH256
#define XAH_HASH256_PREVIOUS_TXN_ID    0x05
#define XAH_HASH256_WALLET_LOCATOR     0x07
#define XAH_HASH256_ACCOUNT_TXN_ID     0x09
#define XAH_HASH256_NFTOKEN_ID         0x0A
#define XAH_HASH256_INVOICE_ID         0x11
#define XAH_HASH256_NICKNAME           0x12
#define XAH_HASH256_HOOK_ON            0x14
#define XAH_HASH256_DIGEST             0x15
#define XAH_HASH256_CHANNEL            0x16
#define XAH_HASH256_CHECK_ID           0x18
#define XAH_HASH256_NFTOKEN_BUY_OFFER  0x1C
#define XAH_HASH256_NFTOKEN_SELL_OFFER 0x1D
#define XAH_HASH256_HOOK_HASH          0x1F
#define XAH_HASH256_HOOK_NAMESPACE     0x20
#define XAH_HASH256_OFFER_ID           0x22
#define XAH_HASH256_ESCROW_ID          0x23
#define XAH_HASH256_URITOKEN_ID        0x24
#define XAH_HASH256_GOVERNANCE_MARKS   0x62
#define XAH_HASH256_GOVERNANCE_FLAGS   0x63
// AMOUNT
#define XAH_UINT64_AMOUNT             0x01
#define XAH_UINT64_BALANCE            0x02
#define XAH_UINT64_LIMIT_AMOUNT       0x03
#define XAH_UINT64_TAKER_PAYS         0x04
#define XAH_UINT64_TAKER_GETS         0x05
#define XAH_UINT64_FEE                0x08
#define XAH_UINT64_SEND_MAX           0x09
#define XAH_UINT64_DELIVER_MIN        0x0A
#define XAH_UINT64_NFTOKEN_BROKER_FEE 0x13
// BLOB
#define XAH_VL_PUBLIC_KEY           0x01
#define XAH_VL_MESSAGE_KEY          0x02
#define XAH_VL_SIGNING_PUB_KEY      0x03
#define XAH_VL_TXN_SIGNATURE        0x04
#define XAH_VL_URI                  0x05
#define XAH_VL_SIGNATURE            0x06
#define XAH_VL_DOMAIN               0x07
#define XAH_VL_CREATE_CODE          0x0B
#define XAH_VL_MEMO_TYPE            0x0C
#define XAH_VL_MEMO_DATA            0x0D
#define XAH_VL_MEMO_FORMAT          0x0E
#define XAH_VL_FULFILLMENT          0x10
#define XAH_VL_CONDITION            0x11
#define XAH_VL_HOOK_PARAMETER_NAME  0x18
#define XAH_VL_HOOK_PARAMETER_VALUE 0x19
#define XAH_VL_BLOB                 0x1A
// VECTOR256
#define XAH_VECTOR256_NFTOKEN_OFFERS 0x04
#define XAH_VECTOR256_URITOKEN_IDS   0x63
// ACCOUNTID
#define XAH_ACCOUNT_ACCOUNT        0x01
#define XAH_ACCOUNT_OWNER          0x02
#define XAH_ACCOUNT_DESTINATION    0x03
#define XAH_ACCOUNT_ISSUER         0x04
#define XAH_ACCOUNT_AUTHORIZE      0x05
#define XAH_ACCOUNT_UNAUTHORIZE    0x06
#define XAH_ACCOUNT_REGULAR_KEY    0x08
#define XAH_ACCOUNT_NFTOKEN_MINTER 0x09
#define XAH_ACCOUNT_INFORM         0x63
// STOBJECT
#define XAH_STOBJECT_MEMO           0x0A
#define XAH_STOBJECT_SIGNER_ENTRY   0x0B
#define XAH_STOBJECT_NFTOKEN        0x0C
#define XAH_STOBJECT_HOOK           0x0E
#define XAH_STOBJECT_SIGNER         0x10
#define XAH_STOBJECT_HOOK_PARAMETER 0x17
#define XAH_STOBJECT_HOOK_GRANT     0x18
#define XAH_STOBJECT_AMOUNT         0x5B
#define XAH_STOBJECT_MINT_URITOKEN  0x5C
// STARRAY
#define XAH_STARRAY_SIGNERS         0x03
#define XAH_STARRAY_SIGNER_ENTRIES  0x04
#define XAH_STARRAY_MEMOS           0x09
#define XAH_STARRAY_NFTOKENS        0x0A
#define XAH_STARRAY_HOOKS           0x0B
#define XAH_STARRAY_HOOK_PARAMETERS 0x13
#define XAH_STARRAY_HOOK_GRANTS     0x14
#define XAH_STARRAY_AMOUNTS         0x5C

#define XAH_CURRENCY_CURRENCY 0x01

// Array of type one is reserved for end-of-array marker so this
// constant cannot possibly collide with anything in the future
#define ARRAY_PATHSET 0x01
#define ARRAY_NONE    0x00

#define PATHSET_NEXT 0xFF
#define PATHSET_END  0x00

#define XAH_ACCOUNT_SIZE   20
#define XAH_CURRENCY_SIZE  20
#define XAH_VECTOR256_SIZE 32

typedef struct {
    uint8_t buf[XAH_ACCOUNT_SIZE];
} xah_account_t;

typedef struct {
    uint8_t buf[XAH_CURRENCY_SIZE];
} xah_currency_t;

typedef struct {
    uint8_t type;
    uint8_t index1;
    uint8_t index2;
} array_info_t;

typedef struct {
    uint8_t buf[16];
} hash128_t;

typedef struct {
    uint8_t buf[32];
} hash256_t;

typedef struct {
    uint8_t id;
    field_type_t data_type;
    uint16_t length;
    union {
        uint8_t u8;
        uint16_t u16;
        uint32_t u32;
        hash128_t *hash128;
        hash256_t *hash256;
        xah_account_t *account;
        xah_currency_t *currency;
        uint8_t *ptr;
    } data;
    array_info_t array_info;
} field_t;

typedef struct {
    char buf[MAX_FIELDNAME_LEN];
} field_name_t;

typedef struct {
    char buf[MAX_FIELD_LEN];
} field_value_t;

bool is_normal_account_field(field_t *field);
const char *resolve_field_name(field_t *field);
bool is_field_hidden(field_t *field);

#endif  // LEDGER_APP_XAH_FIELDS_H

```

```
/*******************************************************************************
 *   XAH Wallet
 *   (c) 2020 Towo Labs
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 ********************************************************************************/

#include <string.h>

#include "fields.h"
#include "flags.h"
#include "common.h"

#define HIDE(t, i) \
    if (field->data_type == (t) && field->id == (i) && field->array_info.type == 0) return true

bool is_normal_account_field(field_t *field) {
    return field->data_type == STI_ACCOUNT && field->id == XAH_ACCOUNT_ACCOUNT &&
           field->array_info.type == 0;
}

const char *resolve_field_name(field_t *field) {
    if (field->data_type == STI_UINT16) {
        switch (field->id) {
            case 2:
                return "Transaction Type";
            case 3:
                return "Signer Weight";
            case 4:
                return "Transfer Fee";
            case 20:
                return "Hook Api Version";
        }
    }

    if (field->data_type == STI_UINT32) {
        switch (field->id) {
            // 32-bit integers
            case 1:
                return "Network ID";
            case 2:
                return "Flags";
            case 3:
                return "Source Tag";
            case 4:
                return "Sequence";
            case 10:
                return "Expiration";
            case 11:
                return "Transfer Rate";
            case 12:
                return "Wallet Size";
            case 14:
                return "Destination Tag";
            case 20:
                return "Quality In";
            case 21:
                return "Quality Out";
            case 25:
                return "Offer Sequence";
            case 26:
                return "First Ledger Sequence";
            case 27:
                return "Last Ledger Sequence";
            case 29:
                return "Operation Limit";
            case 33:
                return "Set Flag";
            case 34:
                return "Clear Flag";
            case 35:
                return "Signer Quorum";
            case 36:
                return "Cancel After";
            case 37:
                return "Finish After";
            case 39:
                return "Settle Delay";
            case 40:
                return "Ticket Count";
            case 41:
                return "Ticket Sequence";
            case 42:
                return "NFToken Taxon";
        }
    }

    if (field->data_type == STI_HASH128) {
        switch (field->id) {
            case 1:
                return "Email Hash";
        }
    }

    if (field->data_type == STI_HASH256) {
        switch (field->id) {
            // 256-bit
            case 5:
                return "Previous Txn ID";
            case 7:
                return "Wallet Locator";
            case 9:
                return "Account Txn ID";
            case 10:
                return "NFToken ID";
            case 17:
                return "Invoice ID";
            case 18:
                return "Nickname";
            case 20:
                return "Hook On";
            case 21:
                return "Digest";
            case 22:
                return "Channel";
            case 24:
                return "Check ID";
            case 28:
                return "NFToken Buy Offer";
            case 29:
                return "NFToken Sell Offer";
            case 31:
                return "Hook Hash";
            case 32:
                return "Hook Namespace";
            case 34:
                return "Offer ID";
            case 35:
                return "Escrow ID";
            case 36:
                return "URIToken ID";
            case 98:
                return "Governance Marks";
            case 99:
                return "Governance Flags";
        }
    }

    if (field->data_type == STI_AMOUNT) {
        switch (field->id) {
            // currency amount
            case 1:
                return "Amount";
            case 2:
                return "Balance";
            case 3:
                return "Limit Amount";
            case 4:
                return "Taker Pays";
            case 5:
                return "Taker Gets";
            case 8:
                return "Fee";
            case 9:
                return "Send Max";
            case 10:
                return "Deliver Min";
            case 19:
                return "NFToken Broker Fee";
        }
    }

    if (field->data_type == STI_VL) {
        switch (field->id) {
            // variable length (common)
            case 1:
                return "Public Key";
            case 2:
                return "Message Key";
            case 3:
                return "Sig.PubKey";
            case 4:
                return "Txn Sig.";
            case 5:
                return "URI";
            case 6:
                return "Signature";
            case 7:
                return "Domain";
            case 11:
                return "Create Code";
            case 12:
                return "Memo Type";
            case 13:
                return "Memo Data";
            case 14:
                return "Memo Fmt";
            case 16:
                return "Fulfillment";
            case 17:
                return "Condition";
            case 24:
                return "Hook Param Name";
            case 25:
                return "Hook Param Value";
            case 26:
                return "Blob";
        }
    }

    if (field->data_type == STI_VECTOR256) {
        switch (field->id) {
            // vector 256
            case 5:
                return "Hook Namespaces";
            case 99:
                return "URIToken IDs";
        }
    }

    if (field->data_type == STI_ACCOUNT) {
        switch (field->id) {
            case 1:
                return "Account";
            case 2:
                return "Owner";
            case 3:
                return "Destination";
            case 4:
                return "Issuer";
            case 5:
                return "Authorize";
            case 6:
                return "Unauthorize";
            case 8:
                return "Regular Key";
            case 9:
                return "NFToken Minter";
            case 99:
                return "Inform";
        }
    }

    if (field->data_type == STI_OBJECT) {
        switch (field->id) {
            // inner object
            case 10:
                return "Memo";
            case 11:
                return "Signer Entry";
            case 12:
                return "NFToken";
            case 14:
                return "Hook";
            case 16:
                return "Signer";
            case 23:
                return "Hook Parameter";
            case 24:
                return "Hook Grant";
            case 91:
                return "Amount Entry";
            case 92:
                return "Mint URIToken";
        }
    }

    if (field->data_type == STI_ARRAY) {
        switch (field->id) {
            // array of objects
            case 3:
                return "Signers";
            case 4:
                return "Signer Entries";
            case 9:
                return "Memos";
            case 10:
                return "NFTokens";
            case 11:
                return "Hooks";
            case 19:
                return "Hook Parameters";
            case 20:
                return "Hook Grants";
            case 92:
                return "Amounts";
        }
    }

    if (field->data_type == STI_UINT8) {
        switch (field->id) {
            // 8-bit integers
            case 16:
                return "Tick Size";
        }
    }

    if (field->data_type == STI_PATHSET) {
        switch (field->id) {
            case 1:
                return "Paths";
        }
    }

    if (field->data_type == STI_CURRENCY) {
        switch (field->id) {
            case 1:
                return "Currency";
        }
    }

    // Default case
    return "Unknown";
}

bool is_field_hidden(field_t *field) {
    HIDE(STI_UINT32, XAH_UINT32_SEQUENCE);
    HIDE(STI_UINT32, XAH_UINT32_LAST_LEDGER_SEQUENCE);
    HIDE(STI_VL, XAH_VL_SIGNING_PUB_KEY);

    if (field->data_type == STI_ARRAY || field->data_type == STI_OBJECT ||
        field->data_type == STI_PATHSET) {
        // Field is only used to instruct parsing code how to handle following fields: don't show
        return true;
    }

    if (is_flag_hidden(field)) {
        return true;
    }

    return false;
}

```

Requirements:

- You must return code.
"""
client = AthenahClient("id", "dist", "app-xah")
response = client.promptv1(prompt)
print(response)
