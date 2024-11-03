from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
import plotly.express as px
from loguru import logger
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from config import config


def plot_target_histograms(y_test, y_pred):
    combined_df = pd.DataFrame(
        dict(
            series=["test"] * len(y_test) + ["pred"] * len(y_pred),
            data=np.concatenate([y_test, y_pred]),
        )
    )
    histogram = px.histogram(combined_df, x="data", color="series", barmode="overlay")
    return histogram


if __name__ == "__main__":
    df = pd.read_csv(Path(config.data_filepath, "preprocessed_data.csv"))

    X, y = df.drop(config.target_column, axis=1), df[config.target_column]

    X_train, X_test, y_train, y_test = train_test_split(X, y)

    logger.info("Training model...")
    logger.info(f"Using params {config.estimator_params}")
    model = Pipeline(
        [
            ("scaler", MinMaxScaler()),
            ("estimator", MLPRegressor(**config.estimator_params)),
        ]
    )
    model.fit(X=X_train, y=y_train)
    loss_history = model["estimator"].loss_curve_
    logger.info("Model has been trained!")

    logger.info("Evaluating model...")
    y_pred = model.predict(X=X_test)
    metrics = {
        "r2": r2_score(y_true=y_test, y_pred=y_pred),
        "final_training_loss": loss_history[-1],
    }
    logger.info(f"Test metrics: {metrics}")

    histogram = plot_target_histograms(y_test=y_test, y_pred=y_pred)
    histogram_file_path = Path(config.data_filepath, "histogram.html")

    model_signature = mlflow.models.infer_signature(
        model_input=X_train, model_output=y_pred
    )

    with mlflow.start_run():
        mlflow.log_params(params=config.estimator_params)
        mlflow.log_metrics(metrics=metrics)
        for step, value in enumerate(loss_history):
            mlflow.log_metric(key="Training loss history", value=value, step=step)
        mlflow.log_figure(figure=histogram, artifact_file=histogram_file_path)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="mlp-housing",
            signature=model_signature,
        )
