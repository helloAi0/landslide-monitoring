import requests
import os
import sys

DATASET_URL = "https://data.nasa.gov/api/views/dd9e-wu2v/rows.csv?accessType=DOWNLOAD"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(CURRENT_DIR, "raw")
OUTPUT_FILE = os.path.join(RAW_DIR, "nasa_global_landslides.csv")

def download_nasa_glc():
    print(f"Starting download of NASA Global Landslide Catalog...")
    print(f"Source URL: {DATASET_URL}")
    print(f"Target Location: {OUTPUT_FILE}")
    
    # Add a standard browser User-Agent to bypass bot protection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Added timeout to prevent infinite hanging
        response = requests.get(DATASET_URL, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        with open(OUTPUT_FILE, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    
        print("\nSUCCESS: Dataset downloaded successfully!")
        
        file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        print(f"File Size: {file_size_mb:.2f} MB")

    except Exception as e:
        print(f"\nERROR: Automated download blocked or timed out. {e}")
        print("\n" + "="*50)
        print(" MANUAL FALLBACK REQUIRED ")
        print("="*50)
        print("NASA's server is rejecting the script. To unblock the project, please:")
        print("1. Open your web browser (Chrome/Edge/Firefox).")
        print(f"2. Paste this URL and press Enter:\n   {DATASET_URL}")
        print("3. The file will download as 'Global_Landslide_Catalog_Export.csv' (or similar).")
        print("4. Move that downloaded file into your project folder:")
        print(f"   {RAW_DIR}")
        print("5. Rename the file EXACTLY to: nasa_global_landslides.csv")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    download_nasa_glc()