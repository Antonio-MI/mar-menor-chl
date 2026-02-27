This repository contains the code and outputs relative to the article **"Chlorophyll-a Mapping and Prediction in the Mar Menor Lagoon Using C2RCC-Processed Sentinel 2 Imagery"** by Antonio Martínez Ibarra, Aurora González Vidal, Adrián Cánovas Rodríguez, and Antonio F. Skarmeta from the University of Murcia.

![Output demo: Chl-a for 2022-07-14](saved_files/application/2022-07-14_chl_pred_loop.gif)

# Abstract

The Mar Menor, Europe’s largest hypersaline coastal lagoon, located in southeastern Spain, has undergone severe eutrophication crises, with devastating impacts on biodiversity and water quality. Monitoring chlorophyll-a, a proxy for phytoplankton biomass, is essential to anticipate harmful algal blooms and guide mitigation. Traditional *in situ* measurements, while precise, are spatially and temporally limited. Satellite-based approaches provide a more comprehensive view, enabling scalable and long-term monitoring. This study aims to overcome limitations of chlorophyll monitoring, often restricted to surface estimates or limited temporal coverage, by developing a reliable methodology to predict and map chlorophyll-a concentrations across the water column of the Mar Menor. This work integrates Sentinel 2 imagery with buoy-based ground truth to create models capable of high-resolution, depth-specific monitoring, enhancing early-warning capabilities for eutrophication. 
Nearly a decade of Sentinel 2 images were atmospherically corrected using C2RCC processors. Buoy data were aggregated by depth (0–1 m, 1–2 m, 2–3 m, 3–4 m). Multiple machine and deep learning algorithms, including CatBoost, XGBoost, Support Vector Machines, and Multilayer Perceptron Networks, were trained and validated using cross-validation. Band-combination experiments and spatial aggregation strategies were tested to optimize prediction. The results show depth-dependent performance. The Root Mean Squared Logarithmic Error (RMSLE) obtained ranges from 0.34 at the surface to 0.39 at 3–4 m, while the $R^2$ value was 0.76 at the surface, 0.76 at 1–2 m, 0.70 at 2–3 m, and 0.60 at 3–4 m. Generated maps successfully reproduced known eutrophication events (e.g., 2016 crisis, 2025 surge), confirming robustness. The study delivers an end-to-end, validated methodology chlorophyll mapping. Its integration of multispectral band combinations, buoy calibration, and modeling offers a transferable framework for other turbid coastal systems.

## Application examples

**2022-07-14**

Whiting event, when a white spot appeared on the western side of the lagoon. Such phenomena are usually linked to phytoplankton blooms or riverine sediments, although in this case the cause was uncertain. Previous reports noted consistently higher Chl-a concentrations within the white spot compared to surrounding areas. Accordingly, the predicted map for this date highlights the white spot with higher Chl-a values than its vicinity.

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

Update: an automated flux has been added to the repo (16/10/2025) with Docker. It can be found in `\Docker`.

The code is structured as follows:

