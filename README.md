This repository contains the code and outputs relative to the article **"Chlorophyll-a Mapping and Prediction in the Mar Menor Lagoon Using C2RCC-Processed Sentinel 2 Imagery"** by Antonio Martínez Ibarra, Aurora González Vidal, Adrián Cánovas Rodríguez, and Antonio F. Skarmeta from the University of Murcia, submitted to IEEE Transactions on Geoscience and Remote Sensing for publication.

![Output demo: Chl-a for 2022-07-14](saved_files/application/2022-07-14_chl_pred_loop.gif)

# Paper Abstract

The Mar Menor, Europe’s largest hypersaline coastal lagoon, located in southeastern Spain, has undergone severe eutrophication crises, with devastating impacts on biodiversity and water quality. Monitoring chlorophyll-a (Chl-a), a proxy for phytoplankton biomass, is essential to anticipate harmful algal blooms and guide mitigation. Traditional *in situ* measurements, while precise, are spatially and temporally limited. Satellite-based approaches provide a more comprehensive view, enabling scalable, long-term, and transferable monitoring.
This study aims to overcome limitations of chlorophyll monitoring, often restricted to surface estimates or limited temporal coverage, by developing a reliable methodology to predict and map Chl-a concentrations across the entire water column of the Mar Menor. Specifically, the work integrates Sentinel 2 imagery with buoy-based ground truth to create models capable of high-resolution, depth-specific monitoring, enhancing early-warning capabilities for eutrophication.
Nearly a decade of Sentinel 2 images was atmospherically corrected using C2RCC processors. Buoy data were aggregated by depth (0–1 m, 1–2 m, 2–3 m, 3–4 m). Multiple machine learning and deep learning algorithms—including Random Forest, XGBoost, CatBoost, Multilater Perceptron Networks, and ensembles—were trained and validated using cross-validation. Systematic band-combination experiments and spatial aggregation strategies were tested to optimize prediction.
Results show depth-dependent performance. At the surface, C2X-Complex with XGBoost and ensemble models achieved $R^2$ = 0.89; at 1–2 m, CatBoost and ensemble models reached $R^2$ = 0.87; at 2–3 m, TOA reflectances with KNN performed best ($R^2$ = 0.81); while at 3–4 m, Random Forest achieved $R^2$ = 0.66. Generated maps successfully reproduced known eutrophication events (e.g., 2016 crisis, 2025 surge), confirming robustness.
The study delivers an end-to-end, validated methodology for depth-specific chlorophyll mapping, surpassing previous surface-only efforts. Its integration of multispectral band combinations, buoy calibration, and ML/DL modeling offers a transferable framework for other turbid coastal systems.

## Application examples

**2022-07-14**

Whiting event, when a white spot appeared on the western side of the lagoo. Such phenomena are usually linked to phytoplankton blooms or riverine sediments, although in this case the cause was uncertain. Previous reports noted consistently higher Chl-a concentrations within the white spot compared to surrounding areas. Accordingly, the predicted map for this date highlights the white spot with higher Chl-a values than its vicinity.

| ![img1](saved_files/application/2022-07-14_chl_map_0_1.png) | ![img2](saved_files/application/2022-07-14_chl_map_1_2.png) | ![img3](saved_files/application/2022-07-14_chl_map_2_3.png) | ![img4](saved_files/application/2022-07-14_chl_map_3_4.png) |
| :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: |
|                           0 - 1 m                           |                           1 - 2 m                           |                           2 - 3 m                           |                           3 - 4 m                           |

**2025-07-28**

Recent monitoring reports indicated a potential eutrophication episode triggered by increasing Chl-a levels in the lagoon. Consequently, the output for this date should show higher Chl-a concentrations than in July 2022, when average values were relatively low. Additionally, a general pattern observed is that Chl-a concentration tends to increase with depth.

| ![img1](saved_files/application/2025-07-28_chl_map_0_1.png) | ![img2](saved_files/application/2025-07-28_chl_map_1_2.png) | ![img3](saved_files/application/2025-07-28_chl_map_2_3.png) | ![img4](saved_files/application/2025-07-28_chl_map_3_4.png) |
| :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: |
|                           0 - 1 m                           |                           1 - 2 m                           |                           2 - 3 m                           |                           3 - 4 m                           |

