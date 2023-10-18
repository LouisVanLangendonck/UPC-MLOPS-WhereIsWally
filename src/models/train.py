"""Module that trains the model """
import os
import pickle
from getpass import getpass
from pathlib import Path
import mlflow
from ultralytics import YOLO
import yaml
from codecarbon import EmissionsTracker
import pandas as pd

# os.environ['MLFLOW_TRACKING_USERNAME'] = input('Enter your DAGsHub username: ')
os.environ['MLFLOW_TRACKING_USERNAME'] = LouisVanLangendonck
# os.environ['MLFLOW_TRACKING_PASSWORD'] = input('Enter your DAGsHub access token: ')
os.environ['MLFLOW_TRACKING_PASSWORD'] = input('Enter your DAGsHub access token: ')
os.environ['MLFLOW_TRACKING_URI'] = input('Enter your DAGsHub project tracking URI: ')

mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])


EMISSIONS_OUTPUT_FOLDER = '../../metrics'
MODELS_OUTPUT_FOLDER = '../../models'

with open(r"params.yaml", encoding='utf-8') as f:
    params = yaml.safe_load(f)

# Load the model.
model = YOLO(params['model_type'])

# Training.
mlflow.set_experiment(params['name'])
with mlflow.start_run():
    with EmissionsTracker(
            output_dir=EMISSIONS_OUTPUT_FOLDER,
            output_file="emissions.csv",
            on_csv_write="update",
    ):
        results = model.train(
            data="../../data/raw/yolov8_format/data.yaml",
            imgsz=params['imgsz'],
            epochs=params['epochs'],
            batch=params['batch'],
            name=params['name'])

    # Log the CO2 emissions to MLflow
    emissions = pd.read_csv(EMISSIONS_OUTPUT_FOLDER / "emissions.csv")
    emissions_metrics = emissions.iloc[-1, 4:13].to_dict()
    emissions_params = emissions.iloc[-1, 13:].to_dict()
    mlflow.log_params(emissions_params)
    mlflow.log_metrics(emissions_metrics)

    # Save the model as a pickle file
    Path("models").mkdir(exist_ok=True)

    with open(MODELS_OUTPUT_FOLDER / "yolov8_model.pkl", "wb") as pickle_file:
        pickle.dump(results, pickle_file)
