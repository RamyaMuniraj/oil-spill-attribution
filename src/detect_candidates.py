from pathlib import Path

import matplotlib.pyplot as plt
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

OUTPUT_PATH = PROJECT_DIR / "outputs" / "candidate_regions.png"


def main():

    # 1. Read Sentinel-1 image
    with rasterio.open(IMAGE_PATH) as source:
        image = source.read(1).astype(float)

    # 2. Smooth SAR image
    smoothed = gaussian(
        image,
        sigma=2,
        preserve_range=True
    )

    # 3. Calculate threshold
    valid_pixels = smoothed[image > 0]

    threshold = np.percentile(
        valid_pixels,
        15
    )

    # 4. Detect dark regions
    dark_mask = (
        (image > 0)
        & (smoothed < threshold)
    )

    # 5. Clean mask
    clean_mask = opening(
        dark_mask,
        footprint=disk(1)
    )

    clean_mask = remove_small_objects(
        clean_mask,
        max_size=50
    )

    # 6. Connected components
    labelled = label(clean_mask)
    regions = regionprops(labelled)

    # 7. Extract candidates
    filtered_mask = np.zeros_like(
        clean_mask,
        dtype=bool
    )

    candidates = []

    for region in regions:

        if 50 <= region.area <= 200_000:

            filtered_mask[
                labelled == region.label
            ] = True

            perimeter = region.perimeter
            major_axis = region.axis_major_length
            minor_axis = region.axis_minor_length

            if minor_axis > 0:
                aspect_ratio = (
                    major_axis / minor_axis
                )
            else:
                aspect_ratio = 0

            if perimeter > 0:
                compactness = (
                    4 * np.pi * region.area
                ) / (perimeter ** 2)
            else:
                compactness = 0

            candidates.append({
                "label": region.label,
                "area_pixels": region.area,
                "perimeter_pixels": perimeter,
                "major_axis_pixels": major_axis,
                "minor_axis_pixels": minor_axis,
                "aspect_ratio": aspect_ratio,
                "compactness": compactness,
                "solidity": region.solidity,
                "centroid_row": region.centroid[0],
                "centroid_col": region.centroid[1],
            })

    print(
        f"Low-backscatter threshold: {threshold:.4f}"
    )

    print(
        f"Candidate regions found: {len(candidates)}"
    )

    # 8. Save geometry
    geometry_df = pd.DataFrame(candidates)

    geometry_output = (
        PROJECT_DIR
        / "outputs"
        / "candidate_geometry.csv"
    )

    geometry_df.to_csv(
        geometry_output,
        index=False
    )

    print(
        f"Saved candidate geometry: "
        f"{geometry_output}"
    )

    # 9. Visualization
    display_pixels = image[image > 0]

    low, high = np.percentile(
        display_pixels,
        (2, 98)
    )

    plt.figure(
        figsize=(10, 8)
    )

    plt.imshow(
        image,
        cmap="gray",
        vmin=low,
        vmax=high
    )

    plt.contour(
        filtered_mask,
        colors="red",
        linewidths=0.8
    )

    plt.title(
        "Preliminary Low-Backscatter Candidates"
    )

    plt.axis("off")
    plt.tight_layout()

    plt.savefig(
        OUTPUT_PATH,
        dpi=200
    )

    print(
        f"Saved result: {OUTPUT_PATH}"
    )

    plt.show()


if __name__ == "__main__":
    main()