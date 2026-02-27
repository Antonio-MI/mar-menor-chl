import pandas as pd
import os
import numpy as np
import logging
import sys
from datetime import datetime
pd.options.mode.chained_assignment = None
import optuna
from sklearn.metrics import r2_score, mean_squared_error, mean_squared_log_error
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import RobustScaler
import pickle
import json


#=================================================
# CONFIGURACIÓN DE LOGGING
#=================================================
def setup_logging(log_filename):
    """
    Configura logging para escribir tanto a consola como a archivo.
    
    Args:
        log_filename: Ruta al archivo de log
    """
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    
    # Configurar formato
    log_format = '%(message)s'
    
    # Configurar handlers
    handlers = [
        logging.FileHandler(log_filename, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers,
        force=True
    )
    
    logging.info(f"Log iniciado: {log_filename}")
    logging.info(f"="*70)

#=================================================
# FUNCIÓN PARA CARGAR Y PREPARAR DATASETS
#=================================================
def load_and_prepare_datasets(depth, path="saved_files/dataset"):
    """
    Carga y prepara dataframes para una profundidad específica.
    
    Args:
        depth: Profundidad (ej: "in_0_1", "in_1_2")
        datasets_to_keep: Lista de nombres de datasets a mantener (opcional) - Puesto a mano dentro de la función
        path: Ruta al directorio con los archivos CSV
    
    Returns:
        dict: Diccionario {nombre_dataset: dataframe_preparado}
    """
    # Cargamos los csv de los tifs
    dfs = {}
    for archivo in os.listdir(path):
        if archivo.endswith(f"{depth}_features.csv"):
            nombre_sin_extension = os.path.splitext(archivo)[0]  # sin .csv
            ruta_completa = os.path.join(path, archivo)
            dfs[nombre_sin_extension[:-9]] = pd.read_csv(ruta_completa)
    
    # Limpiamos valores nulos
    for nombre_df, df in dfs.items():
        for band_set in ["rhow", "rhown", "rtoa"]:
            dfs[nombre_df] = df.dropna()
    
    # Filtrar datasets si se especifica
    datasets_to_keep = [
		'C2X-Complex_rhow_9x9_depth_in_0_1', 
		'TOA_15x15_depth_in_0_1',
		'C2X-Complex_rhown_9x9_depth_in_0_1',
		'C2X-Complex_rhow_5x5_depth_in_0_1',
		'C2RCC_rhow_5x5_depth_in_0_1',
		'C2RCC_rhow_15x15_depth_in_0_1', 
		'C2X-Complex_rhown_15x15_depth_in_0_1',
		'C2RCC_rhown_5x5_depth_in_0_1', 
		'C2X-Complex_rhow_15x15_depth_in_0_1',
		'C2RCC_rhow_9x9_depth_in_0_1',
		'C2X-Complex_rhow_5x5_depth_in_1_2', 
		'C2X_rhow_3x3_depth_in_1_2',
		'C2X-Complex_rhown_5x5_depth_in_1_2',
		'C2X-Complex_rhow_9x9_depth_in_1_2',
		'C2X-Complex_rhow_3x3_depth_in_1_2',
		'C2X-Complex_rhown_3x3_depth_in_1_2',
		'C2RCC_rhown_3x3_depth_in_1_2',
		'C2X-Complex_rhown_9x9_depth_in_1_2',
		'C2X-Complex_rhow_15x15_depth_in_1_2', 
		'C2X_rhow_5x5_depth_in_1_2',
        'TOA_15x15_depth_in_2_3',
		'TOA_9x9_depth_in_2_3',
		'TOA_5x5_depth_in_2_3', 
		'C2X-Complex_rhow_5x5_depth_in_2_3',
		'C2RCC_rhown_5x5_depth_in_2_3', 
		'TOA_3x3_depth_in_2_3',
		'C2X-Complex_rhown_5x5_depth_in_2_3', 
		'C2RCC_rhow_3x3_depth_in_2_3',
		'C2X-Complex_rhown_9x9_depth_in_2_3', 
		'C2X_rhow_9x9_depth_in_2_3',
        'TOA_9x9_depth_in_3_4',
		'TOA_3x3_depth_in_3_4',
		'TOA_5x5_depth_in_3_4',
		'C2X-Complex_rhow_5x5_depth_in_3_4', 
		'TOA_1x1_depth_in_3_4',
		'TOA_15x15_depth_in_3_4',
		'C2X-Complex_rhown_5x5_depth_in_3_4',
		'C2X-Complex_rhow_9x9_depth_in_3_4',
		'C2X-Complex_rhow_15x15_depth_in_3_4',
		'C2X-Complex_rhown_9x9_depth_in_3_4'
        ]

    if datasets_to_keep is not None:
        dfs = {k: dfs[k] for k in datasets_to_keep if k in dfs}
    
    # Procesamiento de cada dataframe
    for nombre_df, df in dfs.items():
        # HIGH_CHL REDEFINIDA
        # Marcamos las columnas de Chl alta (equivalente a quantile(0.9))
        threshold = df["Chl"].quantile(0.9)
        df["High_Chl"] = df["Chl"] > threshold
        
        # Sacamos la estación de cada fecha
        df['Date'] = pd.to_datetime(df['Date'])
        
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Invierno'
            elif month in [3, 4, 5]:
                return 'Primavera'
            elif month in [6, 7, 8]:
                return 'Verano'
            else:
                return 'Otoño'
        
        df['Season'] = df['Date'].dt.month.apply(get_season)
        
        # Convertir a categorías y hacer one-hot encoding
        for col in df.select_dtypes(include=['object', 'string']).columns:
            df[col] = df[col].astype('category')
        
        df = pd.concat([df.drop(columns=["Season"]), pd.get_dummies(df["Season"])], axis=1)
        dfs[nombre_df] = df
    
    return dfs

#=================================================
# FUNCIÓN OBJETIVO DE OPTUNA
#=================================================
def objective(trial, df, nombre_df, target, model_name, seed, models, hyperparams_path="hyperparams.json"):
    """
    Función objetivo para optimización de hiperparámetros con Optuna.
    
    Args:
        trial: Trial de Optuna
        df: DataFrame de entrenamiento (ya sin test split)
        nombre_df: Nombre del dataset
        target: Variable objetivo (ej: "Chl")
        model_name: Nombre del modelo a optimizar
        seed: Semilla aleatoria
        models: Diccionario con clases de modelos
        hyperparams_path: Ruta al archivo JSON con hiperparámetros
    
    Returns:
        tuple: (rmsle_mean, r2_mean)
    """
    # Configuración
    FOLDS = 4
    correct = True  # Para hacer clip a las predicciones y forzar > 0
    results = {}
    
    # Cargar configuración de hiperparámetros desde JSON
    with open(hyperparams_path, 'r') as f:
        config = json.load(f)[model_name]
    
    scale_values = config.get('scale_values', False)
    param_config = config['params']
    
    # Preparar datos (eliminar columnas no features)
    df_work = df.iloc[:, 4:].copy()  # Eliminar Date, Lat, Lon, Buoy
    
    # Separar features y target
    X = df_work.drop(columns=[target, "High_Chl", "Turbidez"])
    y = df_work[target]
    y_class = df_work["High_Chl"]  # Para StratifiedKFold
    
    # Construir parámetros para el trial
    params = {}

    # Mapeo especial para hidden_layer_sizes (MLP)
    hidden_options = {
        '32': (32,),
        '64': (64,),
        '32_16': (32, 16),
        '32_16_8': (32, 16, 8)
    }
    
    for param_name, param_spec in param_config.items():
        if isinstance(param_spec, dict) and 'type' in param_spec:
            param_type = param_spec['type']
            
            if param_type == 'categorical':
                choices = param_spec['choices']
                # Manejar listas de listas para hidden_layer_sizes
                # if param_name == 'hidden_layer_sizes':
                #     choices_tuples = [tuple(c) if isinstance(c, list) else c for c in choices]
                #     params[param_name] = trial.suggest_categorical(param_name, choices_tuples)
                if param_name == 'hidden_layer_sizes':
                    choice_key = trial.suggest_categorical(param_name, list(hidden_options.keys()))
                    params[param_name] = hidden_options[choice_key]
                else:
                    params[param_name] = trial.suggest_categorical(param_name, choices)
            
            elif param_type == 'int':
                params[param_name] = trial.suggest_int(param_name, param_spec['low'], param_spec['high'])
            
            elif param_type == 'float':
                log_scale = param_spec.get('log', False)
                params[param_name] = trial.suggest_float(
                    param_name, 
                    param_spec['low'], 
                    param_spec['high'], 
                    log=log_scale
                )
        else:
            # Parámetros fijos (no optimizables)
            params[param_name] = param_spec
    
    # Inicializar modelo con parámetros
    model = models[model_name](**params)
    
    # Dicts para guardar resultados de validación cruzada
    val_preds = np.zeros(len(X))
    results[nombre_df] = {model_name: {'RMSLE': [], 'R2': []}}
    
    # Stratified K-Fold
    skf = StratifiedKFold(n_splits=FOLDS, shuffle=True, random_state=seed)
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y_class)):
        #print(f"Fold {fold+1}")
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        if scale_values:
            # Escalar datos para modelos basados en distancias
            scaler_X = RobustScaler()
            scaler_y = RobustScaler()
            
            X_train_scaled = scaler_X.fit_transform(X_train)
            X_val_scaled = scaler_X.transform(X_val)
            y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()
            
            model.fit(X_train_scaled, y_train_scaled)
            val_pred = scaler_y.inverse_transform(model.predict(X_val_scaled).reshape(-1, 1)).ravel()
        else:
            # Fit directo sin scaling
            model.fit(X_train, y_train)
            val_pred = model.predict(X_val)
        
        if correct:
            # Clip para forzar predicciones > 0.2
            val_pred = np.clip(val_pred, 0.2, None)
        
        # Guardar predicciones
        val_preds[val_idx] = val_pred
        
        # Calcular métricas
        rmsle = np.sqrt(mean_squared_log_error(y_val, val_pred))
        r2 = r2_score(y_val, val_pred)
        
        results[nombre_df][model_name]['RMSLE'].append(rmsle)
        results[nombre_df][model_name]['R2'].append(r2)
    
    # Retornar promedios de las métricas
    rmsle_mean = np.mean(results[nombre_df][model_name]["RMSLE"])
    r2_mean = np.mean(results[nombre_df][model_name]["R2"])
    
    return rmsle_mean, r2_mean

