import os
import sys
import pandas as pd
import numpy as np

# Define paths relative to backend directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
RAW_DATA_PATH = os.path.join(BACKEND_DIR, "data", "raw", "nasa_global_landslides.csv")
PROCESSED_DATA_PATH = os.path.join(BACKEND_DIR, "data", "processed", "processed_landslides.csv")

# Bounding box for North Eastern Region (NER) of India
# Lat: 21.5°N to 29.5°N | Lon: 87.5°E to 97.5°E
NER_BOUNDS = {
    "lat_min": 21.5,
    "lat_max": 29.5,
    "lon_min": 87.5,
    "lon_max": 97.5
}

def estimate_terrain_features(lat, lon):
    """
    Estimates topographically plausible Elevation (m) and Slope (deg) 
    based on geographic coordinates in the NER region.
    - Northern & eastern hilly regions (Arunachal, Sikkim) have high elevation/slope.
    - Central valley (Assam Brahmaputra valley) has lower elevation/slope.
    """
    # Base elevation gradient towards northern/eastern Himalayas
    lat_norm = (lat - NER_BOUNDS["lat_min"]) / (NER_BOUNDS["lat_max"] - NER_BOUNDS["lat_min"])
    lon_norm = (lon - NER_BOUNDS["lon_min"]) / (NER_BOUNDS["lon_max"] - NER_BOUNDS["lon_min"])
    
    elevation = 150 + 3200 * (0.6 * lat_norm + 0.4 * lon_norm) + np.random.normal(0, 50)
    elevation = max(50.0, float(elevation))
    
    # Steeper slopes correlate with higher elevation
    slope = 2.0 + (elevation / 120.0) + np.random.normal(0, 3.0)
    slope = np.clip(slope, 1.0, 65.0)
    
    return round(elevation, 2), round(slope, 2)

def run_data_pipeline():
    print("=" * 60)
    print("RUNNING LANDSLIDE GEOSPATIAL DATA PIPELINE")
    print("=" * 60)

    if not os.path.exists(RAW_DATA_PATH):
        print(f"ERROR: Raw data file not found at: {RAW_DATA_PATH}")
        sys.exit(1)

    print(f"Loading raw NASA catalog from: {RAW_DATA_PATH}")
    df_raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    print(f"Total raw records in catalog: {len(df_raw)}")

    # Clean column headers
    df_raw.columns = [col.strip().lower() for col in df_raw.columns]

    # Flexible column selection for coordinates and dates
    lat_col = 'latitude' if 'latitude' in df_raw.columns else 'lat'
    lon_col = 'longitude' if 'longitude' in df_raw.columns else 'lon'
    date_col = 'event_date' if 'event_date' in df_raw.columns else 'submitted_date'

    # Filter out missing lat/lon
    df_clean = df_raw.dropna(subset=[lat_col, lon_col]).copy()
    df_clean[lat_col] = pd.to_numeric(df_clean[lat_col], errors='coerce')
    df_clean[lon_col] = pd.to_numeric(df_clean[lon_col], errors='coerce')
    df_clean = df_clean.dropna(subset=[lat_col, lon_col])

    # Filter spatially for North Eastern Region (NER) of India
    ner_mask = (
        (df_clean[lat_col] >= NER_BOUNDS["lat_min"]) & 
        (df_clean[lat_col] <= NER_BOUNDS["lat_max"]) &
        (df_clean[lon_col] >= NER_BOUNDS["lon_min"]) & 
        (df_clean[lon_col] <= NER_BOUNDS["lon_max"])
    )
    df_ner = df_clean[ner_mask].copy()
    print(f"Landslide records located within NER India: {len(df_ner)}")

    # Process Positive Samples (is_landslide = 1)
    positive_records = []
    np.random.seed(42)

    for _, row in df_ner.iterrows():
        lat = float(row[lat_col])
        lon = float(row[lon_col])
        
        # Parse date / month
        try:
            date_val = pd.to_datetime(row[date_col])
            month = date_val.month
        except Exception:
            month = np.random.choice([6, 7, 8, 9]) # Default to monsoon season

        elevation, slope = estimate_terrain_features(lat, lon)
        
        # Landslides correlate with heavy monsoon rainfall
        daily_rain = np.random.gamma(shape=5.0, scale=12.0) + 20.0
        rain_3d = daily_rain + np.random.gamma(shape=4.0, scale=10.0) + 15.0
        rain_7d = rain_3d + np.random.gamma(shape=4.0, scale=12.0) + 20.0

        positive_records.append({
            'latitude': lat,
            'longitude': lon,
            'month': month,
            'elevation': elevation,
            'slope': slope,
            'daily_rainfall': round(daily_rain, 2),
            'cumulative_rainfall_3d': round(rain_3d, 2),
            'cumulative_rainfall_7d': round(rain_7d, 2),
            'is_landslide': 1
        })

    # Generate Negative Samples (is_landslide = 0) to balance dataset
    num_negatives = max(len(positive_records) * 3, 500) # Ensure sufficient sample size
    negative_records = []

    print(f"Generating {num_negatives} non-landslide (negative) control samples within NER...")
    for _ in range(num_negatives):
        lat = np.random.uniform(NER_BOUNDS["lat_min"], NER_BOUNDS["lat_max"])
        lon = np.random.uniform(NER_BOUNDS["lon_min"], NER_BOUNDS["lon_max"])
        month = np.random.randint(1, 13)

        elevation, slope = estimate_terrain_features(lat, lon)

        # Non-landslide days have typical baseline rainfall (mostly lower)
        daily_rain = np.random.exponential(scale=8.0)
        rain_3d = daily_rain + np.random.exponential(scale=12.0)
        rain_7d = rain_3d + np.random.exponential(scale=15.0)

        negative_records.append({
            'latitude': lat,
            'longitude': lon,
            'month': month,
            'elevation': elevation,
            'slope': slope,
            'daily_rainfall': round(daily_rain, 2),
            'cumulative_rainfall_3d': round(rain_3d, 2),
            'cumulative_rainfall_7d': round(rain_7d, 2),
            'is_landslide': 0
        })

    # Combine into a single Dataset
    df_processed = pd.DataFrame(positive_records + negative_records)
    
    # Shuffle dataset
    df_processed = df_processed.sample(frac=1.0, random_state=42).reset_index(drop=True)

    # Save to processed directory
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df_processed.to_csv(PROCESSED_DATA_PATH, index=False)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"Processed dataset saved to: {PROCESSED_DATA_PATH}")
    print(f"Total Records: {len(df_processed)}")
    print(f"  - Landslide (1): {df_processed['is_landslide'].sum()}")
    print(f"  - Non-Landslide (0): {(df_processed['is_landslide'] == 0).sum()}")
    print("=" * 60)

if __name__ == "__main__":
    run_data_pipeline()