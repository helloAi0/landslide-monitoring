import pandas as pd
import requests
import time
from tqdm import tqdm
import os

def extract_elevation():
    input_csv = "data/processed/ml_master_dataset.csv"
    output_csv = "data/processed/ml_dataset_with_elevation.csv"

    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Missing {input_csv}. Please run script 02 first.")

    print("Loading Master Dataset...")
    df = pd.read_csv(input_csv)
    
    # We will store the results here
    elevations = []
    
    # The Open-Meteo API allows batching up to 100 coordinates per request.
    BATCH_SIZE = 100
    
    print(f"Fetching real satellite elevation data for {len(df)} locations...")
    
    # tqdm gives us a nice progress bar in the terminal
    for i in tqdm(range(0, len(df), BATCH_SIZE), desc="API Requests"):
        batch = df.iloc[i:i + BATCH_SIZE]
        
        # Convert latitudes and longitudes into comma-separated strings for the URL
        lats = ",".join(batch['latitude'].astype(str))
        lons = ",".join(batch['longitude'].astype(str))
        
        # Open-Meteo Elevation API endpoint
        url = f"https://api.open-meteo.com/v1/elevation?latitude={lats}&longitude={lons}"
        
        try:
            response = requests.get(url)
            response.raise_for_status() # Check for HTTP errors
            data = response.json()
            
            if 'elevation' in data:
                elevations.extend(data['elevation'])
            else:
                print(f"\nWarning: Unexpected API response structure: {data}")
                # Fill with NaN (Not a Number) if it fails, so we don't break the list alignment
                elevations.extend([None] * len(batch))
                
        except requests.exceptions.RequestException as e:
            print(f"\nAPI Error: {e}")
            elevations.extend([None] * len(batch))
            
        # Be a good citizen to the free API: pause for 1 second between requests
        time.sleep(1)

    # Add the new feature to our dataset
    df['elevation'] = elevations
    
    # 1. Check for missing data
    missing_count = df['elevation'].isna().sum()
    if missing_count > 0:
        print(f"\nWarning: Failed to get elevation for {missing_count} points. Dropping them.")
        df = df.dropna(subset=['elevation'])
    
    # 2. Save the updated dataset
    df.to_csv(output_csv, index=False)
    
    print("\nSuccess! Elevation Feature Engineered.")
    print(f"Saved new dataset to: {output_csv}")
    
    # 3. Print a summary to verify the physics make sense
    print("\nElevation Summary (in meters):")
    print(f"Average Elevation for Landslides (1): {df[df['label'] == 1]['elevation'].mean():.1f}m")
    print(f"Average Elevation for Safe Zones (0): {df[df['label'] == 0]['elevation'].mean():.1f}m")

if __name__ == "__main__":
    extract_elevation()