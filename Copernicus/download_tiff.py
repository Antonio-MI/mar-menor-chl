import configparser
from rasterio.io import MemoryFile
from datetime import datetime, timedelta
from sentinelhub import SHConfig, SentinelHubCatalog, DataCollection
import os
import rasterio
import time
import requests
from sentinelhub import BBox, bbox_to_dimensions, CRS
from typing import Any, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import json

#year = 2022
start = datetime(2017, 6, 1)
end = datetime(2017, 6, 30)
#cloud_cover_limit = 90
folder = "/home/thinking/raw/Sentinel2_tiff_metadata/"

## Function to retrieve access token

def get_access_token(username: str, password: str) -> str:

    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    try:
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
        access_token = r.json().get("access_token")
        if not access_token:
            raise ValueError("No access token found in response.")
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def extract_metadata(results):
    """Extrae metadatos relevantes de Sentinel Hub Catalog results."""
    metadata_list = []
    for r in results:
        props = r.get("properties", {})
        assets = r.get("assets", {})
        
        metadata = {
            "id": r.get("id"),
            "platform": props.get("platform"),
            "instrument": props.get("instruments", [None])[0],
            "datetime": props.get("datetime"),
            "bbox": r.get("bbox"),
            "epsg": props.get("proj:epsg"),
            "proj_bbox": props.get("proj:bbox"),
            "cloud_cover": props.get("eo:cloud_cover"),
            "gsd": props.get("gsd"),
            "s3_href": assets.get("data", {}).get("href"),
        }
        metadata_list.append(metadata)
    return metadata_list

config_file = configparser.ConfigParser()
config_file.read("config.ini")

username = config_file["copernicus"]["username"]
password = config_file["copernicus"]["password"]

config = SHConfig()
config.sh_client_id = config_file["copernicus"]["client_id"] #"<CLIENT ID>"
config.sh_client_secret = config_file["copernicus"]["client_secret"] #<CLIENT SECRET>"
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token" # Is it required?
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.save("cdse")
config = SHConfig("cdse")

