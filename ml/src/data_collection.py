from pathlib import Path

from loguru import logger
from sklearn.datasets import fetch_california_housing

from config import config

if __name__ == "__main__":
    logger.info("Fetching raw data from source...")

    data = fetch_california_housing(as_frame=True).frame
    data.to_csv(Path(config.data_filepath, "raw_data.csv"), index=False)
