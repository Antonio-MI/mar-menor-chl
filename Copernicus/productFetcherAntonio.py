"""

************************************************************************************************************************
                                                    PRODUCT FETCHER
************************************************************************************************************************

Product fetcher es un script dedicado a descargar productos .SAFE del bucket S3 de Copernicus. Necesita un token de
acceso generado en la propia web de Copernicus y una lista de fechas a descargar.

Por defecto, va a descargar imágenes de la casilla del mar menor, la 30SXG, pero tanto ésta como la región se pueden
cambiar para obtener imágenes de otros lugares.

Genera un .csv residual con los nombres de los productos dentro del bucket S3, además de una carpeta con todos los
productos .SAFE descargados para esas fechas.

"""





import subprocess
import boto3
from botocore.config import Config
import os
import datetime
import csv

# Configuración de credenciales y cliente S3
ACCESS_KEY = 'R502RC3I5CM1WYTESZ61'
SECRET_KEY = 'fPkfpmxGtO9NH3DijrC0xnEzngbExPP4II2i79KY'

s3 = boto3.client(
    's3',
    region_name='eu-central-1',
    endpoint_url='https://eodata.dataspace.copernicus.eu',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4')
)

# Lista de fechas en formato string
# fechas_str = ["2017-06-30", "2018-01-31", "2018-02-20", "2018-03-07", "2018-05-11", "2018-05-16", "2018-06-20",
#               "2018-07-10", "2018-08-09", "2018-08-14", "2018-08-29", "2018-10-03", "2018-11-07", "2019-02-20",
#               "2019-03-12", "2019-06-25", "2019-07-10", "2019-08-14", "2019-09-18", "2019-10-03", "2019-11-27",
#               "2020-02-20", "2020-02-25", "2020-03-11", "2020-05-05", "2020-05-20", "2020-08-13", "2020-12-21",
#               "2021-01-05", "2021-04-20", "2021-06-14", "2021-07-14", "2021-08-03", "2021-08-13", "2021-11-11",
#               "2021-12-01", "2022-02-24", "2022-06-24", "2022-07-14", "2022-08-03", "2022-09-07", "2023-01-10",
#               "2023-01-20", "2023-03-01", "2023-03-16", "2023-04-20", "2023-05-25", "2023-07-19", "2023-09-07",
#               "2023-09-27", "2023-11-16", "2024-04-24", "2024-05-29", "2024-06-18", "2024-07-03", "2024-07-18"]
fechas_str = ["2017-06-30", "2018-01-31", "2018-03-07", "2018-05-11", "2018-05-16", 
              "2018-07-10", "2018-08-09", "2018-08-14", "2018-10-03", "2019-02-20", "2019-06-25", "2019-07-10",
              "2020-02-20", "2020-02-25", "2020-05-20", "2020-08-13", "2020-12-21",
              "2021-01-05", "2021-06-14", "2021-07-14", "2021-08-03", "2021-08-13", "2021-11-11",
              "2021-12-01", "2022-02-24", "2022-06-24", "2022-08-03", "2022-09-07", "2023-01-10",
              "2023-01-20", "2023-03-01", "2023-04-20", "2023-05-25", "2023-07-19", "2023-09-07",
              "2023-09-27", "2023-11-16", "2024-04-24", "2024-05-29", "2024-06-18", "2024-07-03", "2024-07-18"]

fechas_str = ["2017-06-30", "2018-01-31", "2018-03-07"]

# Convertir las fechas a objetos datetime.date
fechas = [datetime.datetime.strptime(f, "%Y-%m-%d").date() for f in fechas_str]

# Tile ID específico
tile_id = "30SXG"

# Construir prefijos basados en las fechas y el tile ID
prefixes = [f"Sentinel-2/MSI/L1C_N0500/{fecha.year}/{fecha.month:02d}/{fecha.day:02d}/" for fecha in fechas]



def download_safe_files(prefixes):
    products = []

    for prefix in prefixes:
        print(f"\n Buscando en: {prefix}")
        paginator = s3.get_paginator('list_objects_v2')

        # Buscar los objetos dentro del prefijo especificado
        most_recent_file = None
        product = ""

        for page in paginator.paginate(Bucket='eodata', Prefix=prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                # Solo considerar los archivos con el sufijo '.SAFE'
                if key.endswith('.SAFE/') and tile_id in key:
                    products.append(key)
                    break

    # Guardar los productos en un archivo CSV
    with open('productos.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Product'])  # Escribir encabezado
        for product in products:
            writer.writerow([product])  # Escribir cada producto en una fila

    print(f"Productos guardados en 'productos.csv'.")

    # Proceder con la descarga
    for p in products:
        pName = 's3://eodata/' + p
        download_dir = 'SAFE_downloads/' + p.rstrip('/').rsplit('/', 1)[-1]
        print(download_dir)

        # Comprobar si el directorio ya existe
        if not os.path.exists(download_dir):
            # Si el directorio no existe, crearlo
            os.makedirs(download_dir)
            print(f"Carpeta creada: {download_dir}")
            #subprocess.run(['s3cmd', 'get', '--recursive', '--continue', pName, download_dir], capture_output=True, text=True)
            result = subprocess.run(
                ['s3cmd', 'get', '--recursive', '--continue', pName, download_dir],
                capture_output=True,
                text=True
            )
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")

        else:
            print(f"Carpeta ya existe: {download_dir}")


# Ejecutar la descarga
download_safe_files(prefixes)
