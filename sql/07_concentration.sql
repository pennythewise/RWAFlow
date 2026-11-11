-- =====================================================================
-- 07_concentration.sql
-- Question: how concentrated is ownership — top-10 share and Gini
-- coefficient?
-- Tables used: balances_ethereum.latest, tokens.erc20 (VERIFY via 00_verify_tables.sql)
-- Written: 2026-11-11
--
-- Gini formula on holder balances sorted ascending:
--   G = (2 * SUM(i * x_i)) / (n * SUM(x_i)) - (n + 1) / n
--   where i is the 1-based rank and x_i the balance. G=0 perfect equality,
--   G→1 perfect concentration. Explain this formula in the notebook —
--   interviewers ask about it.
--
-- Uses ALL non-zero holders from balances_ethereum.latest, not just top
-- 20, so the Gini is over the real holder set (still misses wallets whose
-- balance is held via contracts that never appear — acceptable, note it).
-- =====================================================================

WITH params AS (
    SELECT
        0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92 AS token_address  -- OUSG
),

holders AS (
    SELECT address, balance
    FROM balances_ethereum.latest
    WHERE token_address = (SELECT token_address FROM params)
      AND token_standard = 'erc20'
      AND balance > 0
),

ranked AS (
    SELECT
        balance,
        ROW_NUMBER() OVER (ORDER BY balance ASC) AS i,
        COUNT(*) OVER () AS n,
        SUM(balance) OVER () AS total_supply_held
    FROM holders
),

top_shares AS (
    SELECT
        SUM(balance) AS top10_balance,
        (SELECT total_supply_held FROM ranked LIMIT 1) AS total_balance
    FROM (
        SELECT balance
        FROM holders
        ORDER BY balance DESC
        LIMIT 10
    )
)

SELECT
    r.n AS holder_count,
    r.total_supply_held,
    ts.top10_balance,
    ROUND(100.0 * ts.top10_balance / NULLIF(ts.total_balance, 0), 2) AS top10_share_pct,
    ROUND(
        (2.0 * SUM(r.i * r.balance)) / NULLIF(r.n * SUM(r.balance), 0)
        - (r.n + 1.0) / r.n,
        4
    ) AS gini_coefficient
FROM ranked r
CROSS JOIN top_shares ts
GROUP BY r.n, r.total_supply_held, ts.top10_balance, ts.total_balance;