def download_image_copernicus(access_token, time_interval, image_type, aoi, evalscript, resolution, config, save_path, cloud_cover_limit): 

    # Set the url to sent the request
    url = "https://sh.dataspace.copernicus.eu/api/v1/process"

    # Define the Area of Interest
    aoi_bbox = BBox(bbox=aoi, crs=CRS.WGS84)
    aoi_size = bbox_to_dimensions(aoi_bbox, resolution=resolution)

    # Use SentinelHubCatalog to check if there are any images in the time interval of interest
    # If there are, extract the date (can't get it directly from the tiff)
    catalog = SentinelHubCatalog(config=config)
    date_range = time_interval[0],  time_interval[1]
    search_iterator = catalog.search(
        DataCollection.SENTINEL2_L2A,
        bbox=aoi_bbox,
        time= date_range ,
        fields={"include": ["properties"]},
    )
    results = list(search_iterator)
    # Sacamos metadatos
    metadata = extract_metadata(results)
    print(metadata)
    unique_results = {}
    # A partir del id guardamos las fechas
    for item in results:
        acquisition_id = item['id'].split('_T')[0]
        if acquisition_id not in unique_results:
            unique_results[acquisition_id] = item
    unique_results = list(unique_results.values())
    ids = [item['id'] for item in unique_results]
    dates = [datetime.strptime(id.split('_')[2][:8], "%Y%m%d").date() for id in ids]
    
    # Guardamos cloud cover de las imágenes en el intervalo
    cloud_covers = []
    for item in results:
        cloud_cover = item["properties"]["eo:cloud_cover"]
        cloud_covers.append(cloud_cover)

    if len(dates) == 0: 
        print(f"Request empty for dates {time_interval}")
        return None, None
    
    # Comprobar si la imagen está cubierta por nubes antes de seguir
    # elif any(cc > cloud_cover_limit for cc in cloud_covers):
    #     print(f"Request covered by clouds for dates {time_interval}, with coverage {cloud_covers}")
    #     return None, None       

    else: 
        date_string = [d.isoformat() for d in dates][0]

        # Define the content for the post
        headers={
        "Content-Type": "application/json",
        "Authorization" : "Bearer "+ access_token
        }


        json_payload={
            "input": {
                "bounds": {
                    "bbox": aoi
                },
                "data": [
                    {
                    "dataFilter": {
                        "timeRange": {
                        "from": time_interval[0] + "T00:00:00Z", #"2024-10-12T00:00:00Z", #YYYY-mm-dd
                        "to": time_interval[1] + "T23:59:59Z"#"2024-11-12T23:59:59Z"
                        },
                        "mosaickingOrder": "leastCC"
                    
                    },
                    "type": "sentinel-2-l2a"
                    }]
            },
            "output": {
                "width": aoi_size[0],#1271,
                "height": aoi_size[1],#2183

                "responses": [
                    {
                        "format": {
                            "type": "image/" + image_type
                        }
                    }
                ]
            },
            "evalscript" : evalscript,
            "data_folder" : "test_dir",
            "save_data" : True
        }

        response = requests.post(url, headers=headers, json=json_payload)

        if response.status_code == 200:
            print(f"Request completed for date {date_string} in interval {time_interval}")
            
        if save_path:
            # Nombre de archivo a partir de la fecha
            full_id = metadata[0]["id"]
            short_id = "_".join(full_id.split("_")[:-2])

            tiff_file = os.path.join(save_path, f"{short_id}.tif")
            json_file = os.path.join(save_path, f"{short_id}.json")

            # full_date = metadata[0]["datetime"] if metadata else None
            # print(f"--------{full_date}")

            # Guardar metadatos en JSON
            with open(json_file, "w") as f:
                json.dump(metadata, f, indent=4)
            print(f"Saved JSON metadata to {json_file}")

            # Guardar imagen georreferenciada
            with MemoryFile(response.content) as memfile:
                with memfile.open() as dataset:
                    profile = dataset.profile
                    profile.update(driver="GTiff")
                    with rasterio.open(tiff_file, 'w', **profile) as dst:
                        dst.write(dataset.read())
            print(f"Saved TIFF file to {tiff_file}")
            
            return response, date_string
        else:
            print(f"Request failed {response.content}")
            return None, None
        
evalscript_all_bands = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12","SCL"]
            }],
            output: {
                bands: 13,
                sampleType: "FLOAT32"
            }
        };
    }

    function evaluatePixel(sample) {
        return [sample.B01,
                sample.B02,
                sample.B03,
                sample.B04,
                sample.B05,
                sample.B06,
                sample.B07,
                sample.B08,
                sample.B8A,
                sample.B09,
                sample.B11,
                sample.B12,
                sample.SCL];
    }
