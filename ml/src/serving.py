import mlflow
import pandas as pd
import uvicorn
from config import config
from fastapi import FastAPI
from loguru import logger

app = FastAPI()


@app.get("/health")
async def health():
    return {"message": "Server is up!"}


@app.post("/infer")
async def infer(inference_data: dict[str, list[dict]]):
    model = mlflow.sklearn.load_model("models:/mlp-housing/1")

    inference_data = inference_data["instances"]
    logger.info(f"Input data: {inference_data}")
    logger.info("Running inference...")

    X_infer = pd.DataFrame.from_dict(inference_data)
    y_pred = model.predict(X=X_infer)

    logger.info(f"Predictions: {y_pred}")

    return {"predictions": list(y_pred)}


if __name__ == "__main__":
    uvicorn.run("serving:app", port=1234, reload=True)
