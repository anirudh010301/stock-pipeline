Perfect! Everything is already pushed to GitHub. ✅
Now let's update the README. Type this and hit Enter:
bashcode README.md
Then replace the entire file with this final version:
markdown# 📈 Stock Price Data Pipeline

An end-to-end batch data pipeline that automatically ingests real stock market data daily, transforms it, stores it in a production-grade database, and displays it on an interactive Bloomberg-style dashboard — fully orchestrated by Apache Airflow and containerized with Docker.

---

## 🏗️ Architecture

yfinance API → Python Ingestion → PostgreSQL (Raw) → dbt Transformation → PostgreSQL (Marts) → Streamlit Dashboard
↑
Apache Airflow (Daily Schedule at Midnight)
Docker & Docker Compose (Single Command Setup)

---

## 🛠️ Tech Stack

| Layer            | Tool                      | Purpose                                           |
| ---------------- | ------------------------- | ------------------------------------------------- |
| Data Source      | `yfinance`                | Pulls real stock price data (OHLCV)               |
| Ingestion        | `Python`                  | Extracts and loads raw data into PostgreSQL       |
| Orchestration    | `Apache Airflow`          | Schedules and monitors pipeline daily at midnight |
| Transformation   | `dbt Core`                | Cleans and transforms raw data using SQL models   |
| Data Warehouse   | `PostgreSQL`              | Stores all data — also used as Airflow backend    |
| Dashboard        | `Streamlit`               | Interactive Bloomberg-style visualization         |
| Containerization | `Docker & Docker Compose` | Runs entire stack with a single command           |
| Version Control  | `Git & GitHub`            | Tracks all code changes publicly                  |

---

## 📊 Dashboard Features

- 📈 Candlestick price chart with 7-day and 30-day moving averages
- 📉 Daily returns and 30-day rolling volatility charts
- 📦 Volume analysis with 7-day average volume
- 🔢 Key metrics — latest close, 52-week high/low, volatility
- 🆚 Normalized price comparison across all 5 stocks
- 📋 Raw data table with all calculated metrics

---

## ⚙️ Pipeline DAG

The Airflow DAG runs every day at midnight with 3 tasks in order:
ingest_stock_data → dbt_staging → dbt_marts

| Task                | Type           | Purpose                                            |
| ------------------- | -------------- | -------------------------------------------------- |
| `ingest_stock_data` | PythonOperator | Pulls data from yfinance and loads into PostgreSQL |
| `dbt_staging`       | BashOperator   | Runs staging model to clean raw data               |
| `dbt_marts`         | BashOperator   | Runs marts model to calculate moving averages      |

---

## 📁 Project Structure

stock-pipeline/
│
├── airflow/ # Airflow configuration
│ └── airflow.cfg # Airflow settings (PostgreSQL backend)
├── dags/
│ └── stock_pipeline_dag.py # Airflow DAG definition
├── ingestion/
│ └── fetch_stocks.py # Python ingestion script
├── dashboard/
│ ├── app.py # Streamlit dashboard
│ └── requirements.txt # Dashboard dependencies
├── dbt_project/
│ ├── models/
│ │ ├── staging/ # stg_stock_prices.sql
│ │ └── marts/ # fct_stock_prices.sql
│ └── dbt_project.yml # dbt configuration
├── docker/
│ ├── docker-compose.yml # Full stack Docker config
│ ├── Dockerfile.airflow # Custom Airflow image with dependencies
│ └── init.sql # Creates airflow_db on startup
├── .env # Environment variables (not on GitHub)
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## 🚀 How to Run This Project

### Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM allocated to Docker
- Git installed

### 1. Clone the repository

```bash
git clone https://github.com/anirudhadda/stock-pipeline.git
cd stock-pipeline
```

### 2. Create your `.env` file

```bash
touch .env
```

Add the following to `.env`:
POSTGRES_USER=stock_user
POSTGRES_PASSWORD=stock_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=stock_db

### 3. Start the entire stack

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 4. Access the services

| Service             | URL                   |
| ------------------- | --------------------- |
| Airflow UI          | http://localhost:8080 |
| Streamlit Dashboard | http://localhost:8501 |

### 5. Trigger the pipeline

- Open http://localhost:8080
- Login with `admin` / `admin`
- Enable the `stock_pipeline` DAG
- Click ▶️ to trigger a run

### 6. Stop everything

```bash
docker-compose -f docker/docker-compose.yml down
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

## 🐛 Known Issues & Fixes

| Issue                                   | Fix                                                       |
| --------------------------------------- | --------------------------------------------------------- |
| Airflow scheduler crashing              | Switched Airflow backend to PostgreSQL + fixed secret key |
| `DROP TABLE` failing due to dbt views   | Added `CASCADE` to drop command                           |
| yfinance version incompatibility        | Upgraded to `yfinance==1.4.0`                             |
| SQLAlchemy version conflict with pandas | Used `psycopg2` directly instead                          |
| dbt marts hanging                       | Increased Docker memory to 12GB                           |
| dbt `profiles.yml` not found in Docker  | Added profiles.yml to custom Dockerfile                   |

---

## 👤 Author

**Anirudh Adda**
