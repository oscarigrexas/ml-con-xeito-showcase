from pathlib import Path

import pandas as pd
from loguru import logger

from config import config

if __name__ == "__main__":
    df = pd.read_csv(Path(config.data_filepath, "raw_data.csv"))

    logger.info("Preprocessing data...")
    df = df.drop_duplicates()
    df = df.dropna()

    df.to_csv(Path(config.data_filepath, "preprocessed_data.csv"), index=False)
