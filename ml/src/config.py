import os

from omegaconf import OmegaConf

import mlflow

config = OmegaConf.load("conf/config.yml")

mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
mlflow.set_experiment(config.experiment_name)
