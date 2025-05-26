import boto3
import datetime
import os
import csv

# Credenciales y configuración de sesión
ACCESS_KEY = 'R502RC3I5CM1WYTESZ61'
SECRET_KEY = 'fPkfpmxGtO9NH3DijrC0xnEzngbExPP4II2i79KY'

session = boto3.session.Session()
s3 = session.resource(
    's3',
    endpoint_url='https://eodata.dataspace.copernicus.eu',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='default'
)

bucket = s3.Bucket("eodata")

# Fechas ya descargadas
# fechas_str = ["2017-06-30", "2018-01-31", "2018-02-20", "2018-03-07", "2018-05-11", "2018-05-16", "2018-06-20", "2018-07-10", "2018-08-09", "2018-08-14", "2018-08-29", "2018-10-03", "2018-11-07", "2019-02-20", "2019-03-12", "2019-06-25", "2019-07-10", "2019-08-14", "2019-09-18", "2019-10-03", "2019-11-27", "2020-02-20", "2020-03-11", "2020-05-20", "2021-01-05", "2021-04-20", "2021-06-14", "2021-07-14", "2021-08-03", "2021-08-13", "2021-11-11", "2021-12-01", "2022-02-24", "2022-06-24", "2022-08-03", "2022-09-07", "2023-01-10", "2023-01-20", "2023-03-01", "2023-03-16", "2023-04-20", "2023-05-25", "2023-07-19", "2023-09-07", "2023-09-27", "2023-11-16"]
# Otra tanda
fechas_str = ["2017-09-11", "2019-11-07", "2020-02-25", "2020-05-05", "2020-06-02", "2020-08-13", "2020-12-21", "2021-01-13", "2021-09-27", "2022-07-14"]

fechas = [datetime.datetime.strptime(f, "%Y-%m-%d").date() for f in fechas_str]

# Tile ID a buscar
tile_id = "30SXG"

# Prefijos base de búsqueda
prefixes = [f"Sentinel-2/MSI/L1C_N0500/{fecha.year}/{fecha.month:02d}/{fecha.day:02d}/" for fecha in fechas]

# Carpeta local destino
output_dir = "SAFE_downloads"


def download_product(bucket, prefix: str, tile_id: str, target_root: str):
    """
    Busca y descarga un producto SAFE que contenga el tile_id en el prefijo dado.
    Devuelve el nombre del producto descargado o None si no encuentra nada.
    """
    for obj in bucket.objects.filter(Prefix=prefix):
        if obj.key.endswith('.SAFE/') and tile_id in obj.key:
            product_prefix = obj.key
            print(f"Producto encontrado: {product_prefix}")
            local_target = os.path.join(target_root, os.path.basename(product_prefix.rstrip('/')))
            for file_obj in bucket.objects.filter(Prefix=product_prefix):
                local_path = os.path.join(local_target, os.path.relpath(file_obj.key, product_prefix))
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                if not file_obj.key.endswith('/'):  # evitar carpetas virtuales
                    print(f"Descargando {file_obj.key} → {local_path}")
                    bucket.download_file(file_obj.key, local_path)
            return product_prefix
    print(f"No se encontró producto SAFE con tile {tile_id} en {prefix}")
    return None


def main():
    os.makedirs(output_dir, exist_ok=True)
    productos_encontrados = []

    for prefix in prefixes:
        print(f"\nBuscando productos en: {prefix}")
        result = download_product(bucket, prefix, tile_id, output_dir)
        if result:
            productos_encontrados.append(result)

    # Guardar en CSV los productos descargados
    if productos_encontrados:
        with open('productos.csv', mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Product'])
            for p in productos_encontrados:
                writer.writerow([p])
        print(f"\n{len(productos_encontrados)} productos descargados. Guardados en 'productos.csv'.")
    else:
        print("\nNo se descargó ningún producto.")

if __name__ == "__main__":
    main()
