import boto3
import datetime
import os
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True, type=str, help="Fecha del producto a descargar (YYYY-MM-DD)")
parser.add_argument("--output", required=False, help="Directorio donde guardar el .SAFE")
args = parser.parse_args()

# Credenciales desde el entorno (docker --env-file .env)
ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
SECRET_KEY = os.getenv("S3_SECRET_KEY")

if not ACCESS_KEY or not SECRET_KEY:
    raise EnvironmentError("No se encontraron los credenciales de S3 en el entorno o .env")

# Cliente S3 de Copernicus Data Space Ecosystem
s3 = boto3.client(
    's3',
    endpoint_url='https://eodata.dataspace.copernicus.eu',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='default',
)
BUCKET = "eodata"

date_str = str(args.date)
fechas = [datetime.datetime.strptime(date_str, "%Y-%m-%d").date()]

# Tile ID a buscar
tile_id = "30SXG"
# Órbita que cubre por completo el Mar Menor (S2 ~10:46). La órbita adyacente
# (p. ej. R094) solo roza el borde del tile y produce una escena casi vacía.
preferred_orbit = "R051"

# Carpeta local destino
output_dir = args.output

# Prefijos base de búsqueda: primero L1C_N0500 (baselines antiguos), luego L1C
prefix_patterns = [
    "Sentinel-2/MSI/L1C_N0500/{y}/{m:02d}/{d:02d}/",
    "Sentinel-2/MSI/L1C/{y}/{m:02d}/{d:02d}/"
]


def list_subfolders(prefix):
    """Subcarpetas (CommonPrefixes) bajo 'prefix' con navegación jerárquica (Delimiter='/').

    CDSE sirve eodata como un almacén jerárquico: el listado plano ya no
    devuelve nada y los marcadores '.SAFE/' de carpeta han desaparecido, así
    que hay que navegar con Delimiter.
    """
    paginator = s3.get_paginator('list_objects_v2')
    subfolders = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix, Delimiter='/'):
        for cp in page.get('CommonPrefixes', []):
            subfolders.append(cp['Prefix'])
    return subfolders


def iter_files(prefix):
    """Genera recursivamente todas las claves de fichero bajo 'prefix'."""
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix, Delimiter='/'):
        for obj in page.get('Contents', []):
            if not obj['Key'].endswith('/'):  # ignorar marcadores de carpeta
                yield obj['Key']
        for cp in page.get('CommonPrefixes', []):
            yield from iter_files(cp['Prefix'])


def find_product(prefix, tile_id, preferred_orbit=None):
    """Devuelve el prefijo de la carpeta .SAFE con el tile buscado.

    Si hay varios productos para el tile (habitual ahora: R051 + una órbita
    adyacente), prioriza 'preferred_orbit'.
    """
    candidates = [
        p for p in list_subfolders(prefix)
        if p.rstrip('/').endswith('.SAFE') and tile_id in p
    ]
    if not candidates:
        return None
    if preferred_orbit:
        preferidos = [p for p in candidates if f"_{preferred_orbit}_" in p]
        if preferidos:
            return sorted(preferidos)[0]
    return sorted(candidates)[0]


def download_product(product_prefix, target_root):
    """Descarga recursivamente todos los ficheros del producto SAFE."""
    local_target = os.path.join(target_root, os.path.basename(product_prefix.rstrip('/')))
    for key in iter_files(product_prefix):
        local_path = os.path.join(local_target, os.path.relpath(key, product_prefix))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        print(f"Descargando {key} → {local_path}")
        s3.download_file(BUCKET, key, local_path)
    return product_prefix


def main():
    os.makedirs(output_dir, exist_ok=True)
    productos_encontrados = []

    for fecha in fechas:
        print(f"\nProcesando fecha {fecha.strftime('%Y-%m-%d')}")

        # probar cada patrón en orden
        for pattern in prefix_patterns:
            prefix = pattern.format(y=fecha.year, m=fecha.month, d=fecha.day)
            print(f"Buscando productos en: {prefix}")

            product = find_product(prefix, tile_id, preferred_orbit)
            if product:
                print(f"Producto encontrado: {product}")
                download_product(product, output_dir)
                productos_encontrados.append(product)
                break  # rompe el bucle interno si se encontró algo
            else:
                print(f"No se encontró producto SAFE con tile {tile_id} en {prefix}")
        else:
            # Este else del for se ejecuta solo si NO se ejecutó 'break'
            print(f"No se encontró ningún producto para la fecha {fecha.strftime('%Y-%m-%d')} en ninguno de los prefijos.")

    if productos_encontrados:
        print(f"\nSe descargó el producto para la fecha buscada.")
        sys.exit(0)
    else:
        print("\nNo se descargó ningún producto.")
        sys.exit(1)


if __name__ == "__main__":
    main()