#=================================================
# FUNCIÓN PARA EJECUTAR OPTUNA
#=================================================
def run_optuna(df, nombre_df, target, n_trials, model_name, seed, models):
    """
    Ejecuta optimización de hiperparámetros con Optuna (multi-objetivo).
    
    Args:
        df: DataFrame de entrenamiento
        nombre_df: Nombre del dataset
        target: Variable objetivo (ej: "Chl")
        n_trials: Número de trials para optimización
        model_name: Nombre del modelo
        seed: Semilla aleatoria
    
    Returns:
        dict: Diccionario con best_params, best_rmsle y best_r2
    """
    results = {}
    
    logging.info(f"Buscando mejores hiperparámetros para {model_name} con {nombre_df}...")
    
    # Multi-objective study: minimizar RMSLE, maximizar R2
    study = optuna.create_study(directions=['minimize', 'maximize'],
                                sampler=optuna.samplers.TPESampler(constant_liar=True, n_startup_trials=8))
    
    # Optimizar
    study.optimize(
        lambda trial: objective(trial, df, nombre_df, target, model_name, seed, models),
        n_trials=n_trials,
        n_jobs=8
    )
    

    # En optimización multi-objetivo, no hay un único "best":
    # Optuna mantiene un frente de Pareto de soluciones no dominadas.
    # Ninguna de ellas es estrictamente mejor que las demás en AMBAS métricas.
    # La selección de best_trials[0] no nos garantiza que el resultado se óptimo puesto que no hay orden.
    #
    # Estrategia de selección:
    #   1. Tomamos todos los trials del frente de Pareto (study.best_trials).
    #   2. Normalizamos RMSLE y R² al rango [0, 1] para hacerlos comparables.
    #   3. Calculamos un score combinado: 65% RMSLE normalizado + 35% (1 - R² normalizado).
    #      El factor (1 - r2_norm) invierte R² para que menor score = mejor R².
    #   4. Seleccionamos el trial con el score combinado más bajo.
    #
    # Si solo hay 1 trial en el frente (o ninguno), se usa directamente ese.
    pareto_trials = study.best_trials if study.best_trials else study.trials

    if len(pareto_trials) > 1:
        rmsle_vals = np.array([t.values[0] for t in pareto_trials])
        r2_vals    = np.array([t.values[1] for t in pareto_trials])

        # Normalización min-max (+ 1e-9 para evitar división por cero)
        rmsle_norm = (rmsle_vals - rmsle_vals.min()) / (rmsle_vals.max() - rmsle_vals.min() + 1e-9)
        r2_norm    = 1 - (r2_vals - r2_vals.min()) / (r2_vals.max() - r2_vals.min() + 1e-9)

        # Score combinado: minimizar para mejor trial (arbitrario también, pero acorde a lo que se hace para seleccionar modelos posteriormente)
        score = 0.65 * rmsle_norm + 0.35 * r2_norm

        # Trial seleccionado: el de menor score combinado del frente de Pareto
        best_trial = pareto_trials[int(np.argmin(score))]
    else:
        # Un único trial no dominado (o fallback si best_trials está vacío)
        best_trial = pareto_trials[0]
    
    rmsle_val = best_trial.values[0]
    r2_val = best_trial.values[1]
    
    logging.info(f"\n✅ {model_name} con {nombre_df}")
    # logging.info(f"   RMSLE: {rmsle_val:.3f}")
    # logging.info(f"   R2: {r2_val:.3f}")
    logging.info(f"📋 Parámetros: {best_trial.params}\n")
    
    results[model_name] = {
        'best_params': best_trial.params,
        'best_rmsle': np.round(rmsle_val, 3),
        'best_r2': np.round(r2_val, 3)
    }
    
    return results

