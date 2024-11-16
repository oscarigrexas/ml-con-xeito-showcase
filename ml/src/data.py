import os
from io import BytesIO

import boto3
import pandas as pd

s3_session = boto3.Session(
    aws_access_key_id=os.environ["ELT_AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["ELT_AWS_SECRET_ACCESS_KEY"],
)

s3_client = s3_session.client(
    "s3",
    endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"],
    region_name="",
)


def load_csv_from_minio(bucket_name: str, file_key: str):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    df = pd.read_csv(
        BytesIO(response["Body"].read()), encoding="utf-8", compression="gzip"
    )
    return df


def load_csv_from_minio_prefix(bucket_name: str, prefix: str):
    s3 = s3_session.resource(
        "s3",
        endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"],
        region_name="",
    )
    bucket = s3.Bucket(bucket_name)
    prefix_objs = bucket.objects.filter(Prefix=prefix)
    prefix_df = []
    for obj in prefix_objs:
        df = pd.read_csv(
            BytesIO(obj.get()["Body"].read()), encoding="utf-8", compression="gzip"
        )
        prefix_df.append(df)
    merged_df = pd.concat(prefix_df)
    return merged_df[~merged_df.index.duplicated(keep="first")]


if __name__ == "__main__":
    data = load_csv_from_minio_prefix(
        bucket_name="elt-data", prefix="rest_api_data/air_quality/"
    )
    print(data.head())
    print(data.shape)
