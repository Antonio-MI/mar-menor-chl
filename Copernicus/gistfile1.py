import pandas as pd
import requests
import configparser
import subprocess
import json
import requests
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

username = config["copernicus"]["username"]
password = config["copernicus"]["password"]

def get_access_token(username: str, password: str) -> str:
    # Prepare the data for the token request
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    
    # Send the request to get the access token
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

# Get username and password from user securely
import getpass
# username = getpass.getpass("Enter your username: ")
# password = getpass.getpass("Enter your password: ")

# Retrieve the token
access_token = get_access_token(username, password)
if access_token:
    #print(f"Access token: {access_token}")
    print("Access token retrieved")
else:
    print("Failed to retrieve access token.")


# Define parameters
start_date = "2022-06-01"
end_date = "2022-06-10"
data_collection = "SENTINEL-2"
aoi = "POLYGON((4.220581 50.958859,4.521264 50.953236,4.545977 50.906064,4.541858 50.802029,4.489685 50.763825,4.23843 50.767734,4.192435 50.806369,4.189689 50.907363,4.220581 50.958859))'"

# Replace with your actual access token
# access_token = config["copernicus"]["access_token"]

# Prepare headers with the access token
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Make the request to fetch images
response = requests.get(
    f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
    f"$filter=Collection/Name eq '{data_collection}' and "
    f"OData.CSC.Intersects(area=geography'SRID=4326;{aoi}) and "
    f"ContentDate/Start gt {start_date}T00:00:00.000Z and "
    f"ContentDate/Start lt {end_date}T00:00:00.000Z",
    headers=headers
)

# Parse the JSON response and convert to DataFrame
if response.status_code == 200:
    json_data = response.json()
    if 'value' in json_data:
        df = pd.DataFrame.from_dict(json_data['value'])
        print(df.head(5))  # Display the first 5 rows
    else:
        print("No data found in the response.")
else:
    print(f"Failed to fetch data: {response.status_code} - {response.text}")

# Manually selected the first ID
url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products(550c10a8-3a31-5f28-8d68-e0b7086dbc8f)/$value"

#headers = {"Authorization": f"Bearer {access_token}"}

session = requests.Session()
session.headers.update(headers)
response = session.get(url, headers=headers, stream=True)

with open("product.zip", "wb") as file:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            file.write(chunk)