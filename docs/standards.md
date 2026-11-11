# Standards notes — plain words for interviews

This page explains the token/address standards this project relies on.
Write it in your own words if asked; the goal is that you can *defend*
each concept, not recite it.

## ERC-20 tokens and Transfer events

Every ERC-20 token is a smart contract that emits a standard `Transfer`
event whenever tokens move:

```
Transfer(address indexed from, address indexed to, uint256 value)
```

This single event type is why one query pattern works across USDC, BUIDL,
OUSG and USDY: Dune's `tokens.transfers` table is decoded from exactly
these logs. A "mint" is a Transfer **from** the zero address
`0x0000...0000`; a "burn" is a Transfer **to** it.

Two quirks that matter for this project:

- **Rebasing tokens (BUIDL).** Some tokens grow every holder's balance
  continuously to reflect accrued yield, without any Transfer event. On
  Dune the balances move but the transfer table shows nothing — so
  "supply from mints minus burns" will drift below `totalSupply()`. We
  document the delta instead of hiding it.
- **Permissioned tokens (BUIDL, OUSG).** Transfers can be restricted to
  whitelisted addresses (compliance/KYC at the contract level). Fewer
  wallets, less organic churn — interpret holder metrics accordingly.

## ERC-4626 vaults

ERC-4626 is the standard for tokenized vaults: you deposit an asset
(e.g. USDC) and receive *shares* representing your claim. Share price
appreciates as the vault earns yield. Relevant because several RWA
tokens are structured as or alongside 4626-style vaults — if a token's
issuance shows `Deposit`/`Withdraw` events rather than plain `Transfer`
mints, the mint/burn queries need to read those events too. Check
`docs.ondo.finance` / contract docs per token before assuming.

## Checksummed addresses (EIP-55)

Ethereum addresses are 40 hex characters. EIP-55 "checksums" them by
casing letters based on a hash of the address — a single flipped
character produces a *different-looking but valid-format* address, and a
lowercased-then-remixed address may be invalid. Rules we follow:

- Always store and compare addresses in the checksummed form from
  official sources (see `docs/scope.md`).
- When querying case-insensitive systems (BigQuery stores lowercase),
  lowercase deliberately — never "fix" casing by hand.
- `0x` + 40 hex = address; all-zero address = mint/burn sentinel.

## Address labels and metadata

An address is just a number — "Binance hot wallet" or any exchange label
is off-chain
knowledge attached by explorers/indexers. This project treats labels as
**data with provenance**: every label in `docs/holder_labels.md` records
its source (Nansen, Arkham, Etherscan, manual, or "guess"). On-chain you
can also read a contract's `name()`/`symbol()`/`decimals()` (ERC-20
metadata) — Dune exposes these in `tokens.erc20` — which tells you what
a token *is*, not who holds it.

## Where each concept shows up in the repo

| Concept | Where |
|---|---|
| Transfer events, mint/burn | `sql/01`–`sql/03` |
| Balances / holder counts | `sql/04`–`sql/07` via `balances_ethereum.latest` |
| Labels with sources | `docs/holder_labels.md` |
| Rebasing caveat | `docs/scope.md`, `sql/02`–`sql/03` headers |
| BigQuery lowercase addresses | `notebooks/bigquery_run.ipynb` |
