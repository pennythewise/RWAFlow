-- =====================================================================
-- 03_supply_over_time.sql
-- Question: how does circulating supply evolve, and does
-- (cumulative mints - burns) reconcile with the token's totalSupply?
-- Tables used: tokens.transfers, tokens.erc20 (VERIFY via 00_verify_tables.sql)
-- Written: 2026-11-11
--
-- APPROXIMATION: supply is reconstructed from Transfer events only.
-- - Rebasing tokens (BUIDL): interest accrual does NOT emit Transfers,
--   so reconstructed supply drifts below true totalSupply. Expect and
--   document the delta.
-- - If tokens are minted to non-zero addresses (issuer wallets), the
--   "mint" detection misses them; check top recipients in 04/07.
--
-- RECONCILIATION (Phase 1 done-criteria): compare final cumulative net
-- supply to on-chain totalSupply() — query it via a tiny web3.py script
-- or Etherscan read; state the tolerance you observe.
-- =====================================================================

WITH params AS (
    SELECT
        0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92 AS token_address,  -- OUSG
        DATE '2024-01-01' AS start_date
),

ZERO AS (SELECT 0x0000000000000000000000000000000000000000::varbinary AS addr),

daily AS (
    SELECT
        block_date,
        SUM(CASE WHEN "to" = (SELECT addr FROM ZERO) THEN -amount ELSE 0 END) AS burned,
        SUM(CASE WHEN "from" = (SELECT addr FROM ZERO) THEN amount ELSE 0 END) AS minted,
        SUM(amount) AS gross_volume
    FROM tokens.transfers
    WHERE blockchain = 'ethereum'
      AND token_standard = 'erc20'
      AND contract_address = (SELECT token_address FROM params)
      AND block_date >= (SELECT start_date FROM params)
    GROUP BY 1
)

SELECT
    block_date,
    minted,
    burned,
    SUM(minted - burned) OVER (ORDER BY block_date) AS net_supply_from_events,
    SUM(gross_volume) OVER (ORDER BY block_date) AS cumulative_volume
FROM daily
ORDER BY block_date;
