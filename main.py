import numpy as np
import logging
from datetime import datetime
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from utils import load_and_prepare_datasets, run_training_pipeline, setup_logging
import time


# Profundidades a iterar
depth = "in_0_1" # in_0_1, in_1_2, in_2_3, in_3_4
n_trials_optuna = 75
input_file_seeds = "input_file_seeds.txt"
output_file_seeds = "output_file_seeds.txt"

log_filename = f"training_logs/training_{depth}.log"
setup_logging(log_filename)

models = {
    "XGB": XGBRegressor,
    "LBM": LGBMRegressor,
    "MLP": MLPRegressor,
    "SVR": SVR,
    "KNN": KNeighborsRegressor,
    "LR": LinearRegression,
    "RF": RandomForestRegressor,
    "CAT": CatBoostRegressor,
    "ELN": ElasticNet
}



logging.info(f"Profundidad a procesar: {depth}")
logging.info(f"Número de trials por modelo: {n_trials_optuna}\n")
logging.info(f"\n{'*'*80}")
logging.info(f"DEPTH: {depth}")
logging.info(f"{'*'*80}\n")
dfs = load_and_prepare_datasets(
    depth=depth
)

with open(input_file_seeds, "r") as inputfile:
    lines = inputfile.readlines()
# 2. Ejecutar pipeline para cada seed
for seed in lines:
    seed_int = int(seed.strip())
    seeds = [seed_int]
    run_training_pipeline(
        dfs=dfs,
        models=models,
        seeds=seeds,
        n_trials=n_trials_optuna,
        depth=depth,
        test_size=0.20
    )
    with open(output_file_seeds, "a") as outp:
        outp.write(seed)
    with open(input_file_seeds, "w") as inputfile:
        inputfile.writelines(lines[1:])
    lines = lines[1:]
