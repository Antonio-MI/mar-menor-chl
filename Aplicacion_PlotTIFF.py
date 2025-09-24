import rasterio
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap, BoundaryNorm

date = ""
depth = ""

# Leer y parsear el archivo del colormap
colormap_path = "saved_files/application/colormap_custom_2.txt"


colors = []
boundaries = []
labels = ["0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0", "1.2", "1.4", "1.6", "1.8", "2.0", "2.4", "2.8", "3.2", "3.6", "4.0", "4.5", "5.0", "6.0", "8.0", "10.0", "12.0", "15.0", "18.0", "24.0", "30.0"]

with open(colormap_path, "r") as f:
    for line in f:
        if line.startswith("#") or "INTERPOLATION" in line:
            continue

        parts = line.strip().split(",")
        if len(parts) < 6:
            continue

        value = float(parts[0])
        r, g, b, a = [int(p) for p in parts[1:5]]
        label = parts[5].strip()

        boundaries.append(value)
        colors.append((r / 255, g / 255, b / 255, a / 255))
        #labels.append(label)

# Crear colormap y norm
custom_cmap = ListedColormap(colors)
norm = BoundaryNorm(boundaries, custom_cmap.N)

# Calcular ubicación de los ticks como puntos medios entre boundaries
tick_locs = [(boundaries[i] + boundaries[i + 1]) / 2 for i in range(len(boundaries) - 1)]
tick_labels = labels[:-1]  # Último valor ("inf") normalmente no se etiqueta
# print(tick_locs)
# print(tick_labels)

with rasterio.open('saved_files/application/chl_pred_0_1.tif') as src:
    data = src.read(1)

# === Crear figura ===
fig, ax = plt.subplots(figsize=(8, 6))  # Tamaño ajustado para un solo plot

# === Mostrar la imagen con colormap personalizado ===
im = ax.imshow(data, cmap=custom_cmap, norm=norm)
ax.set_title('chl_pred_0_1')

# === Añadir colorbar ===
cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cb.set_ticks(tick_locs)
cb.set_ticklabels(tick_labels)
cb.ax.tick_params(labelsize=7)

# === Título encima del colorbar ===
cb.ax.text(0.5, 1.05, "Chl mg/m³", fontsize=8, ha='center', va='bottom', transform=cb.ax.transAxes)

# === Ocultar ejes ===
ax.axis('off')

# === Mostrar y guardar ===
plt.tight_layout()
plt.savefig('saved_files/application/chl_pred_custom_single.png', dpi=300, bbox_inches='tight')
plt.show()




# -------------2 SUBPLOTS-----------
# # === PLOTEO ===
# with rasterio.open('saved_files/application/chl_pred_0_1.tif') as src1, rasterio.open('saved_files/application/chl_pred_1_2.tif') as src2:
#     data1 = src1.read(1)
#     data2 = src2.read(1)

# fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# # === Primer subplot ===
# im1 = axes[0].imshow(data1, cmap=custom_cmap, norm=norm)
# axes[0].set_title('chl_pred_0_1')
# cb1 = plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)
# cb1.set_ticks(tick_locs)
# cb1.set_ticklabels(tick_labels)
# cb1.ax.tick_params(labelsize=7)
# cb1.set_label("Chl mg/m³", fontsize=8, labelpad=5)

# # === Segundo subplot ===
# im2 = axes[1].imshow(data2, cmap=custom_cmap, norm=norm)
# axes[1].set_title('chl_pred_1_2')
# cb2 = plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)
# cb2.set_ticks(tick_locs)
# cb2.set_ticklabels(tick_labels)
# cb2.ax.tick_params(labelsize=7)
# cb2.set_label("Chl mg/m³", fontsize=8, labelpad=5)

# for ax in axes:
#     ax.axis('off')

# plt.tight_layout()
# plt.savefig('saved_files/application/chl_pred_custom.png', dpi=300, bbox_inches='tight')
# plt.show()