**2021-08-13**

The maps for August 13, 2021, correspond to a short period in which chlorophyll-a concentrations peaked, with values close to those reached during the 2016 eutrophication crisis.

| ![img1](saved_files/application/2021-08-13_chl_map_0_1.png) | ![img2](saved_files/application/2021-08-13_chl_map_1_2.png) | ![img3](saved_files/application/2021-08-13_chl_map_2_3.png) | ![img4](saved_files/application/2021-08-13_chl_map_3_4.png) |
| :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: |
|                           0 - 1 m                           |                           1 - 2 m                           |                           2 - 3 m                           |                           3 - 4 m                           |

**2024-02-04**

Chl-a concentrations for February 4, 2024. Represented to visualize normal behavior: low Chl-a values at surface which increase slightly with depth.

| ![img1](saved_files/application/2024-02-04_chl_map_0_1.png) | ![img2](saved_files/application/2024-02-04_chl_map_1_2.png) | ![img3](saved_files/application/2024-02-04_chl_map_2_3.png) | ![img4](saved_files/application/2024-02-04_chl_map_3_4.png) |
| :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: |
|                           0 - 1 m                           |                           1 - 2 m                           |                           2 - 3 m                           |                           3 - 4 m                           |

**2016-09-08**

September 8, 2016, during the eutrophication crisis. The maps show Chl-a concentrations peaking and in some depths, they have even saturated the color scale. 

| ![img1](saved_files/application/2016-09-08_chl_map_0_1.png) | ![img2](saved_files/application/2016-09-08_chl_map_1_2.png) | ![img3](saved_files/application/2016-09-08_chl_map_2_3.png) | ![img4](saved_files/application/2016-09-08_chl_map_3_4.png) |
| :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: | :---------------------------------------------------------: |
|                           0 - 1 m                           |                           1 - 2 m                           |                           2 - 3 m                           |                           3 - 4 m                           |

# Code description

The notebooks used to train and evaluate the models are:

`Preparación_Datasets.ipynb` $\rightarrow$ `Seleccion_Parametros.ipynb` $\rightarrow$ `Entrenamiento_Final.ipynb`

The flux needed to process a new image and create a map is:

- `productFetcher.py` to download the date of interest. Needs S3 credentials from https://eodata-s3keysmanager.dataspace.copernicus.eu/
- `snap_batch_application.sh` from the terminal to apply atmospheric correction. The date can be changed in this script.
- `Aplicacion_Models.py`  to load processed tiff and apply corresponding models for each depth.
- `Aplicacion_TIFFfromCSV.py` to load Chl-a prediction csvs and generate a tiff file for each depth.
- `Aplicacion_PlotTIFF.py` to create individual plots or `Aplicacion_GenerateGif.py` to create a gif with all depths.

The code is structured as follows:

