
import requests

from sentinelhub import BBox, bbox_to_dimensions, CRS

from typing import Any, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np

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


## Function to make requests

def get_image_copernicus(access_token, time_interval, image_type, aoi, evalscript, resolution = 10): 
    identifier = ""
    if image_type == "png": 
        identifier = "default"
    elif image_type == "tiff":
        identifier = "index"
    url = "https://sh.dataspace.copernicus.eu/api/v1/process"

    aoi_bbox = BBox(bbox=aoi, crs=CRS.WGS84)
    aoi_size = bbox_to_dimensions(aoi_bbox, resolution=resolution)

    headers={
    "Content-Type": "application/json",
    "Authorization" : "Bearer "+ access_token
    }


    json={
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
                    "identifier": identifier,
                    "format": {
                        "type": "image/" + image_type
                    }
                }
            ]
        },
        "evalscript" : evalscript
    }

    response = requests.post(url, headers=headers, json=json)

    if response.status_code == 200:
        print(f"Request completed")
        return response 
    else:
        print(f"Request failed {response.content}")
        return None


## Function to plot maps
def plot_image(
    image: np.ndarray,
    factor: float = 1.0,
    clip_range: Optional[Tuple[float, float]] = None,
    grid_interval: Optional[int] = None,  # Grid interval in pixels
    **kwargs: Any
) -> None:
    """Utility function for plotting RGB images with optional grid."""
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    
    # Ensure correct aspect ratio and disable interpolation
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, aspect='equal', interpolation='none', **kwargs)
    
    if grid_interval:  # Add grid if specified
        ax.set_xticks(np.arange(0, image.shape[1], grid_interval))
        ax.set_yticks(np.arange(0, image.shape[0], grid_interval))
        ax.grid(color="white", linestyle="-", linewidth=0.5)
    else:  # Remove ticks if no grid
        ax.set_xticks([])
        ax.set_yticks([])