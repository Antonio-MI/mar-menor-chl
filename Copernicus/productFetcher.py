import boto3
import datetime
import os
import csv

# Credenciales y configuración de sesión
ACCESS_KEY = 'WE9L7X4K1NR0KPTUB28X'
SECRET_KEY = 'hEVos6faoDpcBJEZX6ufxvQth9TXhPdws9VyHVKK'

session = boto3.session.Session()
s3 = session.resource(
    's3',
    endpoint_url='https://eodata.dataspace.copernicus.eu',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='default'
)

bucket = s3.Bucket("eodata")

fechas_str = [
    '2025-07-28'
]

fechas = [datetime.datetime.strptime(f, "%Y-%m-%d").date() for f in fechas_str]

# Tile ID a buscar
tile_id = "30SXG"

# Prefijos base de búsqueda: L1C_N0500 o L1C
#prefixes = [f"Sentinel-2/MSI/L1C_N0500/{fecha.year}/{fecha.month:02d}/{fecha.day:02d}/" for fecha in fechas]
prefixes = [f"Sentinel-2/MSI/L1C/{fecha.year}/{fecha.month:02d}/{fecha.day:02d}/" for fecha in fechas]

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
