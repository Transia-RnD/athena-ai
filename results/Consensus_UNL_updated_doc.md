- The UNL (Unique Node List) is managed by the ValidatorList class, which maintains trusted validator public keys, publisher lists, and the Negative UNL.
- The publisher list is handled by parsing published validator lists (see ValidatorList.cpp, e.g., parsing `jss::validators` and `jss::validation_public_key` fields).
- The RPC handler `doUnlList` (UnlList.cpp) exposes the current UNL and trusted status for each validator via the `unl` field in the JSON response.
- Nodes handle non-UNL participants by filtering validations: only validations from trusted (UNL) validators are counted for consensus. The ValidatorList class provides methods to retrieve the trusted master keys and to filter out validations from non-UNL or Negative UNL validators.
- If there are publisher lists or a local publisher list but the computed UNL size is zero, the node sets a "UNLBlocked" status, indicating it cannot participate in consensus.
- The Negative UNL is also managed in ValidatorList, and validations from Negative UNL validators are filtered out.
- Non-UNL participants (validators not on the UNL) are not counted for quorum or consensus, and their validations are ignored by default. Only trusted validators (on the UNL and not on the Negative UNL) are considered in consensus calculations.

References:
- ValidatorList.cpp (parsing publisher lists, trusted key management, filtering)
- UnlList.cpp (RPC handler for UNL)
- Negative UNL filtering in ValidatorList

All statements are strictly grounded in the provided source code and documentation.