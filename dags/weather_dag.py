from datetime import datetime, timedelta

from dotenv import load_dotenv
from airflow.sdk import dag, task
from pathlib import Path
import sys, os

sys.path.insert(0, '/opt/airflow/src')

from extract_data import extract_weather_data
from load_data import load_weather_data
from transform_data import data_transformations

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('API_KEY')
PARQUET_PATH = Path('/opt/airflow/data/temp_data_parquet')

url = f'https://api.openweathermap.org/data/2.5/weather?q=Minas Gerais,BR&units=metric&appid={API_KEY}'

@dag(
  dag_id = 'weather_pipeline',
  default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
  },
  description='Pipeline ETL - Minas Gerais',
  schedule='0 */1 * * *',
  start_date=datetime(2026, 10, 8),
  catchup = False,
  tags=['weather', 'etl']
)
def weather_pipeline():

  @task
  def extract():
    extract_weather_data(url)

  @task
  def transform():
    df = data_transformations()
    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_PATH, index=False)

  @task
  def load():
    import pandas as pd
    df = pd.read_parquet(PARQUET_PATH)
    load_weather_data('mg_weather', df)


  extract() >> transform() >> load()

weather_pipeline()
