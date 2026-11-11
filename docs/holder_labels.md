# Holder labels — RWA Flow Tracker

Phase 2 deliverable. For each top holder (from `sql/04_top_holders.sql` /
`sql/08_where_activity_goes.sql`), record who it is and **where the label
came from**. If a label is a guess, mark it as a guess — rule 4 in
AGENTS.md.

Label categories: `exchange`, `issuer`, `custodian`, `fund`, `defi`,
`bridge`, `unknown`.

Sources to try, in order of effort:
1. **Etherscan** — address page often shows a name tag; free, no key needed
   for the website (API needs a key).
2. **Arkham** — free tier, good exchange/institution labels.
3. **Nansen** — free tier; labels are part of what the JD asks about, so
   prefer it where it has coverage and note "Nansen" as the source.
4. **Manual** — project docs, official announcements, on-chain role
   (e.g. the contract IS the token's own minter → label `issuer`).

| Asset | Address | Balance | Label | Source | Confidence | Notes |
|---|---|---|---|---|---|---|
| _fill from 04_top_holders output_ | | | | | | |

## Known addresses worth checking first

- BUIDL issuer/custody: Securitize-related wallets; check Arkham for
  "Securitize" labelled addresses.
- OUSG: Ondo's `OUSG_InstantManager` contract
  `0x93358db73B6cd4b98D89c8F5f230E81a95c2643a` and Coinbase Prime address
  `0xF67416a2C49f6A46FEe1c47681C5a3832cf8856c` (from docs.ondo.finance/addresses)
  are documented non-holder infrastructure — if they appear as "holders"
  in results, label them `issuer`/`custodian` with source "Ondo docs".
- USDC: known exchange wallets are well labelled on Etherscan/Arkham.

## Phase 2 upgrade

Once labels are filled, add a `labels` CTE to `sql/08_where_activity_goes.sql`
joining address → label and re-run to get inflow volume by category —
that table feeds the executive summary.