#=================================================
# ENTRENAMIENTO CON LOS HIPERPARAMETROS OPTIMIZADOS
#=================================================
def train_final_model(X_train, y_train, model_name, params, models):
    """
    Entrena modelo final con mejores hiperparámetros.
    Combina parámetros optimizados con parámetros fijos del JSON.
    """
    # Cargar configuración
    with open("hyperparams.json", 'r') as f:
        config = json.load(f)[model_name]
    
    scale_values = config.get('scale_values', False)
    param_config = config['params']
    
    # Construir parámetros finales: empezar con parámetros fijos del JSON
    final_params = {}
    
    # Añadir parámetros fijos (no optimizables)
    for param_name, param_spec in param_config.items():
        if not isinstance(param_spec, dict) or 'type' not in param_spec:
            # Parámetro fijo (como n_jobs, random_state, etc.)
            final_params[param_name] = param_spec
    
    # Sobrescribir con parámetros optimizados por Optuna
    final_params.update(params)

    # Mapeo especial para hidden_layer_sizes (MLP)
    if model_name == "MLP" and 'hidden_layer_sizes' in final_params:
        hidden_options = {
            '32': (32,),
            '64': (64,),
            '32_16': (32, 16),
            '32_16_8': (32, 16, 8)
        }
        final_params['hidden_layer_sizes'] = hidden_options[final_params['hidden_layer_sizes']]
    
    # Crear modelo con parámetros combinados
    model = models[model_name](**final_params)
    
    # Entrenar
    if scale_values:
        scaler_X = RobustScaler()
        scaler_y = RobustScaler()
        X_scaled = scaler_X.fit_transform(X_train)
        y_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()
        model.fit(X_scaled, y_scaled)
        model.scaler_X = scaler_X
        model.scaler_y = scaler_y
    else:
        model.fit(X_train, y_train)
    
    model.scale_values = scale_values
    return model    