```
├── Aplicacion_Modelos.ipynb # Notebook to apply final models for each depth to new images and generate Chl-a prediction for each pixel, saved into csv. Uses the functions defined in Aplicacion_utils.py
├── Aplicacion_PlotTIFF.py # Script to plot tiff files (obtained from Aplicacion_TIFFfromCSV.py) using a custom colormap
├── Aplicacion_TIFFfromCSV.py # Script to generate tiff files from the csv's generated by Aplicacion_Modelos.ipynb
├── Aplicacion_utils.py # Script with functions to: extract reflectances for each pixel in the Mar Menor, split C2RCC processing methods into dataframes, add band combinations, and perform inference with the models
├── BuoyData # Folder with data from two sources: IMIDA and UPCT
│   ├── boyaIMIDA
│   │   ├── CTD-XX 
│   │   │   ├── Chl-a (as Clorofila.csv) and other parameters such as temperature, oxygen and turbidity, among others
│   └── boyaUPCT
│       ├── extractedData
│       │   ├── CTDXX
│       │   │   ├── Chl-a (as Clorofila.csv) and other parameters such as temperature, oxygen and turbidity, among others.
│       ├── locBoyasUPCT.csv # Buoys' coordinates
│       └── locBoyasUPCT_reproyectado.csv # With another coordinate system
├── Copernicus # Contains scripts and notebooks related to Sentinel 2 imagery
│   ├── access_token_credentials.py # function to get access token
│   ├── config.ini # passwords for the previous script
│   ├── download_tiff.ipynb # Example to download L2A images for a specific AoI
│   ├── Fechas_CloudCover.ipynb # Measurement of cloud cover for a predefined AoI and dates
│   ├── productFetcher.py # Script to download SAFE files
│   ├── productFetcher_tozip.py # Script to zip SAFE files
│   ├── snap_batch.sh # bash script to process images with SNAP in the terminal
│   ├── snap_graph.properties # SNAP Parameters for the bash script
│   ├── snap_graph.xml # Graph of operations performed by SNAP
│   ├── snap_batch_application.sh # As the previous, but with parameters needed specically to apply final models
│   ├── snap_graph_application.properties
│   ├── snap_graph_application.xml
│   └── utils.py
├── Entrenamiento_Final.ipynb # Notebook to train all the models for the selected datasets, evaluation, and final training with the best configuration to save and apply in Aplicacion_Modelos.ipynb
├── extraNotebooks
│   ├── Aplicacion_GenerateGif.py # Generate a gif with all depths
│   ├── Comparacion_Boyas_UPCT_IMIDA_filtered.ipynb # Comparison between buoy data from the two sources used
│   ├── Comparacion_Boyas_UPCT_IMIDA_raw.ipynb
│   ├── Comparacion_Boyas_Zonas.ipynb # Clustering test to group bouys by zone
│   ├── Datos_Boyas.ipynb # Visualization and descriptive analysis of buoy data
│   ├── Entrenamiento_V3.ipynb # Preliminary test to implement cross validation into the flux
│   ├── Replicar_Related_Extended.ipynb # Notebooks to replicate other articles
│   ├── Replicar_Related.ipynb
│   └── Replicar_Related_merged_dataset.ipynb
├── files # files used in the article and Mar Menor geojson
├── Preparacion_Datasets.ipynb # Notebook to unify buoy data, load reflectances from processed images (with SNAP) and make window aggregations. Intermediate outputs saved into saved_files. Merge of bouy and satellite data and band combinations addition. csv outputs save into saved_files/dataset. Those are used in Seleccion_Parametros.ipynb
├── README.md
├── requirements.txt
├── saved_files
│   ├── application # Tiffs and pngs for several dates and depth
│   │   ├── 2022-07-14_chl_map_0_1.png 
│   │   ├── ...
│   │   ├── 2022-07-14_chl_pred_loop.gif # Gif example
│   │   ├── colormap_custom.txt # Custom colormap for the maps
│   │   ├── preds # Outputs from Aplicacion_Modelos.ipynb go here. Empty beacuse each file is ~100mb.
│   │   └── temp_csv # csv with reflectances for all the pixes obtained in Aplicacion_Modelos.ipynb go here. Empty because each file is ~250mb.
│   ├── dataset # csv for every combination of (C2RCC processing x window aggregation x depth x with/without added features)
│   ├── df_boyas_merge_depth_in_0_1.csv # Merged buoy data for each depth
│   ├── ...
│   ├── df_tifs_C2RCC_15x15.csv # Reflectances with different window aggregations and processing
│   ├── df_tifs_C2X_9x9.csv
│   ├── ...
├── Seleccion_Parametros.ipynb # Hyperparameter seleccion with Optuna. Results saved in training_results
├── training_results
│   ├── global_results.pkl
│   ├── models # joblib with final models and json files with metadata
│   ├── results_csv # train and test metrics (R2 and RMSE). Obtained in Entrenamiento_Final.ipynb
│   ├── results_entrenamiento_final_in_0_1.pkl # Result from Entrenamiento_Final.ipynb
│   ├── ...
│   ├── selection_results_in_0_1.pkl # Results form Seleccion_Parametros.ipynb
│   ├── ...
└── utils.py

```

# Cite

## 

## Contact

antonio.martinezi@um.es
