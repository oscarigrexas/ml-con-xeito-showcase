from omegaconf import OmegaConf

import mlflow

config = OmegaConf.load("conf/config.yml")

mlflow.set_tracking_uri(config.mlflow_uri)
mlflow.set_experiment(config.experiment_name)
