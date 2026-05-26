# ============================================================
# app.py
# Bloomberg-style Stock Price Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

# ============================================================
# STEP 1: Load environment variables
# ============================================================
load_dotenv()

# ============================================================
# STEP 2: Page configuration — dark theme, wide layout
# ============================================================
st.set_page_config(
    page_title="Stock Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STEP 3: Custom CSS for Bloomberg-style dark theme
# ============================================================
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #111111; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 16px;
    }

    /* Metric label */
    [data-testid="metric-container"] label {
        color: #888888 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Metric value */
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: bold;
    }

    /* Positive delta */
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        font-size: 13px !important;
    }

    /* Section headers */
    h2, h3 { color: #ffffff !important; }

    /* Divider */
    hr { border-color: #2a2a2a; }

    /* Dataframe */
    .stDataFrame { background-color: #1a1a1a; }

    /* Selectbox */
    .stSelectbox label { color: #888888 !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# STEP 4: Connect to PostgreSQL
# ============================================================
@st.cache_resource
def get_connection():
    """Creates and returns a PostgreSQL connection"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

# ============================================================
# STEP 5: Load data from PostgreSQL
# ============================================================
@st.cache_data(ttl=3600)
def load_data():
    """Loads all stock data from our fct_stock_prices table"""
    conn = get_connection()
    query = """
        SELECT
            date, ticker, open, high, low, close,
            volume, daily_range, daily_return_pct,
            ma_7, ma_30, avg_volume_7
        FROM fct_stock_prices
        ORDER BY ticker, date
    """
    df = pd.read_sql(query, conn)
    df["date"] = pd.to_datetime(df["date"])
    return df

# ============================================================
# STEP 6: Plotly dark theme config
# All our charts will use this consistent dark theme
# ============================================================
CHART_THEME = dict(
    plot_bgcolor="#0a0a0a",
    paper_bgcolor="#0a0a0a",
    font=dict(color="#e0e0e0", family="monospace"),
    xaxis=dict(
        gridcolor="#1a1a1a",
        linecolor="#2a2a2a",
        tickcolor="#2a2a2a"
    ),
    yaxis=dict(
        gridcolor="#1a1a1a",
        linecolor="#2a2a2a",
        tickcolor="#2a2a2a"
    ),
    legend=dict(
        bgcolor="#111111",
        bordercolor="#2a2a2a",
        borderwidth=1
    )
)

# ============================================================
# STEP 7: Dashboard header
# ============================================================
col_title, col_time = st.columns([3, 1])
with col_title:
    st.markdown("# 📈 Stock Analytics Dashboard")
    st.markdown("<p style='color:#888888; font-size:13px;'>Real-time analysis powered by yfinance · PostgreSQL · dbt</p>", unsafe_allow_html=True)
with col_time:
    st.markdown(f"<p style='color:#888888; font-size:12px; text-align:right; margin-top:20px;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# STEP 8: Load data
# ============================================================
df = load_data()

# ============================================================
# STEP 9: Sidebar filters
# ============================================================
st.sidebar.markdown("## ⚙️ Filters")

# Ticker selector
tickers = sorted(df["ticker"].unique().tolist())
selected_ticker = st.sidebar.selectbox("Select Stock", tickers)

# Date range selector
min_date = df["date"].min()
max_date = df["date"].max()
selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Moving average toggles
st.sidebar.markdown("## 📊 Chart Options")
show_ma7 = st.sidebar.toggle("Show 7-Day MA", value=True)
show_ma30 = st.sidebar.toggle("Show 30-Day MA", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='color:#888888; font-size:11px;'>Stocks tracked: AAPL · GOOGL · MSFT · AMZN · META</p>", unsafe_allow_html=True)

# ============================================================
# STEP 10: Filter dataframe
# ============================================================
filtered_df = df[
    (df["ticker"] == selected_ticker) &
    (df["date"] >= pd.to_datetime(selected_dates[0])) &
    (df["date"] <= pd.to_datetime(selected_dates[1]))
].copy()

# ============================================================
# STEP 11: SECTION 1 — Key Metrics
# ============================================================
st.markdown(f"## {selected_ticker} — Key Metrics")

latest = filtered_df.iloc[-1]
prev = filtered_df.iloc[-2]

price_change = latest["close"] - prev["close"]
price_change_pct = (price_change / prev["close"]) * 100
high_52w = filtered_df["high"].max()
low_52w = filtered_df["low"].min()
avg_volume = filtered_df["volume"].mean()
volatility = filtered_df["daily_return_pct"].std()

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "Latest Close",
        f"${latest['close']:.2f}",
        f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
    )
with col2:
    st.metric("7-Day MA", f"${latest['ma_7']:.2f}")
with col3:
    st.metric("30-Day MA", f"${latest['ma_30']:.2f}")
with col4:
    st.metric("52-Week High", f"${high_52w:.2f}")
with col5:
    st.metric("52-Week Low", f"${low_52w:.2f}")
with col6:
    st.metric("Volatility (Std)", f"{volatility:.2f}%")

st.markdown("---")

# ============================================================
# STEP 12: SECTION 2 — Candlestick Chart with Moving Averages
# ============================================================
st.markdown(f"## {selected_ticker} — Price Chart")

fig_price = go.Figure()

# Candlestick
fig_price.add_trace(go.Candlestick(
    x=filtered_df["date"],
    open=filtered_df["open"],
    high=filtered_df["high"],
    low=filtered_df["low"],
    close=filtered_df["close"],
    name="Price",
    increasing_line_color="#00ff88",   # Green for up days
    decreasing_line_color="#ff4444"    # Red for down days
))

# 7-day moving average
if show_ma7:
    fig_price.add_trace(go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["ma_7"],
        name="7-Day MA",
        line=dict(color="#f0a500", width=1.5)
    ))

# 30-day moving average
if show_ma30:
    fig_price.add_trace(go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["ma_30"],
        name="30-Day MA",
        line=dict(color="#00aaff", width=1.5)
    ))

fig_price.update_layout(
    height=500,
    xaxis_rangeslider_visible=False,
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    **CHART_THEME
)

st.plotly_chart(fig_price, use_container_width=True)

st.markdown("---")

# ============================================================
# STEP 13: SECTION 3 — Daily Returns & Volatility
# ============================================================
st.markdown(f"## {selected_ticker} — Daily Returns & Volatility")

col_ret, col_vol = st.columns(2)

with col_ret:
    # Daily returns bar chart
    # Green bars for positive days, red for negative
    colors = ["#00ff88" if x >= 0 else "#ff4444" for x in filtered_df["daily_return_pct"]]

    fig_returns = go.Figure()
    fig_returns.add_trace(go.Bar(
        x=filtered_df["date"],
        y=filtered_df["daily_return_pct"],
        name="Daily Return %",
        marker_color=colors
    ))
    fig_returns.update_layout(
        height=350,
        title="Daily Return (%)",
        xaxis_title="Date",
        yaxis_title="Return (%)",
        **CHART_THEME
    )
    st.plotly_chart(fig_returns, use_container_width=True)

with col_vol:
    # Rolling 30-day volatility
    # Volatility = standard deviation of daily returns over 30 days
    filtered_df["rolling_volatility"] = filtered_df["daily_return_pct"].rolling(30).std()

    fig_volatility = go.Figure()
    fig_volatility.add_trace(go.Scatter(
        x=filtered_df["date"],
        y=filtered_df["rolling_volatility"],
        name="30-Day Volatility",
        line=dict(color="#ff6600", width=2),
        fill="tozeroy",
        fillcolor="rgba(255,102,0,0.1)"
    ))
    fig_volatility.update_layout(
        height=350,
        title="30-Day Rolling Volatility (%)",
        xaxis_title="Date",
        yaxis_title="Volatility (%)",
        **CHART_THEME
    )
    st.plotly_chart(fig_volatility, use_container_width=True)

st.markdown("---")

# ============================================================
# STEP 14: SECTION 4 — Volume Analysis
# ============================================================
st.markdown(f"## {selected_ticker} — Volume Analysis")

fig_volume = go.Figure()

fig_volume.add_trace(go.Bar(
    x=filtered_df["date"],
    y=filtered_df["volume"],
    name="Daily Volume",
    marker_color="#2a4a7f"
))

fig_volume.add_trace(go.Scatter(
    x=filtered_df["date"],
    y=filtered_df["avg_volume_7"],
    name="7-Day Avg Volume",
    line=dict(color="#f0a500", width=2)
))

fig_volume.update_layout(
    height=350,
    xaxis_title="Date",
    yaxis_title="Volume",
    **CHART_THEME
)

st.plotly_chart(fig_volume, use_container_width=True)

st.markdown("---")

# ============================================================
# STEP 15: SECTION 5 — All 5 Stocks Comparison
# ============================================================
st.markdown("## All Stocks — Comparison")

col_comp1, col_comp2 = st.columns(2)

with col_comp1:
    # Normalized price comparison
    # We normalize to 100 at the start so we can compare
    # stocks with very different prices fairly
    fig_compare = go.Figure()

    colors_map = {
        "AAPL": "#00ff88",
        "GOOGL": "#00aaff",
        "MSFT": "#f0a500",
        "AMZN": "#ff6600",
        "META": "#ff44aa"
    }

    for ticker in tickers:
        ticker_df = df[
            (df["ticker"] == ticker) &
            (df["date"] >= pd.to_datetime(selected_dates[0])) &
            (df["date"] <= pd.to_datetime(selected_dates[1]))
        ].copy()

        # Normalize: start at 100 for fair comparison
        first_close = ticker_df["close"].iloc[0]
        ticker_df["normalized"] = (ticker_df["close"] / first_close) * 100

        fig_compare.add_trace(go.Scatter(
            x=ticker_df["date"],
            y=ticker_df["normalized"],
            name=ticker,
            line=dict(color=colors_map.get(ticker, "#ffffff"), width=2)
        ))

    fig_compare.update_layout(
        height=400,
        title="Normalized Price Performance (Base = 100)",
        xaxis_title="Date",
        yaxis_title="Normalized Price",
        **CHART_THEME
    )
    st.plotly_chart(fig_compare, use_container_width=True)

with col_comp2:
    # Latest metrics comparison table for all stocks
    summary_rows = []
    for ticker in tickers:
        ticker_df = df[df["ticker"] == ticker]
        latest_row = ticker_df.iloc[-1]
        prev_row = ticker_df.iloc[-2]
        chg = latest_row["close"] - prev_row["close"]
        chg_pct = (chg / prev_row["close"]) * 100
        summary_rows.append({
            "Ticker": ticker,
            "Close": f"${latest_row['close']:.2f}",
            "Change": f"{chg:+.2f}",
            "Change %": f"{chg_pct:+.2f}%",
            "52W High": f"${ticker_df['high'].max():.2f}",
            "52W Low": f"${ticker_df['low'].min():.2f}",
            "Volatility": f"{ticker_df['daily_return_pct'].std():.2f}%"
        })

    summary_df = pd.DataFrame(summary_rows)
    st.markdown("### All Stocks Summary")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================
# STEP 16: SECTION 6 — Raw Data Table
# ============================================================
st.markdown(f"## {selected_ticker} — Raw Data")

st.dataframe(
    filtered_df[[
        "date", "ticker", "open", "high", "low",
        "close", "volume", "daily_range",
        "daily_return_pct", "ma_7", "ma_30"
    ]].sort_values("date", ascending=False),
    use_container_width=True,
    hide_index=True
)