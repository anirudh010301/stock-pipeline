# 📈 Stock Price Data Pipeline

An end-to-end batch data pipeline that automatically ingests real stock market data daily, transforms it, stores it in a production-grade database, and displays it on an interactive Bloomberg-style dashboard.

---

## 🏗️ Architecture

yfinance API → Python Ingestion → PostgreSQL → dbt Transformation → Streamlit Dashboard
↑
Docker & Airflow

---

## 🛠️ Tech Stack

| Layer            | Tool                      | Purpose                             |
| ---------------- | ------------------------- | ----------------------------------- |
| Data Source      | `yfinance`                | Pulls real stock price data (OHLCV) |
| Ingestion        | `Python`                  | Extracts and loads raw data         |
| Orchestration    | `Apache Airflow`          | Schedules pipeline to run daily     |
| Transformation   | `dbt Core`                | Cleans and transforms raw data      |
| Data Warehouse   | `PostgreSQL`              | Stores all data via Docker          |
| Dashboard        | `Streamlit`               | Interactive visualization           |
| Containerization | `Docker & Docker Compose` | Packages everything together        |
| Version Control  | `Git & GitHub`            | Tracks all code changes             |

---

## 📊 Dashboard Features

- 📈 Candlestick price chart with 7-day and 30-day moving averages
- 📉 Daily returns and 30-day rolling volatility charts
- 📦 Volume analysis with 7-day average volume
- 🔢 Key metrics — latest close, 52-week high/low, volatility
- 🆚 Normalized price comparison across all 5 stocks
- 📋 Raw data table with all metrics

---

## 📁 Project Structure

stock-pipeline/
│
├── dags/ # Airflow DAG files
├── ingestion/
│ └── fetch_stocks.py # Python ingestion script
├── dashboard/
│ └── app.py # Streamlit dashboard
├── dbt_project/
│ ├── models/
│ │ ├── staging/ # Staging models
│ │ └── marts/ # Final analytics models
│ └── dbt_project.yml # dbt configuration
├── docker/
│ └── docker-compose.yml # Docker configuration
├── .env # Environment variables (not on GitHub)
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## 🚀 How to Run This Project

### 1. Clone the repository

```bash
git clone https://github.com/addaanirudh/stock-pipeline.git
cd stock-pipeline
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

```bash
touch .env
```

Add the following to `.env`:
POSTGRES_USER=stock_user
POSTGRES_PASSWORD=stock_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=stock_db

### 5. Start PostgreSQL with Docker

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 6. Run the ingestion script

```bash
python ingestion/fetch_stocks.py
```

### 7. Run dbt transformations

```bash
cd dbt_project
dbt run
cd ..
```

### 8. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

---

## 📦 Stocks Tracked

| Ticker  | Company               |
| ------- | --------------------- |
| `AAPL`  | Apple Inc.            |
| `GOOGL` | Alphabet Inc.         |
| `MSFT`  | Microsoft Corporation |
| `AMZN`  | Amazon.com Inc.       |
| `META`  | Meta Platforms Inc.   |

---

## 👤 Author

**Anirudh Adda**

- GitHub: [@addaanirudh](https://github.com/addaanirudh)
