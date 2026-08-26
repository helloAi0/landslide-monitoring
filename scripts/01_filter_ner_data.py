import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

def filter_ner_landslides():
    print("Loading global landslide dataset...")
    raw_data_path = "data/raw/nasa_global_landslides.csv"
    processed_csv_path = "data/processed/ner_landslides.csv"
    processed_geojson_path = "data/processed/ner_landslides.geojson"

    # 1. Load the CSV
    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(f"Missing file: {raw_data_path}. Did you download it?")
    
    df = pd.read_csv(raw_data_path)
    
    # 2. Clean missing coordinates
    # We cannot plot or use data that lacks latitude or longitude
    initial_count = len(df)
    df = df.dropna(subset=['latitude', 'longitude'])
    print(f"Dropped {initial_count - len(df)} records missing coordinates.")

    # 3. Define North Eastern Region (NER) India Bounding Box
    # Coordinates roughly covering Sikkim, Assam, Arunachal, Meghalaya, Nagaland, Manipur, Mizoram, Tripura
    MIN_LONGITUDE = 87.8  # West of Sikkim
    MAX_LONGITUDE = 97.5  # East of Arunachal Pradesh
    MIN_LATITUDE = 21.5   # South of Mizoram
    MAX_LATITUDE = 29.5   # North of Arunachal Pradesh

    # 4. Filter using Pandas (Fast spatial bounding box filter)
    ner_df = df[
        (df['longitude'] >= MIN_LONGITUDE) & 
        (df['longitude'] <= MAX_LONGITUDE) & 
        (df['latitude'] >= MIN_LATITUDE) & 
        (df['latitude'] <= MAX_LATITUDE)
    ].copy()

    print(f"Filtered down to {len(ner_df)} landslides in the NER region.")

    if len(ner_df) == 0:
        print("Warning: No records found. Check your bounding box or dataset.")
        return

    # 5. Convert to a GeoPandas GeoDataFrame (Standard for GIS)
    # This turns separate lat/lon columns into a unified 'geometry' object
    geometry = [Point(xy) for xy in zip(ner_df['longitude'], ner_df['latitude'])]
    
    # EPSG:4326 is the standard coordinate reference system (CRS) for GPS coordinates (WGS84)
    ner_gdf = gpd.GeoDataFrame(ner_df, geometry=geometry, crs="EPSG:4326")

    # 6. Save the processed data
    # Save as CSV for ML training later
    ner_df.to_csv(processed_csv_path, index=False)
    
    # Save as GeoJSON for our Next.js/Leaflet web map later
    ner_gdf.to_file(processed_geojson_path, driver="GeoJSON")

    print(f"Success! Saved clean data to:")
    print(f" - {processed_csv_path}")
    print(f" - {processed_geojson_path}")

if __name__ == "__main__":
    filter_ner_landslides()