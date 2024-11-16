import os

import numpy as np
import pandas as pd
import streamlit as st

from src.adapters.data import get_current_data, get_recent_data
from src.adapters.ml import MLFlowMLAdapter

st.title("Will I be sick tomorrow?")

col_1, col_2 = st.columns(2)

col_1.header("Recent air quality")

chart_data = get_recent_data()

col_1.line_chart(chart_data)

col_2.header("Current values")

current_data = get_current_data(recent_hourly_dataframe=chart_data)

custom_current_data = col_2.data_editor(current_data)

st.header("Sickness prediction")

ml_adapter = MLFlowMLAdapter(model_server_uri=os.environ["INFERENCE_SERVER_URI"])


if st.button(
    label="# Predict",
    use_container_width=True,
):
    col_3, col_4 = st.columns(2)
    prediction = ml_adapter.get_prediction(input_data=custom_current_data.to_frame().T)
    if prediction == 1:
        image = "src/images/bad.gif"
        header = "**YOU DIED**"
        caption = "You're gonna be ultra-sick."
    else:
        image = "src/images/good.png"
        header = "**You may live another day**"
        caption = "It's gonna be fine."
    col_3.image(image, use_column_width=True)
    col_4.markdown(header)
    col_4.markdown(caption)
    col_4.markdown(f"Prediction value: {prediction}")
