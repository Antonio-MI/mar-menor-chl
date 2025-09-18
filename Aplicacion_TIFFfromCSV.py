import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import from_origin

df = pd.read_csv('saved_files/application/2022-07-14_pred.csv')

depth = "0_1"

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

with rasterio.open(
    f'saved_files/application/chl_pred_{depth}.tif',
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