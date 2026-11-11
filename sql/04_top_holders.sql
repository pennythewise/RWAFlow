-- =====================================================================
-- 04_top_holders.sql
-- Question: who holds the most of this token right now?
-- Tables used: balances_ethereum.latest, tokens.erc20 (VERIFY via 00_verify_tables.sql)
-- Written: 2026-11-11
--
-- balances_ethereum.latest holds the most recent NON-ZERO balance per
-- (address, token). For tokens with transfer restrictions (BUIDL, OUSG)
-- most supply sits in a few issuer/custodian wallets — that concentration
-- IS the finding. Export results and label them in docs/holder_labels.md
-- (Phase 2) with the label source (Nansen/Arkham/Etherscan/manual).
--
-- NOTE: `balance` is already in display units (decimals applied by Dune).
-- If the column is missing, compute balance_raw / 10^decimals using
-- decimals from tokens.erc20.
-- =====================================================================

WITH params AS (
    SELECT
        0x7712c34205737192402172409a8F7ccef8aA2AEc AS token_address  -- BUIDL
),

token_meta AS (
    SELECT symbol, name, decimals
    FROM tokens.erc20
    WHERE blockchain = 'ethereum'
      AND contract_address = (SELECT token_address FROM params)
),

top_holders AS (
    SELECT
        address,
        balance,
        balance_usd,
        updated_at
    FROM balances_ethereum.latest
    WHERE token_address = (SELECT token_address FROM params)
      AND token_standard = 'erc20'
    ORDER BY balance DESC
    LIMIT 20
)

SELECT
    t.address,
    t.balance,
    t.balance_usd,
    ROUND(100.0 * t.balance / SUM(t.balance) OVER (), 4) AS pct_of_top20,
    t.updated_at,
    m.symbol,
    m.name AS token_name,
    m.decimals
FROM top_holders t
CROSS JOIN token_meta m
ORDER BY t.balance DESC;
