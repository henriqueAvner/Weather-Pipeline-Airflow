
import logging

def setup_logger():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            # %(asctime)s
            # → data/hora

            # %(levelname)s
            # → INFO / WARNING / ERROR

            # %(message)s
            # → sua mensagem
  ) 
