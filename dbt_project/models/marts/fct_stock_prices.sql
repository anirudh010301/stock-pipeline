-- ============================================================
-- fct_stock_prices.sql
-- This is our marts model (final analytics-ready table)
-- It builds on top of our staging model and adds:
-- 1. 7-day moving average
-- 2. 30-day moving average
-- 3. 7-day average volume
-- ============================================================

WITH staging AS (

    -- Pull cleaned data from our staging model
    -- ref() is dbt syntax that references another dbt model
    SELECT * FROM {{ ref('stg_stock_prices') }}

),

final AS (

    SELECT
        -- Basic stock information
        date,
        ticker,
        open,
        high,
        low,
        close,
        volume,
        daily_range,
        daily_return_pct,

        -- 7-day moving average of closing price
        -- This smooths out short term price fluctuations
        ROUND(
            AVG(close) OVER (
                PARTITION BY ticker          -- Calculate separately for each stock
                ORDER BY date
                ROWS BETWEEN 6 PRECEDING    -- Look back 6 rows (7 days total)
                AND CURRENT ROW
            )::NUMERIC
        , 2) AS ma_7,

        -- 30-day moving average of closing price
        -- This smooths out longer term price fluctuations
        ROUND(
            AVG(close) OVER (
                PARTITION BY ticker          -- Calculate separately for each stock
                ORDER BY date
                ROWS BETWEEN 29 PRECEDING   -- Look back 29 rows (30 days total)
                AND CURRENT ROW
            )::NUMERIC
        , 2) AS ma_30,

        -- 7-day average volume
        -- Shows if trading activity is increasing or decreasing
        ROUND(
            AVG(volume) OVER (
                PARTITION BY ticker          -- Calculate separately for each stock
                ORDER BY date
                ROWS BETWEEN 6 PRECEDING    -- Look back 6 rows (7 days total)
                AND CURRENT ROW
            )::NUMERIC
        , 0) AS avg_volume_7

    FROM staging

)

SELECT * FROM final
ORDER BY ticker, date