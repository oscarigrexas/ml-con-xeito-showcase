import os
from io import BytesIO

import boto3
import pandas as pd

s3_client = boto3.client(
    "s3",
    endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="",
)


def load_csv_from_minio(bucket_name: str, file_key: str):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    df = pd.read_csv(
        BytesIO(response["Body"].read()), encoding="utf-8", compression="gzip"
    )
    return df
