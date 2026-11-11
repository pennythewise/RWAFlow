-- =====================================================================
-- 08_where_activity_goes.sql
-- Question: where does token activity flow — exchanges, DeFi, or plain
-- wallets? (Feeds Q4 and the executive summary's partner recommendations.)
-- Tables used: tokens.transfers, balances_ethereum.latest
--              (VERIFY via 00_verify_tables.sql)
-- Written: 2026-11-11
--
-- This query ranks the TOP RECIPIENT addresses by cumulative tokens
-- received — the first pass at "where does supply sit". The output feeds
-- docs/holder_labels.md: you label each address (exchange / issuer /
-- DeFi contract / unknown + source) in Phase 2, then re-run with a
-- labels CTE to get volume-by-category.
--
-- Phase 2 upgrade path: after labelling, join labels and produce
--   SUM(amount) GROUP BY label  →  "X% of inflow went to exchanges"
-- Keep this raw version — it is the evidence the labels are built on.
-- =====================================================================

WITH params AS (
    SELECT
        0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92 AS token_address,  -- OUSG
        DATE '2025-01-01' AS start_date
),

inflows AS (
    SELECT
        "to" AS address,
        SUM(amount) AS tokens_received,
        SUM(amount_usd) AS usd_received,
        COUNT(*) AS transfer_count,
        MAX(block_date) AS last_received
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND token_standard = 'erc20'
      AND contract_address = (SELECT token_address FROM params)
      AND block_date >= (SELECT start_date FROM params)
      AND "to" != 0x0000000000000000000000000000000000000000
    GROUP BY 1
),

current_balances AS (
    SELECT address, balance
    FROM balances_ethereum.latest
    WHERE token_address = (SELECT token_address FROM params)
      AND token_standard = 'erc20'
)

SELECT
    i.address,
    i.tokens_received,
    i.usd_received,
    i.transfer_count,
    i.last_received,
    COALESCE(b.balance, 0) AS current_balance,
    ROUND(100.0 * i.tokens_received / SUM(i.tokens_received) OVER (), 2) AS pct_of_inflow
FROM inflows i
LEFT JOIN current_balances b ON b.address = i.address
ORDER BY i.tokens_received DESC
LIMIT 50;
