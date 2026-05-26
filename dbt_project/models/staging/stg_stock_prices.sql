-- ============================================================
-- stg_stock_prices.sql
-- This is our staging model
-- It cleans up the raw stock data from our ingestion script
-- ============================================================

WITH source AS (

    -- Pull all data from our raw_stock_prices table in PostgreSQL
    SELECT * FROM {{ source('stock_pipeline', 'raw_stock_prices') }}

),

cleaned AS (

    SELECT
        -- Cast date to proper date type
        date::DATE                              AS date,

        -- Uppercase ticker for consistency
        UPPER(ticker)                           AS ticker,

        -- Round prices to 2 decimal places for cleanliness
        ROUND(open::NUMERIC, 2)                 AS open,
        ROUND(high::NUMERIC, 2)                 AS high,
        ROUND(low::NUMERIC, 2)                  AS low,
        ROUND(close::NUMERIC, 2)                AS close,

        -- Volume as a whole number
        volume::BIGINT                          AS volume,

        -- Calculate daily price range (high - low)
        ROUND((high - low)::NUMERIC, 2)         AS daily_range,

        -- Calculate daily return percentage
        ROUND(
            ((close - open) / NULLIF(open, 0) * 100)::NUMERIC
        , 2)                                    AS daily_return_pct

    FROM source

    -- Remove any rows where date or ticker is missing
    WHERE date IS NOT NULL
    AND ticker IS NOT NULL

)

SELECT * FROM cleaned