```
├── Aplicacion_GenerateGif.py # Script to create a gif with all depths
├── Aplicacion_Modelos.ipynb # Notebook to apply final models for each depth to new images and generate Chl-a prediction for each pixel, saved into csv. Uses the functions defined in Aplicacion_utils.py
├── Aplicacion_PlotTIFF.py # Script to plot tiff files (obtained from Aplicacion_TIFFfromCSV.py) using a custom colormap
├── Aplicacion_TIFFfromCSV.py # Script to generate tiff files from the csv's generated by Aplicacion_Modelos.ipynb
├── Aplicacion_utils.py # Script with functions to: extract reflectances for each pixel in the Mar Menor, split C2RCC processing methods into dataframes, add band combinations, and perform inference with the models
├── BuoyData # Folder with data from two sources: IMIDA and UPCT
│   ├── boyaIMIDA
│   │   ├── CTD-XX 
│   │   │   ├── Chl-a (as Clorofila.csv) and other parameters such as temperature, oxygen and turbidity, among others
│   └── boyaUPCT
│       ├── extractedData
│       │   ├── CTDXX
│       │   │   ├── Chl-a (as Clorofila.csv) and other parameters such as temperature, oxygen and turbidity, among others.
│       ├── locBoyasUPCT.csv # Buoys' coordinates
│       └── locBoyasUPCT_reproyectado.csv # With another coordinate system
├── Copernicus # Contains scripts and notebooks related to Sentinel 2 imagery
│   ├── access_token_credentials.py # function to get access token
│   ├── config.ini # passwords for the previous script
│   ├── download_tiff.ipynb # Example to download L2A images for a specific AoI
│   ├── Fechas_CloudCover.ipynb # Measurement of cloud cover for a predefined AoI and dates
│   ├── productFetcher.py # Script to download SAFE files
│   ├── productFetcher_tozip.py # Script to zip SAFE files
│   ├── snap_batch.sh # bash script to process images with SNAP in the terminal
│   ├── snap_graph.properties # SNAP Parameters for the bash script
│   ├── snap_graph.xml # Graph of operations performed by SNAP
│   ├── snap_batch_application.sh # As the previous, but with parameters needed specically to apply final models
│   ├── snap_graph_application.properties
│   ├── snap_graph_application.xml
│   └── utils.py
├── Docker # Docker setup for automated map generation (see README inside)
├── Entrenamiento_Final.ipynb # Notebook to train all the models for the selected datasets, evaluation, and final training with the best configuration to save and apply in Aplicacion_Modelos.ipynb
├── extraNotebooks
│   ├── Comparacion_Boyas_UPCT_IMIDA_filtered.ipynb # Comparison between buoy data from the two sources used
│   ├── Comparacion_Boyas_UPCT_IMIDA_raw.ipynb
│   ├── Comparacion_Boyas_Zonas.ipynb # Clustering test to group bouys by zone
│   ├── Datos_Boyas.ipynb # Visualization and descriptive analysis of buoy data
│   ├── Entrenamiento_V3.ipynb # Preliminary test to implement cross validation into the flux
│   ├── Replicar_Related_Extended.ipynb # Notebooks to replicate other articles
│   ├── Replicar_Related.ipynb
│   ├── Replicar_Related_merged_dataset.ipynb
│   ├── Significancia_Resultados.ipynb # Wilcoxon signed-rank test for statistical significance
│   └── utils.py
├── files # files used in the article and Mar Menor geojson
├── Final_Models.ipynb # Notebook to train final models with all the data
├── hyperparams.json # Hyperparameter configuration used in training and hyperparameter selection
├── input_file_seeds.txt # Input seeds file generated by seeds.py
├── main.py # Entry point for training pipeline execution
├── output_file_seeds.txt # Output seeds file, where completed seeds from input_file_seeds.txt are saved
├── Preparacion_Datasets.ipynb # Notebook to unify buoy data, load reflectances from processed images (with SNAP) and make window aggregations. Intermediate outputs saved into saved_files. Merge of buoy and satellite data and band combinations addition. csv outputs saved into saved_files/dataset. Those are used in Seleccion_Parametros.ipynb
├── Process_Results.ipynb # Notebook to process and analyse training results
├── README.md
├── requirements.txt
├── run.sh # Shell script to run the training pipeline
├── saved_files
│   ├── application # Tiffs and pngs for several dates and depth
│   │   ├── 2022-07-14_chl_map_0_1.png 
│   │   ├── ...
│   │   ├── 2022-07-14_chl_pred_loop.gif # Gif example
│   │   ├── colormap_custom.txt # Custom colormap for the maps
│   │   ├── preds # Outputs from Aplicacion_Modelos.ipynb go here. Empty because each file is ~100mb.
│   │   └── temp_csv # csv with reflectances for all the pixels obtained in Aplicacion_Modelos.ipynb go here. Empty because each file is ~250mb
│   ├── dataset # csv for every combination of (C2RCC processing x window aggregation x depth x with/without added features)
│   ├── df_boyas_merge_depth_in_0_1.csv # Merged buoy data for each depth
│   ├── ...
│   ├── df_tifs_C2RCC_15x15.csv # Reflectances with different window aggregations and processing
│   ├── df_tifs_C2X_9x9.csv
│   ├── ...
├── seeds.py # Script to generate random seeds
├── Seleccion_Parametros.ipynb # Hyperparameter selection with Optuna. Results saved in training_results
├── training_results
│   ├── models # joblib with final models and json files with metadata
│   ├── results_csv # train and test metrics (RMSLE, R2 and RMSE)
└── utils.py # functions used by main.by. Includes data loading, hyperparameter optimization, training, predictions and evalutation functions

```



# Usage

To simplify map generation, a Docker folder has been added to the repository, which allows for a much easier process, detailed in another `README.md` inside that folder.



# Cite

Preprint available at https://doi.org/10.48550/arXiv.2510.09736 (arXiv), and https://zenodo.org/records/18769187 (Zenodo) (DOI's for arxiv and Zenodo are different)

Style IEEE

A. Martínez-Ibarra, A. González-Vidal, A. Cánovas-Rodríguezy A. F. Skarmeta, «Chlorophyll-a Mapping and Prediction in the Mar Menor Lagoon Using C2RCC-Processed Sentinel 2 Imagery». Zenodo, feb. 24, 2026. doi: 10.5281/zenodo.18769187.

Style APA

Martínez-Ibarra, A., González-Vidal, A., Cánovas-Rodríguez, A., & Skarmeta, A. F. (2026). Chlorophyll-a Mapping and Prediction in the Mar Menor Lagoon Using C2RCC-Processed Sentinel 2 Imagery. Zenodo. https://doi.org/10.5281/zenodo.18769187

BibTeX (arxiv)
```
@misc{martínezibarra2026chlorophyllamappingpredictionmar,
      title={Chlorophyll-a Mapping and Prediction in the Mar Menor Lagoon Using C2RCC-Processed Sentinel 2 Imagery}, 
      author={Antonio Martínez-Ibarra and Aurora González-Vidal and Adrián Cánovas-Rodríguez and Antonio F. Skarmeta},
      year={2026},
      eprint={2510.09736},
      archivePrefix={arXiv},
      primaryClass={eess.IV},
      url={https://arxiv.org/abs/2510.09736}, 
}
```


## Contact

antonio.martinezi@um.es
