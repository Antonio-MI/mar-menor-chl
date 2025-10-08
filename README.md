This repository contains the code and outputs relative to the article **"Chlorophyll-a Mapping and Prediction in the Mar Menor Lagoon Using C2RCC-Processed Sentinel 2 Imagery"** by Antonio Martínez Ibarra, Aurora González Vidal, Adrián Cánovas Rodríguez, and Antonio F. Skarmeta from the University of Murcia.

![Output demo: Chl-a for ](saved_files/application/2022-07-14_chl_pred_loop.gif)

# Paper Abstract

The Mar Menor, Europe’s largest hypersaline coastal lagoon, located in southeastern Spain, has undergone severe eutrophication crises, with devastating impacts on biodiversity and water quality. Monitoring chlorophyll-a (Chl-a), a proxy for phytoplankton biomass, is essential to anticipate harmful algal blooms and guide mitigation. Traditional *in situ* measurements, while precise, are spatially and temporally limited. Satellite-based approaches provide a more comprehensive view, enabling scalable, long-term, and transferable monitoring.
This study aims to overcome limitations of surface-only or short-term chlorophyll monitoring by developing a reliable methodology to predict and map Chl-a concentrations across the entire water column of the Mar Menor. Specifically, the work integrates Sentinel 2 imagery with buoy-based ground truth to create models capable of high-resolution, depth-specific monitoring, enhancing early-warning capabilities for eutrophication.
Nearly a decade of Sentinel 2 images was atmospherically corrected using C2RCC processors. Buoy data were aggregated by depth (0–1 m, 1–2 m, 2–3 m, 3–4 m). Multiple machine learning and deep learning algorithms—including Random Forest, XGBoost, CatBoost, Multilater Perceptron Networks, and ensembles—were trained and validated using cross-validation. Systematic band-combination experiments and spatial aggregation strategies were tested to optimize prediction.
Results show depth-dependent performance. At the surface, C2X-Complex with XGBoost and ensemble models achieved $R^2$ = 0.89; at 1–2 m, CatBoost and ensemble models reached $R^2$ = 0.87; at 2–3 m, TOA reflectances with KNN performed best ($R^2$ = 0.81); while at 3–4 m, Random Forest achieved $R^2$ = 0.66. Generated maps successfully reproduced known eutrophication events (e.g., 2016 crisis, 2025 surge), confirming robustness.
The study delivers an end-to-end, validated methodology for depth-specific chlorophyll mapping, surpassing previous surface-only efforts. Its integration of multispectral band combinations, buoy calibration, and ML/DL modeling offers a transferable framework for other turbid coastal systems.

# Code description

