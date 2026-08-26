import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import random
import os

# Set a random seed so our scientific results are reproducible
np.random.seed(42)
random.seed(42)

def generate_negative_samples():
    geojson_path = "data/processed/ner_landslides.geojson"
    output_csv_path = "data/processed/ml_master_dataset.csv"

    if not os.path.exists(geojson_path):
        raise FileNotFoundError(f"Missing {geojson_path}. Run script 01 first.")

    print("Loading positive samples (Historical Landslides)...")
    positives_gdf = gpd.read_file(geojson_path)
    
    # 1. Standardize the positive dataset
    positives_gdf['label'] = 1  # 1 = Landslide
    
    # NER Bounding box (same as Script 01)
    MIN_LONGITUDE, MAX_LONGITUDE = 87.8, 97.5
    MIN_LATITUDE, MAX_LATITUDE = 21.5, 29.5

    # 2. Create a buffer zone around known landslides
    # 1 degree of latitude/longitude is roughly 111 km. 
    # 0.05 degrees is roughly 5.5 kilometers.
    # We consider any area within 5.5km of a historical landslide as "unsafe" 
    # and will not use it as a negative sample.
    BUFFER_DEGREES = 0.05
    hazard_zones = positives_gdf.geometry.buffer(BUFFER_DEGREES).unary_union

    negative_points = []
    num_positives = len(positives_gdf)
    
    print(f"Generating {num_positives} negative samples (Safe zones)...")
    
    # 3. Generate random points until we have enough valid ones
    attempts = 0
    while len(negative_points) < num_positives:
        attempts += 1
        # Generate a random coordinate
        rand_lon = random.uniform(MIN_LONGITUDE, MAX_LONGITUDE)
        rand_lat = random.uniform(MIN_LATITUDE, MAX_LATITUDE)
        random_point = Point(rand_lon, rand_lat)

        # Check if the point is safely outside the hazard zones
        if not hazard_zones.contains(random_point):
            negative_points.append({
                'latitude': rand_lat,
                'longitude': rand_lon,
                'label': 0  # 0 = No Landslide
            })
            
        # Safety break to prevent infinite loops
        if attempts > 100000:
            print("Warning: Taking too long to find safe points.")
            break

    print(f"Successfully generated {len(negative_points)} negative samples in {attempts} attempts.")

    # 4. Combine into a single master DataFrame
    negatives_df = pd.DataFrame(negative_points)
    
    # Extract lat/lon from our positive GeoDataFrame to match the structure
    positives_df = pd.DataFrame({
        'latitude': positives_gdf.geometry.y,
        'longitude': positives_gdf.geometry.x,
        'label': 1
    })

    master_df = pd.concat([positives_df, negatives_df], ignore_index=True)

    # 5. Shuffle the dataset so 1s and 0s are mixed up
    # frac=1 means return 100% of the data, but shuffled
    master_df = master_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # 6. Save to disk
    master_df.to_csv(output_csv_path, index=False)
    print(f"\nSaved ML Master Dataset with {len(master_df)} total records to:")
    print(f" - {output_csv_path}")
    print("\nClass distribution:")
    print(master_df['label'].value_counts())

if __name__ == "__main__":
    generate_negative_samples()