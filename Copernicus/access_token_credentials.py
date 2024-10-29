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
    print(f"Access token: {access_token}")
else:
    print("Failed to retrieve access token.")
