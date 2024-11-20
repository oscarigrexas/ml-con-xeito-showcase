import os

import pandas as pd
import requests
from config import config
from prefect import flow
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import mlflow
from src.data import load_csv_from_minio_prefix


def log_reference_data(reference_data: pd.DataFrame):
    r = requests.post(
        f"{os.environ['DATA_COLLECTOR_URI']}/reference_data",
        data=reference_data.to_json(orient="table"),
    )
    if r.status_code == 500:
        raise Exception("Data collection error!")


@flow(log_prints=True)
def train_model():
    raw_df = load_csv_from_minio_prefix(
        bucket_name=config.bucket_name, prefix=config.training_data_folder
    )
    raw_df = raw_df.set_index("time", drop=True)
    raw_df.index = pd.to_datetime(raw_df.index)
    raw_df = raw_df.drop(["_dlt_load_id", "_dlt_id"], axis=1)
    raw_df = raw_df.resample("1d").max()
    target_df = raw_df[["is_sick"]]
    feature_df = raw_df[config.features]

    print("Logging training data as reference for ML observability")
    log_reference_data(reference_data=feature_df)

    print(f"Using features: {config.features}")

    X, y = feature_df, target_df

    X = X.shift(1).iloc[1:-1]
    y = y.iloc[1:-1]

    print(X.head())
    print(y.head())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, stratify=y["is_sick"]
    )

    print("Training model...")
    print(f"Using params {config.estimator_params}")
    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("estimator", GradientBoostingClassifier(**config.estimator_params)),
        ]
    )

    mlflow.autolog()
    with mlflow.start_run():
        model.fit(X=X_train, y=y_train)
        print("Model has been trained!")

        print("Evaluating model...")
        y_pred = model.predict(X=X_test)
        metrics = {
            "precision": precision_score(y_true=y_test, y_pred=y_pred),
            "recall": recall_score(y_true=y_test, y_pred=y_pred),
            "accuracy": accuracy_score(y_true=y_test, y_pred=y_pred),
        }
        print(f"Test metrics: {metrics}")

        model_signature = mlflow.models.infer_signature(
            model_input=X_train, model_output=y_pred
        )

        mlflow.log_metrics(metrics=metrics)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="air_quality_sickness_classifier",
            signature=model_signature,
        )
