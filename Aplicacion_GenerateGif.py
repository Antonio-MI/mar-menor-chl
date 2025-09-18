import rasterio
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

def read_tif_as_array(filename):
    with rasterio.open(filename) as src:
        return src.read(1)

data1 = read_tif_as_array('chl_pred_0_1.tif')
data2 = read_tif_as_array('chl_pred_1_2.tif')

vmin = np.nanmin([np.nanmin(data1), np.nanmin(data2)])
vmax = np.nanmax([np.nanmax(data1), np.nanmax(data2)])

frames = []
for idx, data in enumerate([data1, data2], start=1):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(data, cmap='viridis', vmin=vmin, vmax=vmax)
    ax.axis('off')
    ax.text(1.05, 0.95, f'Deep {str(idx)}', color='white', fontsize=32, fontweight='bold',
            ha='left', va='top', transform=ax.transAxes, bbox=dict(facecolor='black', alpha=0.5, boxstyle='round,pad=0.3'))
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    canvas.draw()
    img = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    img_rgb = img[..., :3]
    frames.append(Image.fromarray(img_rgb))
    plt.close(fig)

frames[0].save('chl_pred_loop.gif', save_all=True, append_images=frames[1:], duration=1000, loop=0)