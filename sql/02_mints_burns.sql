-- =====================================================================
-- 02_mints_burns.sql
-- Question: are tokens being created (mint) or destroyed (burn), and how
-- much per day?
-- Tables used: tokens.transfers (VERIFY via 00_verify_tables.sql)
-- Written: 2026-11-11
--
-- A mint is a Transfer FROM the zero address; a burn is a Transfer TO the
-- zero address. ERC-4626 vaults may emit mint/burn as Deposit/Withdraw
-- events instead — for OUSG/USDY check whether plain Transfers capture
-- issuance; if issuance looks absent, decoded_events for Deposit events
-- will be needed (see docs/standards.md).
--
-- CAVEAT for BUIDL: it is a rebasing token. Interest accrual increases
-- balances WITHOUT Transfer events, so supply growth here understates
-- true supply growth. Document the gap.
-- =====================================================================

WITH params AS (
    SELECT
        0x7712c34205737192402172409a8F7ccef8aA2AEc AS token_address,  -- BUIDL
        DATE '2024-01-01' AS start_date
),

ZERO AS (SELECT 0x0000000000000000000000000000000000000000::varbinary AS addr),

flows AS (
    SELECT
        t.block_date,
        CASE
            WHEN t."from" = (SELECT addr FROM ZERO) THEN 'mint'
            WHEN t."to"   = (SELECT addr FROM ZERO) THEN 'burn'
        END AS flow_type,
        t.amount,
        t.amount_usd,
        t.tx_hash
    FROM tokens.transfers t
    WHERE t.blockchain = 'ethereum'
      AND t.token_standard = 'erc20'
      AND t.contract_address = (SELECT token_address FROM params)
      AND t.block_date >= (SELECT start_date FROM params)
      AND (t."from" = (SELECT addr FROM ZERO) OR t."to" = (SELECT addr FROM ZERO))
)

SELECT
    block_date,
    flow_type,
    COUNT(*) AS event_count,
    SUM(amount) AS tokens_flowed,
    SUM(amount_usd) AS usd_flowed
FROM flows
GROUP BY 1, 2
ORDER BY 1, 2;
