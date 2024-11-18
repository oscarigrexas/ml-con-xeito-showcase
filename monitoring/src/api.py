import os

import uvicorn
from data import DFDataItem, S3CSVRepository
from fastapi import FastAPI

app = FastAPI()


s3_credentials = {
    "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
    "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
}
region_name = ""
endpoint = os.environ["MLFLOW_S3_ENDPOINT_URL"]

reference_repository = S3CSVRepository(
    bucket="elt-data",
    prefix="data_collection/reference_data",
    endpoint=endpoint,
    region_name=region_name,
    credentials=s3_credentials,
)
current_repository = S3CSVRepository(
    bucket="elt-data",
    prefix="data_collection/current_data",
    endpoint=endpoint,
    region_name=region_name,
    credentials=s3_credentials,
)


@app.post("/reference_data")
def upload_reference_data(data_item: DFDataItem):
    reference_repository.add(item=data_item, mode="overwrite")
    return {"message": "Reference data stored successfully"}


@app.post("/current_data")
def upload_current_data(data_item: DFDataItem):
    current_repository.add(item=data_item, mode="append")
    return {"message": "Current data appended successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4300)
