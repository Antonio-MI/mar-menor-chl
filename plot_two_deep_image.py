import rasterio
import numpy as np
import matplotlib.pyplot as plt

with rasterio.open('chl_pred_0_1.tif') as src1, rasterio.open('chl_pred_1_2.tif') as src2:
    data1 = src1.read(1)
    data2 = src2.read(1)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

im1 = axes[0].imshow(data1, cmap='viridis')
axes[0].set_title('chl_pred_0_1')
plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

im2 = axes[1].imshow(data2, cmap='viridis')
axes[1].set_title('chl_pred_1_2')
plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)

for ax in axes:
    ax.axis('off')

plt.tight_layout()
plt.savefig('chl_pred_viridis.png', dpi=300, bbox_inches='tight')
plt.show()