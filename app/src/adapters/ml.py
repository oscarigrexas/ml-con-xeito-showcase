import json
import os
from random import randint

import pandas as pd
import requests


class FakeMLAdapter:
    def get_prediction(self, input_data: pd.DataFrame) -> int:
        return randint(0, 1)


class MLFlowMLAdapter:
    def __init__(self, model_server_uri: str):
        self.model_server_uri = model_server_uri

    def get_prediction(self, input_data: pd.DataFrame) -> int:
        payload = json.dumps({"dataframe_split": input_data.to_dict(orient="split")})
        response = requests.post(
            url=self.model_server_uri,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        prediction = response.json()["predictions"][0]
        return prediction
