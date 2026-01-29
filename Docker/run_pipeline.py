import argparse
import yaml
import subprocess
import time
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--date", required=True)
parser.add_argument("--config", default="config.yaml")
args = parser.parse_args()

with open(args.config, "r") as f:
    cfg = yaml.safe_load(f)

fecha = args.date
safe_dir = cfg.get("safe_dir")
snap_dir = cfg.get("snap_dir")
model_dir = cfg.get("model_dir")
pred_dir = cfg.get("pred_dir")
map_dir = cfg.get("map_dir")
geojson_file = cfg.get("geojson_file")
colormap_file = cfg.get("colormap_file")
bathymetry_map = cfg.get("bathymetry_map")

# === [0] Inicio del pipeline ===
t_start = time.time()

print(f"\n=== [1] Descargando producto para {fecha} ===")
t1 = time.time()
try:
    subprocess.run(["python3", "fetch/productFetcher.py", "--date", fecha, "--output", safe_dir], check=True)
except subprocess.CalledProcessError:
    print("No se encontraron productos para esa fecha. El pipeline se detendrá.")
    sys.exit(1)
subprocess.run(["python3", "fetch/productFetcher_tozip.py", "--date", fecha, "--input", safe_dir], check=True)
t2 = time.time()
print(f"Tiempo transcurrido [1]: {t2 - t1:.2f} s")

print(f"\n=== [2] Aplicando corrección atmosférica con SNAP ===")
t3 = time.time()
subprocess.run(["bash", "fetch/snap_batch_application.sh", fecha, safe_dir, snap_dir], check=True)
t4 = time.time()
print(f"Tiempo transcurrido [2]: {t4 - t3:.2f} s")

print(f"\n=== [3] Ejecutando modelos de predicción ===")
t5 = time.time()
subprocess.run(["python3", "models/Aplicacion_Modelos.py", "--date", fecha, "--input", snap_dir, "--models", model_dir, "--pred", pred_dir, "--geojson", geojson_file], check=True)
t6 = time.time()
print(f"Tiempo transcurrido [3]: {t6 - t5:.2f} s")

print(f"\n=== [4] Generando TIFFs ===")
t7 = time.time()
subprocess.run(["python3", "models/Aplicacion_TIFFfromCSV.py", "--date", fecha, "--input", pred_dir, "--output", map_dir], check=True)
t8 = time.time()
print(f"Tiempo transcurrido [4]: {t8 - t7:.2f} s")

if cfg.get("plot_individuales", False):
    print(f"\n=== [5] Generando plots individuales ===")
    t9 = time.time()
    subprocess.run(["python3", "models/Aplicacion_PlotTIFF.py", "--date", fecha, "--input", map_dir, "--output", map_dir, "--colormap", colormap_file, "--bathymetry", bathymetry_map], check=True)
    t10 = time.time()
    print(f"Tiempo transcurrido [5]: {t10 - t9:.2f} s")

if cfg.get("generate_gif", False):
    print(f"\n=== [6] Generando GIF ===")
    t11 = time.time()
    subprocess.run(["python3", "models/Aplicacion_GenerateGif.py", "--date", fecha, "--input", map_dir, "--output", map_dir, "--colormap", colormap_file], check=True)
    t12 = time.time()
    print(f"Tiempo transcurrido [6]: {t12 - t11:.2f} s")

t_end = time.time()
print("\n Pipeline completado correctamente.")
print(f"Tiempo total del pipeline: {(t_end - t_start)/60:.2f} min")
