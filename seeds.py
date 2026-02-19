import numpy as np

n_seeds = 50
rng = np.random.default_rng(42)  # Seed maestra para reproducibilidad
seeds = rng.integers(0, 10000, size=n_seeds) # rng.integers(10001, 20000, size=n_seeds)

# Guardar las semillas en un archivo txt
with open("input_file_seeds.txt", "w") as f:
    for s in seeds:
        f.write(f"{s}\n")

print("File created")
