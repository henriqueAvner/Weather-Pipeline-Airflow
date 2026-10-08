import pandas as pd
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

path_name = Path(__file__).parent.parent / 'data' / 'weather_data.json'

colunms_names_to_drop = ['weather', 'weather_icon']

columns_to_normalize_datetime = ['datetime', 'sunrise', 'sunset']

columns_names_to_rename = {
  "dt": "datetime",
  "name": "city_name",
  "cod": "code",
  "coord.lon": "longitude",
  "coord.lat": "latitude",
  "main.temp": "temperature",
  "main.feels_like": "feels_like",
  "main.temp_min": "temp_min",
  "main.temp_max": "temp_max",
  "main.pressure": "pressure",
  "main.humidity": "humidity",
  "main.sea_level": "sea_level",
  "main.grnd_level": "grnd_level",
  "wind.speed": "wind_speed",
  "wind.deg": "wind_deg",
  "wind.gust": "wind_gust",
  "clouds.all": "clouds",
  "sys.id": "sys_id",
  "sys.country": "country",
  "sys.sunrise": "sunrise",
  "sys.sunset": "sunset",
}

def create_dataframe(path_name:str) -> pd.DataFrame:

  logger.info("Criando DataFrame do arquivo JSON...")
  path = path_name

  if not path.exists():
    raise FileNotFoundError(f"Arquivo nao encontrado: {path}")

  with open(path) as file:
    data = json.load(file)

  df = pd.json_normalize(data)
  logger.info(f"\n DataFrame criado com {len(df)} linhas(s)")

  return df

def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:
  df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))

  df_weather = df_weather.rename(columns={
    'id': 'weather_id',
    'main': 'weather_main',
    'description': 'weather_description',
    'icon': 'weather_icon'
  })

  df = pd.concat([df, df_weather], axis=1)

  logger.info(f"\n Coluna 'weather' normalizada - {len(df.columns)} colunas")

  return df

def drop_columns(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:

  logger.info(f"Removendo colunas: {columns_names}")

  df = df.drop(columns=columns_names)

  logger.info(f"Colunas removidas - {len(df.columns)} colunas restantes")

  return df


def rename_colunms(df: pd.DataFrame, columns_names:dict[str,str]) -> pd.DataFrame:

  logging.info(f"\n Renomeando {len(columns_names)} colunas...")

  df = df.rename(columns=columns_names)

  logging.info(f"Colunas renomeadas")

  return df

def normalize_datetime_columns(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:
  logger.info(f"\nConvertendo colunas para datetime: {columns_names}")

  for name in columns_names:
    df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert('America/Sao_Paulo')

  logger.info(f"\nColunas convertidas para datetime\n")

  return df

def data_transformations():
  print("\n Iniciando transformações")
  df = create_dataframe(path_name)
  df = normalize_weather_columns(df)
  df = drop_columns(df, colunms_names_to_drop)
  df = rename_colunms(df, columns_names_to_rename)
  df = normalize_datetime_columns(df, columns_to_normalize_datetime)

  logger.info("Transformações concluídas\n")
  return df