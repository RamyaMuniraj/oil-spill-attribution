from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio


PROJECT_DIR = Path(__file__).resolve().parents[1]
IMAGE_PATH = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "sentinel1_mumbai"
    / "2026-09-06-00_00_2026-09-06-23_59_Sentinel-1_IW_VV_VH_VV_-_decibel_gamma0.tiff"
)
OUTPUT_PATH = PROJECT_DIR / "outputs" / "sar_vv_backscatter.png"


def main():
    with rasterio.open(IMAGE_PATH) as source:
        image = source.read(1).astype(float)

        print("Image size:", source.width, "x", source.height, "pixels")
        print("Coordinate system:", source.crs)
        print("Value range:", np.nanmin(image), "to", np.nanmax(image), "dB")

    low, high = np.nanpercentile(image, (2, 98))

    plt.figure(figsize=(10, 8))
    plt.imshow(image, cmap="gray", vmin=low, vmax=high)
    plt.colorbar(label="VV backscatter (dB)")
    plt.title("Sentinel-1 VV Radar Backscatter — Arabian Sea")
    plt.axis("off")
    plt.tight_layout()

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=200)
    print(f"Saved image: {OUTPUT_PATH}")

    plt.show()


if __name__ == "__main__":
    main()