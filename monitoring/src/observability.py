import os
from datetime import datetime

from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from prefect import flow
from src.api import current_repository, reference_repository

import mlflow

mlflow.set_tracking_uri(os.environ["MLFLOW_REGISTRY_URI"])
mlflow.set_experiment("observability")


@flow(log_prints=True)
def run_ml_monitoring_experiment():
    report = Report(
        metrics=[
            DataDriftPreset(),
        ]
    )

    current_data = current_repository.load_all()
    reference_data = reference_repository.load_all()

    print("Current data")
    print(current_data.head())
    print(current_data.columns)

    print("Reference data")
    print(reference_data.head())
    print(reference_data.columns)

    report.run(
        current_data=current_data,
        reference_data=reference_data,
        column_mapping=None,
    )
    results = report.as_dict()
    print(results)

    with mlflow.start_run():
        mlflow.log_param("current_data_start_datetime", current_data.index.min())
        mlflow.log_param("current_data_end_datetime", current_data.index.max())
        mlflow.log_param("report_timestamp", datetime.now().isoformat())
        mlflow.log_metric(
            "number_of_drifted_columns",
            results["metrics"][0]["result"]["number_of_drifted_columns"],
        )
        mlflow.log_metric(
            "general_dataset_drift_detected",
            results["metrics"][1]["result"]["dataset_drift"],
        )
        for feature, feature_results in results["metrics"][1]["result"][
            "drift_by_columns"
        ].items():
            mlflow.log_metric(
                f"feature_{feature}_drift_detected", feature_results["drift_detected"]
            )
            mlflow.log_metric(
                f"feature_{feature}_drift_score", feature_results["drift_score"]
            )
