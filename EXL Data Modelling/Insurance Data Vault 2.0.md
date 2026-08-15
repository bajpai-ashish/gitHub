# Insurance Canonical Model to Data Vault 2.0

Source: `Canonical Data Model for Insurance Inbound Files.mmd` and `Canonical Model — High-Level Diagram.mmd`.

The accompanying Mermaid diagram is a logical Raw Vault. Use a deterministic 256-bit hash of the normalised business key(s) for every `*_hk`; links are hashed from their participating hub keys. Each table must also have `load_dts` and `record_source`; every satellite must include `hashdiff` and preserve history by `(parent_hk, load_dts)`.

## Hubs

| Hub | Business key from source |
|---|---|
| `H_PARTY` | `party_id` |
| `H_POLICY` | `policy_id` |
| `H_PRODUCT` | `product_id` |
| `H_COVERAGE` | coverage code/identifier (required from inbound contract) |
| `H_RISK_ITEM` | risk-object identifier (required from inbound contract) |
| `H_BILLING_ACCOUNT`, `H_INVOICE`, `H_PAYMENT`, `H_COMMISSION` | respective operational identifiers |
| `H_CLAIM`, `H_CLAIM_INCIDENT` | claim and incident identifiers |
| `H_REINSURANCE_CONTRACT`, `H_REINSURANCE_STATEMENT`, `H_REINSURANCE_SETTLEMENT` | respective reinsurance identifiers |

## Key modelling choices

- `Policy_Version` is a policy satellite, not a hub: it is a descriptive, effective-dated state of a policy. Its natural grain is `(policy_hk, version_no)`.
- `Party_Role`, `Policy_Party`, and `Claim_Party` are represented by role links plus effectivity satellites. This records a party's role without copying party attributes.
- `Policy_Coverage` and `Policy_Risk_Item` are links; their changing coverage/risk details belong to their respective satellites.
- Premium, premium schedule, claim transactions, claim coverage, and cession are satellites in the logical model because the supplied schema does not give them stable operational identifiers. Promote any of them to a hub when its inbound source supplies an independently managed identifier.
- Party-to-party relationships use `L_PARTY_RELATIONSHIP` with two role-qualified party keys. Its relationship type and effective dates belong in `S_PARTY_RELATIONSHIP`.

## Source-data requirements to finalise the physical model

The source schema explicitly gives only `party_id`, `policy_id`, `product_id`, and policy version number. Confirm the business keys for coverage, risk item, billing account, invoice, payment, commission, claim incident, and reinsurance records. If a source has no identifier, define an immutable composite key—for example, policy number plus source risk-object number—and record that choice in the ingestion mapping.

Reference code sets such as policy status, line of business, role type, and transaction type should remain reference data in Raw Vault satellites. They can become reference tables in the Business Vault if governed centrally.