"""


access_token = get_access_token(username, password)
evalscript = evalscript_all_bands
image_type = "tiff" 
aoi = [-0.866977, 37.628916, -0.71696, 37.822802]
resolution = 10

## Time interval ## 
tdelta = timedelta(days=5)
n_chunks = round((end - start)/tdelta)
starts = [(start + i * tdelta).date().isoformat() for i in range(n_chunks+1)]
ends = [(start + timedelta(days=4) + i * tdelta).date().isoformat() for i in range(n_chunks+1)]

# Slots que nos interesan de las fechas que están sincronizadas
target_dates = [
    '2021-01-05', '2021-01-15', '2021-02-04', '2021-02-14', '2021-03-11',
    # '2021-03-16', '2021-03-21', '2021-04-05', '2021-04-20', '2021-04-30',
    # '2021-05-10', '2021-05-20', '2021-05-30', '2021-06-09', '2021-06-19',
    # '2021-06-29', '2021-07-09', '2021-07-19', '2021-07-29', '2021-08-08',
    # '2021-08-18', '2021-08-28', '2021-09-07', '2021-09-17', '2021-09-27',
    # '2021-10-07', '2021-10-17', '2021-10-27', '2021-11-06', '2021-11-16',
    # '2021-11-26', '2021-12-06', '2021-12-16', '2021-12-26', '2022-01-05',
    # '2022-01-15', '2022-01-25', '2022-02-04', '2022-02-14', '2022-02-24',
    # '2022-03-06', '2022-03-16', '2022-03-26', '2022-04-05', '2022-04-15',
    # '2022-04-25', '2022-05-05', '2022-05-15', '2022-05-25', '2022-06-04',
    # '2022-06-14', '2022-06-24', '2022-07-04', '2022-07-14', '2022-07-24',
    # '2022-08-03', '2022-08-13', '2022-08-23', '2022-09-02', '2022-09-12',
    # '2022-09-22', '2022-10-02', '2022-10-12', '2022-10-22', '2022-11-01',
    # '2022-11-11', '2022-11-21', '2022-12-01', '2022-12-11', '2022-12-21',
    # '2022-12-31', '2023-01-10', '2023-01-20', '2023-01-30', '2023-02-09',
    # '2023-02-19', '2023-03-01', '2023-03-11', '2023-03-21', '2023-03-31',
    # '2023-04-10', '2023-04-20', '2023-04-30', '2023-05-10', '2023-05-20',
    # '2023-05-30', '2023-06-09', '2023-06-19', '2023-06-29', '2023-07-09',
    # '2023-07-19', '2023-07-29', '2023-08-08', '2023-08-18', '2023-08-28',
    # '2023-09-07', '2023-09-17', '2023-09-27', '2023-10-07', '2023-10-17',
    # '2023-10-27', '2023-11-06', '2023-11-16', '2023-11-26', '2023-12-06',
    # '2023-12-16', '2023-12-26', '2024-01-05', '2024-01-15', '2024-01-25',
    # '2024-02-04', '2024-02-14', '2024-02-24', '2024-03-05', '2024-03-15',
    # '2024-03-25', '2024-04-04', '2024-04-14', '2024-04-24', '2024-05-04',
    # '2024-05-14', '2024-05-24', '2024-06-03', '2024-06-13', '2024-06-23',
    # '2024-07-03', '2024-07-13', '2024-07-23', '2024-08-02', '2024-08-12',
    # '2024-08-22', '2024-09-01', '2024-09-11', '2024-09-21', '2024-10-01',
    # '2024-10-11', '2024-10-21', '2024-10-31', '2024-11-10', '2024-11-20',
    # '2024-11-30', '2024-12-10', '2024-12-20', '2024-12-30', '2025-01-09',
    # '2025-01-19', '2025-01-29', '2025-02-08', '2025-02-18', '2025-02-28',
    # '2025-03-10', '2025-03-20', '2025-03-30', '2025-04-09', '2025-04-19',
    # '2025-04-29', '2025-05-09', '2025-05-19', '2025-05-29', '2025-06-08',
    # '2025-06-18', '2025-06-28', '2025-07-08', '2025-07-18', '2025-07-28',
    # '2025-08-07', '2025-08-17', '2025-08-27', '2025-09-06'
]
slots = [((datetime.strptime(d, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d"), (datetime.strptime(d, "%Y-%m-%d") + timedelta(days=4)).strftime("%Y-%m-%d")) for d in target_dates]



start_time = time.time()
for time_interval in slots:

    if time.time() - start_time > 540: # If it has been more than 9 minutes since the token is obtained, update the token.
        print('time passed:', time.time() - start_time)
        access_token = get_access_token(username, password)
        start_time = time.time()

    # Get the satellite response for the current time interval
    response, date_taken = download_image_copernicus(access_token, time_interval, image_type, aoi, evalscript, resolution, config, folder, cloud_cover_limit)
    if response is None:
        print(f"No data available for time interval {time_interval}")
        continue 

    if response.status_code == 200:
        print("Ok")