#=================================================
# PREDICCIONES PARA DATOS ESCALADOS
#=================================================
def predict_with_scaling(model, X):
    """Hacer predicciones teniendo en cuenta si se usó scaling"""
    if model.scale_values:
        X_scaled = model.scaler_X.transform(X)
        pred_scaled = model.predict(X_scaled)
        pred = model.scaler_y.inverse_transform(pred_scaled.reshape(-1, 1)).ravel()
    else:
        pred = model.predict(X)
    return pred

#=================================================
# PREDICCIONES DEL ENSEMBLE
#=================================================
def compute_ensemble_predictions(all_train_predictions, all_test_predictions, 
                                  y_train_full, y_test, nombre_df):
    """
    Calcula predicciones y métricas del ensemble (media de modelos).
    
    Args:
        all_train_predictions: Dict {model_name: predictions_train}
        all_test_predictions: Dict {model_name: predictions_test}
        y_train_full: Series con valores reales de train
        y_test: Series con valores reales de test
        nombre_df: Nombre del dataset
    
    Returns:
        tuple: (ensemble_key, ensemble_results_dict)
    """
    if len(all_train_predictions) == 0:
        return None, None
    
    logging.info(f"\n✅   Modelo: ENSEMBLE con {nombre_df}")
    
    # Predicciones ensemble en train
    ensemble_train_pred = np.mean(
        list(all_train_predictions.values()), 
        axis=0
    )
    ensemble_train_pred = np.clip(ensemble_train_pred, 0.2, None)
    
    # Predicciones ensemble en test
    ensemble_test_pred = np.mean(
        list(all_test_predictions.values()), 
        axis=0
    )
    ensemble_test_pred = np.clip(ensemble_test_pred, 0.2, None)
    
    # Métricas ensemble train
    ensemble_train_metrics = {
        'RMSLE': np.sqrt(mean_squared_log_error(y_train_full, ensemble_train_pred)),
        'RMSE': np.sqrt(mean_squared_error(y_train_full, ensemble_train_pred)),
        'R2': r2_score(y_train_full, ensemble_train_pred)
    }
    
    # Métricas ensemble test
    ensemble_test_metrics = {
        'RMSLE': np.sqrt(mean_squared_log_error(y_test, ensemble_test_pred)),
        'RMSE': np.sqrt(mean_squared_error(y_test, ensemble_test_pred)),
        'R2': r2_score(y_test, ensemble_test_pred)
    }
    
    # Preparar resultados
    ensemble_key = (nombre_df, "ENSEMBLE")
    ensemble_results = {
        'best_params': {
            'ensemble_type': 'mean',
            'models_used': list(all_train_predictions.keys())
        },
        'train_metrics': ensemble_train_metrics,
        'test_metrics': ensemble_test_metrics,
        'train_predictions': ensemble_train_pred,
        'test_predictions': ensemble_test_pred,
        'train_y_true': y_train_full.values,
        'test_y_true': y_test.values
    }
    
    logging.info(f"    Train - RMSLE: {ensemble_train_metrics['RMSLE']:.3f}, R2: {ensemble_train_metrics['R2']:.3f}")
    logging.info(f"    Test  - RMSLE: {ensemble_test_metrics['RMSLE']:.3f}, R2: {ensemble_test_metrics['R2']:.3f}")
    
    return ensemble_key, ensemble_results

