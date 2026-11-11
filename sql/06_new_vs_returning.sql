-- =====================================================================
-- 06_new_vs_returning.sql
-- Question: are holders sticky or churning — how many wallets are new
-- each week vs returning?
-- Tables used: tokens.transfers (VERIFY via 00_verify_tables.sql)
-- Written: 2026-11-11
--
-- A wallet is "new" in a week if its FIRST-EVER transfer for this token
-- happens that week; otherwise it is "returning". First-ever is computed
-- from the full history of the token (no start_date filter on the
-- first_seen CTE) — keep the outer range bounded for cost.
--
-- CAVEAT: BUIDL/OUSG are permissioned — "new wallets" mostly means newly
-- whitelisted institutional wallets, not retail churn. Say this in the
-- write-up.
-- =====================================================================

WITH params AS (
    SELECT
        0x7712c34205737192402172409a8F7ccef8aA2AEc AS token_address,  -- BUIDL
        DATE '2025-01-01' AS start_date,
        DATE '2026-11-11' AS end_date
),

all_participants AS (
    SELECT "from" AS address, block_date
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND token_standard = 'erc20'
      AND contract_address = (SELECT token_address FROM params)
      AND "from" != 0x0000000000000000000000000000000000000000

    UNION ALL

    SELECT "to" AS address, block_date
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND token_standard = 'erc20'
      AND contract_address = (SELECT token_address FROM params)
      AND "to" != 0x0000000000000000000000000000000000000000
),

first_seen AS (
    SELECT address, MIN(block_date) AS first_date
    FROM all_participants
    GROUP BY 1
),

weekly AS (
    SELECT
        DATE_TRUNC('week', p.block_date) AS week,
        p.address
    FROM all_participants p
    JOIN first_seen f ON f.address = p.address
    WHERE p.block_date BETWEEN (SELECT start_date FROM params)
                          AND (SELECT end_date FROM params)
    GROUP BY 1, 2
)

SELECT
    week,
    COUNT(*) AS active_wallets,
    COUNT(*) FILTER (WHERE first_date >= week) AS new_wallets,
    COUNT(*) FILTER (WHERE first_date < week) AS returning_wallets,
    ROUND(100.0 * COUNT(*) FILTER (WHERE first_date >= week) / COUNT(*), 1) AS pct_new
FROM weekly
JOIN first_seen f ON f.address = weekly.address
GROUP BY 1
ORDER BY 1;
