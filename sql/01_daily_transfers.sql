-- =====================================================================
-- 01_daily_transfers.sql
-- Question: how much transfer activity do these tokens see per day?
-- Tables used: tokens.transfers (VERIFY name/columns via 00_verify_tables.sql)
-- Written: 2026-11-11
--
-- HOW TO USE: change token_address in the params CTE below to the asset
-- you want (addresses in docs/scope.md), save as a separate Dune query per
-- asset, then add all of them as dashboard visualisations.
-- =====================================================================

WITH params AS (
    SELECT
        0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 AS token_address,  -- USDC
        DATE '2024-01-01' AS start_date
),

transfers AS (
    SELECT
        block_date,
        COUNT(*) AS transfer_count,
        COUNT(DISTINCT "from") AS unique_senders,
        COUNT(DISTINCT "to") AS unique_receivers,
        SUM(amount) AS tokens_moved,
        SUM(amount_usd) AS volume_usd
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND token_standard = 'erc20'
      AND contract_address = (SELECT token_address FROM params)
      AND block_date >= (SELECT start_date FROM params)
    GROUP BY 1
)

SELECT *
FROM transfers
ORDER BY block_date;
