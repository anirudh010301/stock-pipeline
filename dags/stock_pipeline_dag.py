# ============================================================
# stock_pipeline_dag.py
# This is our Airflow DAG file
# It tells Airflow to run our pipeline every day at midnight
# ============================================================

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# ============================================================
# STEP 1: Add our project path to Python's search path
# This allows Airflow to find our ingestion script
# ============================================================
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ============================================================
# STEP 2: Import our ingestion function
# ============================================================
from ingestion.fetch_stocks import main as ingest_stocks

# ============================================================
# STEP 3: Define default arguments for our DAG
# These apply to every task in the DAG
# ============================================================
default_args = {
    'owner': 'stock_pipeline',           # Who owns this DAG
    'depends_on_past': False,            # Don't wait for previous runs
    'email_on_failure': False,           # Don't send emails on failure
    'email_on_retry': False,             # Don't send emails on retry
    'retries': 1,                        # Retry once if a task fails
    'retry_delay': timedelta(minutes=5)  # Wait 5 minutes before retrying
}

# ============================================================
# STEP 4: Define the DAG
# ============================================================
with DAG(
    dag_id='stock_pipeline',             # Unique name for our DAG
    default_args=default_args,
    description='Daily stock price ingestion and transformation pipeline',
    schedule='0 0 * * *',               # Run every day at midnight (cron syntax)
    start_date=datetime(2024, 1, 1),    # When the DAG starts
    catchup=False,                       # Don't run missed past runs
    tags=['stock', 'pipeline']           # Tags for filtering in the UI
) as dag:

    # ============================================================
    # TASK 1: Ingest stock data from yfinance into PostgreSQL
    # PythonOperator runs a Python function as a task
    # ============================================================
    ingest_task = PythonOperator(
        task_id='ingest_stock_data',         # Unique name for this task
        python_callable=ingest_stocks,        # The function to run
    )

    # ============================================================
    # TASK 2: Run dbt staging model
    # BashOperator runs a bash command as a task
    # ============================================================
    dbt_staging_task = BashOperator(
        task_id='dbt_staging',
        bash_command=f'cd {os.path.join(os.path.dirname(__file__), "..", "dbt_project")} && dbt run --select staging',
    )

    # ============================================================
    # TASK 3: Run dbt marts model
    # ============================================================
    dbt_marts_task = BashOperator(
        task_id='dbt_marts',
        bash_command=f'cd {os.path.join(os.path.dirname(__file__), "..", "dbt_project")} && dbt run --select marts',
    )

    # ============================================================
    # STEP 5: Define the order of tasks
    # >> means "then run"
    # ingest first, then staging, then marts
    # ============================================================
    ingest_task >> dbt_staging_task >> dbt_marts_task