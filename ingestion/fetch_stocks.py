# ============================================================
# fetch_stocks.py
# This script pulls daily stock price data from Yahoo Finance
# and loads it into our PostgreSQL database
# ============================================================

import yfinance as yf
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

# ============================================================
# STEP 1: Load environment variables from our .env file
# ============================================================
load_dotenv()

# ============================================================
# STEP 2: Read database credentials from environment variables
# ============================================================
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# ============================================================
# STEP 3: Define the list of stock tickers we want to track
# ============================================================
TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "META"]

# ============================================================
# STEP 4: Define the function that fetches stock data
# ============================================================
def fetch_stock_data(ticker):
    """
    Fetches the last 1 year of daily stock price data
    for a given ticker symbol from Yahoo Finance
    """
    print(f"Fetching data for {ticker}...")

    # Download 1 year of daily stock data from Yahoo Finance
    data = yf.download(ticker, period="1y", interval="1d")

    # Reset the index so date becomes a regular column
    data = data.reset_index()

    # The new yfinance returns multi-level columns like ('Close', 'AAPL')
    # We flatten them by taking only the first part and lowercasing it
    data.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in data.columns]

    # The date column comes in as 'index' in new yfinance — rename it to 'date'
    data = data.rename(columns={"index": "date"})

    # Add a column for the ticker symbol
    data["ticker"] = ticker

    # Keep only the columns we need
    data = data[["date", "open", "high", "low", "close", "volume", "ticker"]]

    print(f"✅ Got {len(data)} rows for {ticker}")

    return data


# ============================================================
# STEP 5: Create the table in PostgreSQL if it doesn't exist
# ============================================================
def create_table(cursor):
    """
    Creates the raw_stock_prices table in PostgreSQL
    if it doesn't already exist
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_stock_prices (
            date        DATE,
            open        FLOAT,
            high        FLOAT,
            low         FLOAT,
            close       FLOAT,
            volume      BIGINT,
            ticker      VARCHAR(10)
        )
    """)


# ============================================================
# STEP 6: Load data into PostgreSQL using psycopg2 directly
# ============================================================
def load_to_postgres(df):
    """
    Loads a dataframe into PostgreSQL using psycopg2
    This approach works with all versions of pandas
    """
    print(f"Loading data into PostgreSQL table: raw_stock_prices...")

    # Connect directly to PostgreSQL using psycopg2
    connection = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

    # A cursor lets us execute SQL commands
    cursor = connection.cursor()

    # Drop the table if it exists and recreate it fresh
    # This ensures we always have clean data
    cursor.execute("DROP TABLE IF EXISTS raw_stock_prices")

    # Create the table
    create_table(cursor)

    # Convert the dataframe rows into a list of tuples
    # This is the format psycopg2 expects for bulk inserts
    rows = [
        (
            str(row["date"]),
            float(row["open"]) if pd.notna(row["open"]) else None,
            float(row["high"]) if pd.notna(row["high"]) else None,
            float(row["low"]) if pd.notna(row["low"]) else None,
            float(row["close"]) if pd.notna(row["close"]) else None,
            int(row["volume"]) if pd.notna(row["volume"]) else None,
            str(row["ticker"])
        )
        for _, row in df.iterrows()
    ]

    # Insert all rows at once using execute_values
    # This is much faster than inserting one row at a time
    execute_values(
        cursor,
        "INSERT INTO raw_stock_prices (date, open, high, low, close, volume, ticker) VALUES %s",
        rows
    )

    # Commit the transaction to save the data permanently
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    print(f"✅ Data loaded into raw_stock_prices successfully!")


# ============================================================
# STEP 7: Main function that ties everything together
# ============================================================
def main():
    print("🚀 Starting stock data ingestion...")

    # Create an empty list to store data for all tickers
    all_data = []

    # Loop through each ticker and fetch its data
    for ticker in TICKERS:
        df = fetch_stock_data(ticker)
        all_data.append(df)

    # Combine all ticker dataframes into one single dataframe
    combined_df = pd.concat(all_data, ignore_index=True)

    print(f"📊 Total rows fetched: {len(combined_df)}")

    # Load the combined dataframe into PostgreSQL
    load_to_postgres(combined_df)

    print("🎉 Ingestion complete!")


# ============================================================
# This makes sure main() only runs when we execute this file
# directly — not when it's imported by another script
# ============================================================
if __name__ == "__main__":
    main()