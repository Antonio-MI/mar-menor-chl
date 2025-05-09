import os
import shutil

# Ruta donde están las carpetas SAFE descargadas
input_dir = "SAFE_downloads"

# Recorremos todos los elementos en la carpeta
for item in os.listdir(input_dir):
    item_path = os.path.join(input_dir, item)

    # Solo procesar carpetas que acaban en .SAFE
    if os.path.isdir(item_path) and item.endswith(".SAFE"):
        zip_path = os.path.join(input_dir, item + ".zip")
        
        if not os.path.exists(zip_path):
            print(f"Comprimiendo {item_path} → {zip_path}")
            shutil.make_archive(base_name=zip_path[:-4], format="zip", root_dir=input_dir, base_dir=item)
        else:
            print(f"{zip_path} ya existe. Saltando.")
