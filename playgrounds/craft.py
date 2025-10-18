#!/usr/bin/env python
# coding: utf-8

AGENT_MODEL = "claude-4-sonnet-20250514"
ATHENAH_CLIENT_NAME: str = "craft"


def main():
    # from athenah_ai.indexer import AthenahIndexer

    # path: str = "/Users/darkmatter/projects/ledger-works/craft"
    # indexer = AthenahIndexer("local", "id", "dist", "craft", "v1")
    # indexer.build_from_dirs(path, ["docs", "projects", "xrpl-std"], True, True)

    from athenah_ai.client import AthenahClient

    ai_source: AthenahClient = AthenahClient(
        "id",
        # provider="anthropic",
        provider="openai",
        # provider="xai",
        model_group="dist",
        custom_model=ATHENAH_CLIENT_NAME,
        version="v1",
        # model_name="claude-4-sonnet-20250514",
        model_name="gpt-4.1",
        # model_name="grok-4",
        temperature=0,
        best_of=3,
    )
    system_prompt: str = """
#![cfg_attr(target_arch = "wasm32", no_std)]

#[cfg(not(target_arch = "wasm32"))]
extern crate std;

#[cfg(target_arch = "wasm32")]
extern crate alloc;

#[cfg(target_arch = "wasm32")]
use alloc::vec::Vec;

#[cfg(not(target_arch = "wasm32"))]
use std::vec::Vec;

use crate::host::{Result::Err, Result::Ok};
use xrpl_std::core::constants::{ACCOUNT_ONE, ACCOUNT_ZERO};
use xrpl_std::core::current_tx::escrow_finish::{EscrowFinish, get_current_escrow_finish};
use xrpl_std::core::current_tx::traits::{EscrowFinishFields, TransactionCommonFields};
use xrpl_std::core::ledger_objects::current_escrow::{CurrentEscrow, get_current_escrow};
use xrpl_std::core::ledger_objects::traits::{
    CurrentEscrowFields, CurrentLedgerObjectCommonFields,
};
use xrpl_std::core::locator::Locator;
use xrpl_std::core::types::account_id::AccountID;
use xrpl_std::core::types::blob::Blob;
use xrpl_std::core::types::hash_256::Hash256;
use xrpl_std::core::types::public_key::PublicKey;
use xrpl_std::core::types::amount::token_amount::TokenAmount;
use xrpl_std::core::types::transaction_type::TransactionType;
use xrpl_std::host;
use xrpl_std::host::trace::{DataRepr, trace, trace_amount, trace_data, trace_num};
use xrpl_std::sfield;
use xrpl_std::core::field_codes::{
    SF_ACCOUNT, SF_ACCOUNT_TXN_ID, SF_CONDITION, SF_FEE, SF_FLAGS, SF_FULFILLMENT, SF_HASH,
    SF_LAST_LEDGER_SEQUENCE, SF_NETWORK_ID, SF_OFFER_SEQUENCE, SF_OWNER, SF_SEQUENCE,
    SF_SIGNING_PUB_KEY, SF_SOURCE_TAG, SF_TICKET_SEQUENCE, SF_TRANSACTION_TYPE, SF_TXN_SIGNATURE,
};

pub const SF_AMOUNT: i32 = 327680; // 0x50000
pub const SF_DESTINATION: i32 = 327681; // 0x50001

pub struct CommonFields {
    pub transaction_type: u16, // e.g., 0 for Payment
    // pub flags: Option<u32>,
    // pub source_tag: Option<u32>,
    pub account: AccountID,
    pub sequence: u32,
    // pub previous_txn_id: Option<Hash256>,
    // pub last_ledger_sequence: Option<u32>,
    // pub account_txn_id: Option<Hash256>,
    // pub fee: TokenAmount,
    // pub operation_limit: Option<u32>,
    // pub memos: Option<Vec<Memo>>, // Add as needed
    pub signing_pub_key: PublicKey,
    // pub ticket_sequence: Option<u32>,
    // pub txn_signature: Option<Signature>, // Add as needed
    // pub signers: Option<Vec<Signer>>, // Add as needed
    // pub network_id: Option<u32>,
    // pub delegate: Option<Delegate>, // Add as needed
}

pub struct PaymentFields {
    pub destination: AccountID,
    // pub amount: TokenAmount,
    // pub send_max: Option<Amount>,
    // pub paths: Option<Paths>, // Add as needed
    // pub invoice_id: Option<Hash256>,
    // pub destination_tag: Option<u32>,
    // pub deliver_min: Option<Amount>,
    // pub credential_ids: Option<Vec<Hash256>>, // Add as needed
    // pub domain_id: Option<u32>, // Add as needed
}

pub struct PaymentTxn {
    pub common: CommonFields,
    pub payment: PaymentFields,
}

impl PaymentTxn {
    pub fn serialize(&self, buf: &mut Vec<u8>) {
        // Serialize common fields
        serialize_u16_field(SF_TRANSACTION_TYPE, self.common.transaction_type, buf);
        // if let Some(flags) = self.common.flags {
        //     serialize_u32_field(SF_FLAGS, flags, buf);
        // }
        // if let Some(source_tag) = self.common.source_tag {
        //     serialize_u32_field(SF_SOURCE_TAG, source_tag, buf);
        // }
        // serialize_account_field(SF_ACCOUNT, &self.common.account, buf);
        // serialize_u32_field(SF_SEQUENCE, self.common.sequence, buf);
        // if let Some(prev) = &self.common.previous_txn_id {
        //     serialize_hash256_field(SF_PREVIOUS_TXN_ID, prev, buf);
        // }
        // if let Some(last_ledger_seq) = self.common.last_ledger_sequence {
        //     serialize_u32_field(SF_LAST_LEDGER_SEQUENCE, last_ledger_seq, buf);
        // }
        // if let Some(account_txn_id) = &self.common.account_txn_id {
        //     serialize_hash256_field(SF_ACCOUNT_TXN_ID, account_txn_id, buf);
        // }
        // serialize_amount_field(SF_FEE, &self.common.fee, buf);
        // if let Some(op_limit) = self.common.operation_limit {
        //     serialize_u32_field(SF_OPERATION_LIMIT, op_limit, buf);
        // }
        serialize_pubkey_field(SF_SIGNING_PUB_KEY, &self.common.signing_pub_key, buf);
        // if let Some(ticket_seq) = self.common.ticket_sequence {
        //     serialize_u32_field(SF_TICKET_SEQUENCE, ticket_seq, buf);
        // }
        // if let Some(network_id) = self.common.network_id {
        //     serialize_u32_field(SF_NETWORK_ID, network_id, buf);
        // }
        // Serialize payment fields
        serialize_account_field(SF_DESTINATION, &self.payment.destination, buf);
        // serialize_amount_field(SF_AMOUNT, &self.payment.amount, buf);
        // if let Some(send_max) = &self.payment.send_max {
        //     serialize_amount_field(SF_SEND_MAX, send_max, buf);
        // }
        // if let Some(invoice_id) = &self.payment.invoice_id {
        //     serialize_hash256_field(SF_INVOICE_ID, invoice_id, buf);
        // }
        // if let Some(dest_tag) = self.payment.destination_tag {
        //     serialize_u32_field(SF_DESTINATION_TAG, dest_tag, buf);
        // }
        // if let Some(deliver_min) = &self.payment.deliver_min {
        //     serialize_amount_field(SF_DELIVER_MIN, deliver_min, buf);
        // }
        // Add more as needed
    }
}

// Helper serialization functions (simplified, you may need to adjust for XRPL serialization rules)
fn serialize_u16_field(field_code: i32, value: u16, buf: &mut Vec<u8>) {
    buf.extend_from_slice(&field_code.to_be_bytes());
    buf.extend_from_slice(&value.to_be_bytes());
}
fn serialize_u32_field(field_code: i32, value: u32, buf: &mut Vec<u8>) {
    buf.extend_from_slice(&field_code.to_be_bytes());
    buf.extend_from_slice(&value.to_be_bytes());
}
fn serialize_account_field(field_code: i32, value: &AccountID, buf: &mut Vec<u8>) {
    buf.extend_from_slice(&field_code.to_be_bytes());
    buf.extend_from_slice(&value.0);
}
fn serialize_hash256_field(field_code: i32, value: &Hash256, buf: &mut Vec<u8>) {
    buf.extend_from_slice(&field_code.to_be_bytes());
    buf.extend_from_slice(&value.0);
}
// fn serialize_amount_field(field_code: i32, value: &TokenAmount, buf: &mut Vec<u8>) {
//     buf.extend_from_slice(&field_code.to_be_bytes());
//     buf.extend_from_slice(&value.0);
// }
fn serialize_pubkey_field(field_code: i32, value: &PublicKey, buf: &mut Vec<u8>) {
    buf.extend_from_slice(&field_code.to_be_bytes());
    buf.extend_from_slice(&value.0);
}

#[unsafe(no_mangle)]
pub extern "C" fn finish() -> bool {
    let _ = trace("$$$$$ STARTING WASM EXECUTION $$$$$");
    let _ = trace("");

    // The transaction prompting execution of this contract.
    const PUBKEY_SECP256K1: [u8; 33] = [
        0x02, 0xC7, 0x38, 0x7F, 0xFC, 0x25, 0xC1, 0x56, 0xCA, 0x7F, 0x8A, 0x6D, 0x76, 0x0C, 0x8D,
        0x01, 0xEF, 0x64, 0x2C, 0xEE, 0x9C, 0xE4, 0x68, 0x0C, 0x33, 0xFF, 0xB3, 0xFF, 0x39, 0xAF,
        0xEC, 0xFE, 0x70,
    ];
    let pubkey = PublicKey::from(PUBKEY_SECP256K1);
    let _ = trace_data("  SigningPubKey:", &pubkey.0, DataRepr::AsHex);

    // Example AccountID and Amount (replace with real values)
    let account = AccountID([0u8; 20]);
    let destination = AccountID([1u8; 20]);
    const BUFFER_SIZE: usize = 48usize;
    let mut buffer = [0u8; BUFFER_SIZE];
    let fee = TokenAmount::from(buffer);
    let amount = TokenAmount::from(buffer);

    let common = CommonFields {
        transaction_type: 0, // Payment
        account,
        sequence: 1,
        // fee,
        signing_pub_key: pubkey,
        // ..Default::default()
    };
    let payment = PaymentFields {
        destination,
        // amount,
        // ..Default::default()
    };
    let txn = PaymentTxn { common, payment };

    // let mut buf = Vec::new();
    // txn.serialize(&mut buf);

    // // Trace log the serialized transaction
    // trace_data("Serialized PaymentTxn:", &buf, DataRepr::AsHex);
    true // <-- Finish the escrow.
}

"""
    user_input: str = """
error: no global memory allocator found but one is required; link to std or add `#[global_allocator]` to a static item that implements the GlobalAlloc trait

- Fix this error. What is asking for the global memory allocator?
"""
    system_prompt = system_prompt + "\n" + user_input
    response = ai_source.agent_prompt("Developer", "Developer Coder", system_prompt)
    # write to a file
    with open("response.txt", "w") as f:
        f.write(response)


main()
