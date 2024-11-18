from datetime import datetime
from io import BytesIO, StringIO
from typing import Any, Dict, List, Literal

import boto3
import pandas as pd
from pydantic import BaseModel


class FieldsField(BaseModel):
    name: str | int
    type: str


class SchemaField(BaseModel):
    fields: List[FieldsField]
    primaryKey: List[str]
    pandas_version: str


class DFDataItem(BaseModel):
    schema: SchemaField
    data: List[Dict[str, Any]]


class S3CSVRepository:
    def __init__(
        self,
        bucket: str,
        prefix: str,
        endpoint: str,
        credentials: dict[str, str],
        region_name: str = "",
    ):
        self.bucket = bucket
        self.prefix = prefix
        self.endpoint = endpoint
        self.region_name = region_name
        self.s3_session = boto3.Session(**credentials)
        self.s3_client = self.s3_session.client(
            "s3",
            endpoint_url=endpoint,
            region_name=region_name,
        )

    def _load_csv_from_minio(self, bucket_name: str, file_key: str):
        response = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)
        df = pd.read_csv(
            BytesIO(response["Body"].read()),
            encoding="utf-8",
        )
        return df

    def _load_csv_from_minio_prefix(self, bucket_name: str, prefix: str):
        s3 = self.s3_session.resource(
            "s3",
            endpoint_url=self.endpoint,
            region_name=self.region_name,
        )
        bucket = s3.Bucket(bucket_name)
        prefix_objs = bucket.objects.filter(Prefix=prefix)
        prefix_df = []
        for obj in prefix_objs:
            df = pd.read_csv(BytesIO(obj.get()["Body"].read()), encoding="utf-8")
            prefix_df.append(df)
        merged_df = pd.concat(prefix_df)
        return merged_df

    def load_all(self) -> pd.DataFrame:
        return self._load_csv_from_minio_prefix(
            bucket_name=self.bucket, prefix=self.prefix
        )

    def append(self, data: pd.DataFrame) -> None:
        location = f"s3://{self.bucket}/{self.prefix}/data.csv"
        storage_options = {"client_kwargs": {"endpoint_url": self.endpoint}}
        data.to_csv(location, index=False, storage_options=storage_options)

    def overwrite(self, data: pd.DataFrame) -> None:
        location = f"s3://{self.bucket}/{self.prefix}/{datetime.now().isoformat()}.csv"
        storage_options = {"client_kwargs": {"endpoint_url": self.endpoint}}
        data.to_csv(location, index=False, storage_options=storage_options)

    def add(self, item: DFDataItem, mode: Literal["append", "overwrite"]) -> None:
        new_data = pd.read_json(StringIO(item.model_dump_json()), orient="table")
        if mode == "append":
            self.append(data=new_data)
        elif mode == "overwrite":
            self.overwrite(data=new_data)
