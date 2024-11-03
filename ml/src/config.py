import os

import mlflow
from omegaconf import OmegaConf

config = OmegaConf.load("conf/config.yml")

mlflow.set_tracking_uri(config.mlflow_uri)
mlflow.set_experiment(config.experiment_name)

os.environ["AWS_ACCESS_KEY_ID"] = config.minio_user
os.environ["AWS_SECRET_ACCESS_KEY"] = config.minio_password
os.environ["MLFLOW_S3_ENDPOINT_URL"] = config.minio_uri
