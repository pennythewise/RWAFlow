-- =====================================================================
-- 05_holder_count.sql
-- Question: is the holder base growing or shrinking over time?
-- Tables used: tokens.transfers (VERIFY via 00_verify_tables.sql)
-- Written: 2026-11-11
--
-- APPROXIMATION: this counts DISTINCT addresses seen in transfers per
-- day/week — a wallet that only receives and never sends still counts
-- once it appears. It is NOT the same as balance-table holder counts.
-- For exact holder counts use balances_ethereum.daily_updates if it is
-- queryable within your Dune compute limits (it is large — try weekly
-- grain first, and prefer running it only for the RWA tokens, not USDC).
--
-- COST WARNING: for USDC this scans a very large table. Keep the date
-- range tight (e.g. last 90 days) or run per-asset only for BUIDL/OUSG.
-- =====================================================================

WITH params AS (
    SELECT
        0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92 AS token_address,  -- OUSG
        DATE '2025-01-01' AS start_date,
        DATE '2026-11-11' AS end_date
),

participants AS (
    SELECT DISTINCT block_date, "from" AS address
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND token_standard = 'erc20'
      AND contract_address = (SELECT token_address FROM params)
      AND block_date BETWEEN (SELECT start_date FROM params) AND (SELECT end_date FROM params)
      AND "from" != 0x0000000000000000000000000000000000000000

    UNION

    SELECT DISTINCT block_date, "to" AS address
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND token_standard = 'erc20'
      AND contract_address = (SELECT token_address FROM params)
      AND block_date BETWEEN (SELECT start_date FROM params) AND (SELECT end_date FROM params)
      AND "to" != 0x0000000000000000000000000000000000000000
)

SELECT
    DATE_TRUNC('week', block_date) AS week,
    COUNT(DISTINCT address) AS active_addresses_that_week
FROM participants
GROUP BY 1
ORDER BY 1;