```
├── Aplicacion_Modelos.ipynb
├── Aplicacion_PlotTIFF.py
├── Aplicacion_TIFFfromCSV.py
├── Aplicacion_utils.py
├── BuoyData
│   ├── boyaIMIDA
│   │   ├── CTD-E1
│   │   │   ├── Clorofila.csv
│   │   │   ├── Conductividad.csv
│   │   │   ├── Materia Organiza.csv
│   │   │   ├── Oxigeno.csv
│   │   │   ├── PH.csv
│   │   │   ├── Polietileno.csv
│   │   │   ├── Salinidad.csv
│   │   │   ├── Temperatura.csv
│   │   │   ├── Transparencia.csv
│   │   │   └── Turbidez.csv
│   └── boyaUPCT
│       ├── extractedData
│       │   ├── CTD1
│       │   │   ├── CDOM.csv
│       │   │   ├── Clorofila.csv
│       │   │   ├── Oxigeno.csv
│       │   │   ├── PE.csv
│       │   │   ├── Salinidad.csv
│       │   │   ├── Temperatura.csv
│       │   │   ├── Transparency.csv
│       │   │   └── Turbidez.csv
│       ├── locBoyasUPCT.csv
│       └── locBoyasUPCT_reproyectado.csv
├── Copernicus
│   ├── access_token_credentials.py
│   ├── config.ini
│   ├── download_tiff.ipynb
│   ├── Fechas_CloudCover.ipynb
│   ├── productFetcher.py
│   ├── productFetcher_tozip.py
│   ├── snap_batch_application.sh
│   ├── snap_batch.sh
│   ├── snap_graph_application.properties
│   ├── snap_graph_application.xml
│   ├── snap_graph.properties
│   ├── snap_graph.xml
│   └── utils.py
├── Entrenamiento_Final.ipynb
├── extraNotebooks
│   ├── Aplicacion_GenerateGif.py
│   ├── Comparacion_Boyas_UPCT_IMIDA_filtered.ipynb
│   ├── Comparacion_Boyas_UPCT_IMIDA_raw.ipynb
│   ├── Comparacion_Boyas_Zonas.ipynb
│   ├── Datos_Boyas.ipynb
│   ├── Entrenamiento_V3.ipynb
│   ├── Replicar_Related_Extended.ipynb
│   ├── Replicar_Related.ipynb
│   └── Replicar_Related_merged_dataset.ipynb
├── files
│   ├── DiagramaCombinaciones.pdf
│   ├── DiagramaCombinaciones.svg
│   ├── GraphicalAbstract_V1.png
│   ├── GraphicalAbstract_V1.svg
│   ├── MarMenorBuoys.png
│   └── marmenor_polygon.geojson
├── Preparacion_Datasets.ipynb
├── README.md
├── requirements.txt
├── saved_files
│   ├── application
│   │   ├── 2022-07-14_chl_map_0_1.png
│   │   ├── 2022-07-14_chl_map_0_1.tif
│   │   ├── 2022-07-14_chl_map_1_2.png
│   │   ├── 2022-07-14_chl_map_1_2.tif
│   │   ├── 2022-07-14_chl_map_2_3.png
│   │   ├── 2022-07-14_chl_map_2_3.tif
│   │   ├── 2022-07-14_chl_map_3_4.png
│   │   ├── 2022-07-14_chl_map_3_4.tif
│   │   ├── 2022-07-14_chl_pred_loop.gif
│   │   ├── colormap_custom_2.txt
│   │   ├── preds
│   │   └── temp_csv
│   ├── dataset
│   │   ├── C2RCC_rhow_15x15_depth_eq_0.csv
│   │   ├── C2RCC_rhow_15x15_depth_eq_0_features.csv
│   │   ├── C2RCC_rhow_15x15_depth_eq_1.csv
│   ├── df_boyas_merge_depth_in_0_1.csv
│   ├── df_boyas_merge_depth_in_1_2.csv
│   ├── df_boyas_merge_depth_in_2_3.csv
│   ├── df_boyas_merge_depth_in_3_4.csv
│   ├── df_tifs_C2RCC_15x15.csv
│   ├── df_tifs_C2RCC_1x1.csv
│   ├── df_tifs_C2RCC_3x3.csv
│   ├── df_tifs_C2RCC_5x5.csv
│   ├── df_tifs_C2RCC_9x9.csv
│   ├── df_tifs_C2X_15x15.csv
│   ├── df_tifs_C2X_1x1.csv
│   ├── df_tifs_C2X_3x3.csv
│   ├── df_tifs_C2X_5x5.csv
│   ├── df_tifs_C2X_9x9.csv
│   ├── df_tifs_C2X-Complex_15x15.csv
│   ├── df_tifs_C2X-Complex_1x1.csv
│   ├── df_tifs_C2X-Complex_3x3.csv
│   ├── df_tifs_C2X-Complex_5x5.csv
│   └── df_tifs_C2X-Complex_9x9.csv
├── Seleccion_Parametros.ipynb
├── training_results
│   ├── global_results.pkl
│   ├── models
│   │   ├── C2X-Complex_rhow_5x5_depth_in_3_4_RF_features.json
│   │   ├── C2X-Complex_rhow_5x5_depth_in_3_4_RF_metadata.json
│   │   ├── C2X-Complex_rhow_5x5_depth_in_3_4_RF_model.joblib
│   │   ├── C2X-Complex_rhow_9x9_depth_in_0_1_XGB_features.json
│   │   ├── C2X-Complex_rhow_9x9_depth_in_0_1_XGB_metadata.json
│   │   ├── C2X-Complex_rhow_9x9_depth_in_0_1_XGB_model.joblib
│   │   ├── C2X-Complex_rhow_9x9_depth_in_0_1_XGB_model.json
│   │   ├── C2X-Complex_rhow_9x9_depth_in_1_2_CAT_features.json
│   │   ├── C2X-Complex_rhow_9x9_depth_in_1_2_CAT_metadata.json
│   │   ├── C2X-Complex_rhow_9x9_depth_in_1_2_CAT_model.cbm
│   │   ├── C2X-Complex_rhow_9x9_depth_in_1_2_CAT_model.joblib
│   │   ├── C2X-Complex_rhow_9x9_depth_in_1_2_CAT_model.json
│   │   ├── TOA_9x9_depth_in_2_3_KNN_features.json
│   │   ├── TOA_9x9_depth_in_2_3_KNN_metadata.json
│   │   └── TOA_9x9_depth_in_2_3_KNN_model.joblib
│   ├── results_csv
│   │   ├── results_in_0_1_R2_test.csv
│   │   ├── results_in_0_1_R2_train.csv
│   │   ├── results_in_0_1_RMSE_test.csv
│   │   ├── results_in_0_1_RMSE_train.csv
│   │   ├── results_in_1_2_R2_test.csv
│   │   ├── results_in_1_2_R2_train.csv
│   │   ├── results_in_1_2_RMSE_test.csv
│   │   ├── results_in_1_2_RMSE_train.csv
│   │   ├── results_in_2_3_R2_test.csv
│   │   ├── results_in_2_3_R2_train.csv
│   │   ├── results_in_2_3_RMSE_test.csv
│   │   ├── results_in_2_3_RMSE_train.csv
│   │   ├── results_in_3_4_R2_test.csv
│   │   ├── results_in_3_4_R2_train.csv
│   │   ├── results_in_3_4_RMSE_test.csv
│   │   └── results_in_3_4_RMSE_train.csv
│   ├── results_entrenamiento_CV_corrected_in_0_1.pkl
│   ├── results_entrenamiento_CV_corrected_in_1_2.pkl
│   ├── results_entrenamiento_CV_corrected_in_2_3.pkl
│   ├── results_entrenamiento_CV_corrected_in_3_4.pkl
│   ├── results_entrenamiento_CV_in_0_1.pkl
│   ├── results_entrenamiento_CV_in_1_2.pkl
│   ├── results_entrenamiento_CV_in_2_3.pkl
│   ├── results_entrenamiento_CV_in_3_4.pkl
│   ├── results_entrenamiento_CV.pkl
│   ├── results_entrenamiento_final_in_0_1.pkl
│   ├── results_entrenamiento_final_in_1_2.pkl
│   ├── results_entrenamiento_final_in_2_3.pkl
│   ├── results_entrenamiento_final_in_3_4.pkl
│   ├── selection_results_in_0_1.pkl
│   ├── selection_results_in_1_2.pkl
│   ├── selection_results_in_2_3.pkl
│   └── selection_results_in_3_4.pkl
└── utils.py

```

