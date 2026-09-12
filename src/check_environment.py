"""Small environment check for the Oil Spill Attribution MVP."""

import sys


def main() -> None:
    print(f"Python: {sys.version.split()[0]}")
    packages = ("numpy", "pandas", "matplotlib", "geopandas", "rasterio", "folium")
    for package in packages:
        __import__(package)
        print(f"OK: {package}")

    print("Environment is ready for the first SAR-image notebook.")


if __name__ == "__main__":
    main()
