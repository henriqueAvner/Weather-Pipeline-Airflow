from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

import logging
logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'

load_dotenv(env_path)

user = os.getenv('user')
password = os.getenv('password')
database = os.getenv('database')

host = 'host.docker.internal'
# host = 'localhost'

def get_engine():

  logger.info(f"Conectando em {host}:5432/{database}")

  return create_engine(
    f"postgresql+psycopg2://{user}:{quote_plus(password)}@{host}:5432/{database}"
  )


engine = get_engine()

def load_weather_data(table_name:str, df):

  df.to_sql(
    name=table_name,
    con=engine,
    if_exists='append',
    index=False
  )

  logger.info(f"Dados carregados com sucesso!!!")

  df_check = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)

  logger.info(f"Total de registros na tabela: {len(df_check)}\n")