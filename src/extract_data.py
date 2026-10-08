import requests
import json
from pathlib import Path
from logging import getLogger

import logging

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s')



def extract_weather_data(url:str) -> list:
  resp = requests.get(url)
  data = resp.json()

  if resp.status_code != 200:

    logging.error("Erro na req")

    return []

  if not data:
    logging.warning('Nenhum dado retornado')
    return []
  output_path = 'data/weather_data.json'

  output_dir = Path(output_path).parent

  output_dir.mkdir(parents=True, exist_ok=True)

  with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4)

  logging.info(f"Arquivo salvo em {output_path}")

  return data

