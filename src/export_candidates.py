from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from skimage.filters import gaussian
from skimage.measure import label, regionprops
from skimage.morphology import disk, opening, remove_small_objects


PROJECT_DIR = Path(__file__).resolve().parents[1]
IMAGE_PATH = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "sentinel1_mumbai"
    / "2026-09-06-00_00_2026-09-06-23_59_Sentinel-1_IW_VV_VH_VV_-_decibel_gamma0.tiff"
)
OUTPUT_PATH = PROJECT_DIR / "outputs" / "candidate_regions.csv"


def main():
    with rasterio.open(IMAGE_PATH) as source:
        image = source.read(1).astype(float)
        transform = source.transform

    smoothed = gaussian(image, sigma=2, preserve_range=True)
    valid_pixels = smoothed[image > 0]
    threshold = np.percentile(valid_pixels, 15)

    dark_mask = (image > 0) & (smoothed < threshold)
    clean_mask = opening(dark_mask, footprint=disk(1))
    clean_mask = remove_small_objects(clean_mask, max_size=50)

    labelled = label(clean_mask)
    records = []

    for region in regionprops(labelled):
        if 50 <= region.area <= 200_000:
            row, column = region.centroid
            longitude, latitude = rasterio.transform.xy(
                transform, row, column
            )

            records.append(
                {
                    "candidate_id": f"C{len(records) + 1:02d}",
                    "latitude": round(latitude, 6),
                    "longitude": round(longitude, 6),
                    "area_pixels": region.area,
                    "low_backscatter_threshold": round(float(threshold), 6),
                }
            )

    candidates = pd.DataFrame(records)
    candidates = candidates.sort_values(
        "area_pixels", ascending=False
    ).reset_index(drop=True)

    candidates.to_csv(OUTPUT_PATH, index=False)

    print(f"Candidates exported: {len(candidates)}")
    print(candidates.to_string(index=False))
    print(f"Saved file: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()