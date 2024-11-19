
from typing import Any, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

def plot_image(
    image: np.ndarray,
    factor: float = 1.0,
    clip_range: Optional[Tuple[float, float]] = None,
    grid_interval: Optional[int] = None,  # Grid interval in pixels
    **kwargs: Any
) -> None:
    """Utility function for plotting RGB images with optional grid."""
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    
    # Ensure correct aspect ratio and disable interpolation
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, aspect='equal', interpolation='none', **kwargs)
    
    if grid_interval:  # Add grid if specified
        ax.set_xticks(np.arange(0, image.shape[1], grid_interval))
        ax.set_yticks(np.arange(0, image.shape[0], grid_interval))
        ax.grid(color="white", linestyle="-", linewidth=0.5)
    else:  # Remove ticks if no grid
        ax.set_xticks([])
        ax.set_yticks([])