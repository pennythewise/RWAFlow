-- =====================================================================
-- 00_verify_tables.sql — RUN THIS FIRST on Dune before any other query.
-- Purpose: confirm the spellbook table/column names below still exist.
-- Tables used: tokens.transfers, balances_ethereum.latest, tokens.erc20
-- Written: 2026-11-11
--
-- If any step errors, check https://dune.com/data (search "transfers",
-- "balances") for the current names, then update the -- VERIFY: comments
-- at the top of every sql/0*.sql file.
-- =====================================================================

-- Step 1: transfers schema — expect columns incl. blockchain, block_date,
-- block_time, contract_address, "from", "to", amount, amount_usd,
-- token_standard, tx_hash
SELECT *
FROM tokens.transfers
WHERE blockchain = 'ethereum'
  AND block_date >= CURRENT_DATE - INTERVAL '1' DAY
LIMIT 5;

-- Step 2: latest balances schema — expect address, token_address,
-- token_symbol, balance, balance_usd, updated_at
SELECT *
FROM balances_ethereum.latest
WHERE token_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48  -- USDC
LIMIT 5;

-- Step 3: token metadata — expect symbol, name, decimals
SELECT *
FROM tokens.erc20
WHERE blockchain = 'ethereum'
  AND contract_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
LIMIT 1;

-- Step 4: our target tokens are indexed at all (non-empty = good)
SELECT contract_address, symbol, name, decimals
FROM tokens.erc20
WHERE blockchain = 'ethereum'
  AND contract_address IN (
    0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48,  -- USDC
    0x7712c34205737192402172409a8F7ccef8aA2AEc,  -- BUIDL
    0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92,  -- OUSG
    0x96F6eF951840721AdBF46Ac996b59E0235CB985C   -- USDY
  );
