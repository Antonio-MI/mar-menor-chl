import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe 
from matplotlib.colors import ListedColormap, BoundaryNorm
import geopandas as gpd
import fiona
import os

date = "2016-09-08"

# Ruta al KML de batimetría
bathymetry_kml_path = os.path.join(os.path.dirname(__file__), "saved_files/MarMenorBathymetry.kml")

# Leer KML una vez (asumimos EPSG:4326)
# Workaround para Python 3.8.5 con versiones antiguas de fiona
fiona.drvsupport.supported_drivers['KML'] = 'r'
with fiona.open(bathymetry_kml_path, 'r') as src:
    bathymetry_gdf = gpd.GeoDataFrame.from_features(src, crs=src.crs)
bathymetry_gdf = bathymetry_gdf.set_crs("EPSG:4326", allow_override=True)

# Leer y parsear el archivo del colormap
colormap_path = "saved_files/application/colormap_custom.txt"

depths = ["0_1", "1_2", "2_3", "3_4"]
#depths = ["2_3"]
for depth in depths:

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


    #with rasterio.open(f'saved_files/application/{date}_chl_map_{depth}_{MODEL}.tif') as src:
    with rasterio.open(f'saved_files/application/{date}_chl_map_{depth}.tif') as src:
        data = src.read(1)
        raster_crs = src.crs
        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
        nodata = src.nodata

    # Enmascarar nodata / NaN
    if nodata is not None:
        data = np.ma.masked_equal(data, nodata)
    else:
        data = np.ma.masked_invalid(data)

    # Reproyectar KML al CRS del raster
    bathymetry_proj = bathymetry_gdf.to_crs(raster_crs)

    # === Crear figura ===
    fig, ax = plt.subplots(figsize=(8, 6))  # Tamaño ajustado para un solo plot

    # === Mostrar la imagen con colormap personalizado ===
    im = ax.imshow(
        data,
        cmap=custom_cmap,
        norm=norm,
        extent=extent,
        origin="upper",
    )

    # Asegurar que el viewport coincide con el raster
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])

    # === Superponer líneas de batimetría ===
    bathymetry_proj.plot(
        ax=ax,
        color="white",
        linewidth=0.6,
        alpha=0.7,
    )

    # === Etiquetas (usa la columna 'name') ===
    for _, row in bathymetry_proj.iterrows():
        if row.geometry is None:
            continue
        pt = row.geometry.representative_point()
        ax.text(
            pt.x, pt.y,
            str(row.get("name", "")),
            color="white",
            fontsize=8,
            ha="center",
            va="center",
            bbox=dict(facecolor="black", alpha=0.4, edgecolor="none", pad=1),
        )

    # Para que el colorbar solamente se vea en la última figura y no se repita cuatro veces
    if depth == "3_4":
        cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cb.set_ticks(tick_locs)
        cb.set_ticklabels(tick_labels)
        cb.ax.tick_params(labelsize=13)
        cb.ax.text(0.5, 1.02, "Chl mg/m³", fontsize=14, ha='center', va='bottom', transform=cb.ax.transAxes)

    ax.axis('off')

    plt.tight_layout()
    plt.savefig(f'saved_files/application/{date}_chl_map_{depth}.pdf', dpi=300, bbox_inches='tight')
    plt.savefig(f'saved_files/application/{date}_chl_map_{depth}.png', dpi=300, bbox_inches='tight')
    plt.show()



