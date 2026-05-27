-- ============================================================
-- fct_stock_prices.sql
-- Final analytics-ready table
-- Simplified for better performance
-- ============================================================

WITH staging AS (
    SELECT * FROM {{ ref('stg_stock_prices') }}
),

final AS (
    SELECT
        date,
        ticker,
        open,
        high,
        low,
        close,
        volume,
        daily_range,
        daily_return_pct,

        -- 7-day moving average
        ROUND(AVG(close) OVER (
            PARTITION BY ticker
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )::NUMERIC, 2) AS ma_7,

        -- 30-day moving average
        ROUND(AVG(close) OVER (
            PARTITION BY ticker
            ORDER BY date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        )::NUMERIC, 2) AS ma_30,

        -- 7-day average volume
        ROUND(AVG(volume) OVER (
            PARTITION BY ticker
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        )::NUMERIC, 0) AS avg_volume_7

    FROM staging
)

SELECT * FROM final
ORDER BY ticker, date