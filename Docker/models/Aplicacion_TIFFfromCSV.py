import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.features import geometry_mask
import geopandas as gpd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True, type=str, help="Fecha del producto a descargar (YYYY-MM-DD)")
parser.add_argument("--input", required=True, help="Directorio donde están las predicciones para la fecha de interés")
parser.add_argument("--output", required=True, help="Directorio donde se guardan los TIFFs")
parser.add_argument("--geojson_dir", default=None, help="Directorio con los GeoJSONs por profundidad (depth0-1_EPSG32630.geojson, ...)")
args = parser.parse_args()

path = args.input
date = args.date
geojson_dir = args.geojson_dir
filename = f"{date}_pred.csv"
df = pd.read_csv(os.path.join(path, filename))

depths = ["0_1", "1_2", "2_3", "3_4"]
for depth in depths:

    print(f"Generating TIFF file for {date} in depth {depth}")
    value_column = f'Chl_pred_{depth}'

    lats = np.sort(df['Latitude'].unique())[::-1]
    lons = np.sort(df['Longitude'].unique()) 

    data = np.full((len(lats), len(lons)), np.nan, dtype=np.float32)

    lat_idx = {lat: i for i, lat in enumerate(lats)}
    lon_idx = {lon: i for i, lon in enumerate(lons)}
    for _, row in df.iterrows():
        i = lat_idx[row['Latitude']]
        j = lon_idx[row['Longitude']]
        data[i, j] = row[value_column]

    pixel_size_lat = abs(lats[1] - lats[0]) if len(lats) > 1 else 0.01
    pixel_size_lon = abs(lons[1] - lons[0]) if len(lons) > 1 else 0.01
    transform = from_origin(lons[0] - pixel_size_lon/2, lats[0] + pixel_size_lat/2, pixel_size_lon, pixel_size_lat)

    if geojson_dir:
        geojson_path = os.path.join(geojson_dir, f"depth{depth.replace('_', '-')}_EPSG32630.geojson")
        gdf = gpd.read_file(geojson_path)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:32630")
        else:
            gdf = gdf.to_crs("EPSG:32630")
        depth_mask = geometry_mask(
            geometries=gdf.geometry,
            transform=transform,
            invert=True,
            out_shape=data.shape
        )
        data[~depth_mask] = np.nan
        print(f"  -> Depth mask applied from {geojson_path}")

    with rasterio.open(
        f'{args.output}{date}_chl_map_{depth}.tif',
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype='float32',
        crs='EPSG:32630',
        transform=transform,
        nodata=np.nan
    ) as dst:
        dst.write(data, 1)