#=================================================
# EJECUCION DEL PIPELINE COMPLETO
#=================================================
def run_training_pipeline(dfs, models, seeds, n_trials, depth, test_size):
    """
    Ejecuta el pipeline completo de entrenamiento multi-seed.
    
    Args:
        dfs: Dict de dataframes preparados
        models: Dict de clases de modelos {nombre: clase}
        seeds: Lista de seeds para train/test splits
        n_trials: Número de trials para Optuna
        depth: Profundidad (para nombres de archivos)
        test_size: Proporción del test set
    
    Returns:
        dict: global_results con todos los resultados por seed
    """

    # Crear directorio base
    os.makedirs("training_results", exist_ok=True)

    # global_results = {}

    for seed in seeds:
        seed_start_time = datetime.now()
        logging.info(f"\n{'='*60}")
        logging.info(f"SEED: {seed}")
        logging.info(f"Inicio: {seed_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"{'='*60}\n")
        seed_results = {}
        os.makedirs(f"training_results/depth_{depth}/seed{seed}", exist_ok=True)
        
        for nombre_df, df_full in list(dfs.items()):
            logging.info(f"\n--- Dataset: {nombre_df} ---")
            
            # Preparar datos
            df_work = df_full.iloc[:, 4:].copy()
            
            # Train/Test Split
            train_df, test_df = train_test_split(
                df_work, 
                test_size=test_size, 
                random_state=seed, 
                stratify=df_work["High_Chl"]
            )
            
            # Preparar train
            X_train_full = train_df.drop(columns=["Chl", "High_Chl", "Turbidez"])
            y_train_full = train_df["Chl"]
        
            # Preparar test
            X_test = test_df.drop(columns=["Chl", "High_Chl", "Turbidez"])
            y_test = test_df["Chl"]

            # Dict para predicciones del ensemble
            all_train_predictions = {}
            all_test_predictions = {}

            # ============================================================
            # LOOP: MODELOS INDIVIDUALES
            # ============================================================
            for model_name in models.keys():
                logging.info(f"\n  Modelo: {model_name}")
                key = (nombre_df, model_name)
                
                try:
                    # 1. Optimización de hiperparámetros
                    optuna_result = run_optuna(
                        train_df, nombre_df, "Chl", n_trials, model_name, seed, models
                    )
                    best_params = optuna_result[model_name]['best_params']
                    
                    # 2. Entrenar modelo final con mejores parámetros
                    model = train_final_model(
                        X_train_full, y_train_full, 
                        model_name, best_params, models
                    )
                    
                    # 3. Predicciones y métricas en TRAIN
                    y_train_pred = predict_with_scaling(
                        model, X_train_full
                    )
                    y_train_pred = np.clip(y_train_pred, 0.2, None)
                    
                    train_metrics = {
                        'RMSLE': np.sqrt(mean_squared_log_error(y_train_full, y_train_pred)),
                        'RMSE': np.sqrt(mean_squared_error(y_train_full, y_train_pred)),
                        'R2': r2_score(y_train_full, y_train_pred)
                    }
                    
                    # 4. Predicciones y métricas en TEST
                    y_test_pred = predict_with_scaling(
                        model, X_test
                    )
                    y_test_pred = np.clip(y_test_pred, 0.2, None)
                    
                    test_metrics = {
                        'RMSLE': np.sqrt(mean_squared_log_error(y_test, y_test_pred)),
                        'RMSE': np.sqrt(mean_squared_error(y_test, y_test_pred)),
                        'R2': r2_score(y_test, y_test_pred)
                    }

                    # Guardar predicciones para el ensemble
                    all_train_predictions[model_name] = y_train_pred
                    all_test_predictions[model_name] = y_test_pred
                    
                    # 5. Guardar resultados
                    seed_results[key] = {
                        'best_params': best_params,
                        'train_metrics': train_metrics,
                        'test_metrics': test_metrics,
                        'train_predictions': y_train_pred,
                        'test_predictions': y_test_pred,
                        'train_y_true': y_train_full.values,
                        'test_y_true': y_test.values
                    }
                    
                    logging.info(f"    Train - RMSLE: {train_metrics['RMSLE']:.3f}, R2: {train_metrics['R2']:.3f}")
                    logging.info(f"    Test  - RMSLE: {test_metrics['RMSLE']:.3f}, R2: {test_metrics['R2']:.3f}")
                except Exception as e:
                    logging.error(f"    ❌ Error: {e}")
                    continue

            # ============================================================
            # ENSEMBLE
            # ============================================================
            ensemble_key, ensemble_results = compute_ensemble_predictions(
                all_train_predictions, all_test_predictions,
                y_train_full, y_test, nombre_df
            )
            
            if ensemble_key is not None:
                seed_results[ensemble_key] = ensemble_results

        # Guardar resultados de esta seed
        #global_results[seed] = seed_results
        try:
            with open(f"training_results/depth_{depth}/seed{seed}/full_results_{depth}.pkl", "wb") as f:
                pickle.dump(seed_results, f)
            seed_end_time = datetime.now()
            seed_elapsed = seed_end_time - seed_start_time
            logging.info(f"\n✅ Resultados de seed {seed} guardados en training_results/seed{seed}/")
            logging.info(f"⏱️  Tiempo total para seed {seed}: {seed_elapsed} (Fin: {seed_end_time.strftime('%H:%M:%S')})")
        except Exception as e:
            logging.error(f"\n❌ Error al guardar resultados de seed {seed}: {e}")
        
        logging.info("------------------------------------------------------------------")
        logging.info("------------------------------------------------------------------")
        logging.info("------------------------------------------------------------------")

    # Guardar resultados globales consolidados
    # try:
    #     with open(f"training_results/depth_{depth}/global_results_{depth}.pkl", "wb") as f:
    #         pickle.dump(global_results, f)
    #     logging.info(f"\n{'='*70}")
    #     logging.info(f"✅✅ TODOS LOS RESULTADOS GUARDADOS")
    #     logging.info(f"{'='*70}")
    #     logging.info(f"Archivo global: training_results/depth_{depth}/global_results_{depth}.pkl")
    #     logging.info(f"Archivos por seed: training_results/depth_{depth}/seed*/full_results_{depth}.pkl")
    # except Exception as e:
    #     logging.error(f"\n❌ Error al guardar resultados globales: {e}")

    #return global_results
