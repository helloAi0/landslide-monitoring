import os
import math
import json
import urllib.request
import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="GeoShield Enterprise - Landslide Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "saved_models", "xgboost_landslide_model.joblib")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Standardized User-Agent with contact info to prevent API blocking
USER_AGENT = 'GeoShield_App/1.0 (contact@yourdomain.com)'

model = None

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)

class MapPredictionRequest(BaseModel):
    latitude: float
    longitude: float
    month: int = 7
    auto_fetch_live_data: bool = True
    daily_rainfall: Optional[float] = 0.0
    cumulative_rainfall_3d: Optional[float] = 0.0
    cumulative_rainfall_7d: Optional[float] = 0.0

class EvacuationRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float

# --- 1. HELPER & REVERSE GEOCODING APIS ---

def fetch_land_and_location_data(lat: float, lon: float):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        # Increased timeout to 5s
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode())
            location_name = data.get('display_name', f"Sector ({lat:.2f}, {lon:.2f})")
            address = data.get('address', {})
            land_type = address.get('suburb') or address.get('county') or address.get('state_district') or "Open Terrain"
            return location_name, land_type
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return f"Coordinates: {lat:.4f}, {lon:.4f}", "Open Terrain"

def calculate_climate_and_terrain(lat: float, lon: float, daily_rain: float, cumul_3d: float, land_type: str):
    try:
        delta = 0.001
        lats = f"{lat},{lat+delta},{lat-delta},{lat},{lat}"
        lons = f"{lon},{lon},{lon},{lon+delta},{lon-delta}"
        
        url = f"https://api.open-meteo.com/v1/elevation?latitude={lats}&longitude={lons}"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        # Increased timeout to 5s
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode())
            elevations = data.get('elevation', [0.0, 0.0, 0.0, 0.0, 0.0])
            
            elevation = elevations[0]
            
            # Prevent Division by Zero if all elevations are identical (flat plains)
            if max(elevations) == min(elevations):
                slope = 0.5
            else:
                dz_dx = (elevations[3] - elevations[4]) / (2 * 111000 * math.cos(math.radians(lat)))
                dz_dy = (elevations[1] - elevations[2]) / (2 * 111000)
                slope_rad = math.atan(math.sqrt(dz_dx**2 + dz_dy**2))
                slope = round(math.degrees(slope_rad), 1)
    except Exception as e:
        print(f"Elevation API Error: {e}")
        # FIXED FALLBACK: Default to realistic flat terrain, NOT random modulo math.
        elevation = 100.0
        slope = 1.0

    slope = max(0.5, slope) # Safe minimum
    temp_c = round(max(-5.0, 32.0 - (elevation / 150.0)), 1)
    weather_desc = "Heavy Downpour" if daily_rain > 50 else "Moderate Rain" if daily_rain > 10 else "Clear / Overcast"
    soil_sat = round(min(100.0, 20.0 + (cumul_3d * 0.8)), 1)
    
    return elevation, slope, temp_c, weather_desc, soil_sat, land_type

def fetch_live_weather(lat: float, lon: float):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&past_days=7&timezone=auto"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            data = json.loads(resp.read().decode())
            daily_precip = data.get('daily', {}).get('precipitation_sum', [])
            daily_rain = daily_precip[-1] if daily_precip else 0.0
            cumul_3d = sum(daily_precip[-3:]) if len(daily_precip) >= 3 else daily_rain
            cumul_7d = sum(daily_precip[-7:]) if len(daily_precip) >= 7 else cumul_3d
            return round(daily_rain, 1), round(cumul_3d, 1), round(cumul_7d, 1)
    except Exception as e:
        print(f"Weather API Error: {e}")
        return 0.0, 0.0, 0.0

def fetch_soilgrids_data(lat: float, lon: float):
    try:
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=clay&property=sand&property=silt&property=bdod&depth=0-5cm&value=mean"
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        # MAJOR FIX: ISRIC is very slow. Increased timeout to 8 seconds.
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            data = json.loads(resp.read().decode())
            layers = {l['name']: l['depths'][0]['values']['mean'] for l in data['geometry']['properties']['layers']}
            
            clay = (layers.get('clay', 200) / 10.0)
            sand = (layers.get('sand', 400) / 10.0)
            silt = (layers.get('silt', 400) / 10.0)
            bulk_density = (layers.get('bdod', 1400) / 100.0)
            return clay, sand, silt, bulk_density
    except Exception as e:
        print(f"Soil API Error: {e}")
        # Standard average soil composition if it completely fails
        return 30.0, 40.0, 30.0, 1.3

# --- 2. GEOTECHNICAL PHYSICS ENGINE ---

def compute_factor_of_safety(slope_deg: float, clay_pct: float, sand_pct: float, bulk_density: float, is_forest: bool):
    if slope_deg <= 2.0:
        return 5.0
    
    rad = math.radians(slope_deg)
    gamma = bulk_density * 9.81
    gamma_w = 9.81
    z = 2.0
    
    phi_deg = 25.0 + (sand_pct * 0.15)
    phi_rad = math.radians(phi_deg)
    
    c_prime = 5.0 + (clay_pct * 0.2)
    if is_forest:
        c_prime += 12.0
        
    numerator = c_prime + ((gamma - gamma_w) * z * (math.cos(rad) ** 2) * math.tan(phi_rad))
    denominator = gamma * z * math.sin(rad) * math.cos(rad)
    
    fos = numerator / max(denominator, 0.001)
    return round(float(np.clip(fos, 0.1, 5.0)), 2)

def send_telegram_alert(location: str, lat: float, lon: float, risk: str, prob: float, fos: float):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    text = (
        f"🚨 *CRITICAL LANDSLIDE HAZARD ALERT*\n\n"
        f"*Location:* {location}\n"
        f"*Coordinates:* {lat:.4f}, {lon:.4f}\n"
        f"*Risk Level:* {risk}\n"
        f"*Failure Probability:* {prob * 100:.1f}%\n"
        f"*Factor of Safety (FoS):* {fos}\n\n"
        f"⚠️ Immediate evacuation protocol recommended for vulnerable sectors."
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req, timeout=2.0)
    except Exception:
        pass

# --- 3. ENDPOINTS ---

@app.post("/api/predict-location")
def predict_location(req: MapPredictionRequest, background_tasks: BackgroundTasks):
    if req.auto_fetch_live_data:
        daily_rain, cumul_3d, cumul_7d = fetch_live_weather(req.latitude, req.longitude)
    else:
        daily_rain, cumul_3d, cumul_7d = req.daily_rainfall, req.cumulative_rainfall_3d, req.cumulative_rainfall_7d

    location_name, land_type = fetch_land_and_location_data(req.latitude, req.longitude)
    clay, sand, silt, bulk_density = fetch_soilgrids_data(req.latitude, req.longitude)
    
    elevation, slope, temp_c, weather_desc, soil_sat, land_type = calculate_climate_and_terrain(
        req.latitude, req.longitude, daily_rain, cumul_3d, land_type
    )

    is_forest = "Forest" in land_type or "Jungle" in land_type
    fos = compute_factor_of_safety(slope, clay, sand, bulk_density, is_forest)

    ml_prob = 0.0
    if model is not None:
        try:
            input_data = pd.DataFrame([{
                'month': req.month, 'elevation': elevation, 'slope': slope,
                'daily_rainfall': daily_rain, 'cumulative_rainfall_3d': cumul_3d,
                'cumulative_rainfall_7d': cumul_7d
            }])
            ml_prob = float(model.predict_proba(input_data)[0][1])
            if is_forest: ml_prob *= 0.35
        except Exception:
            pass

    if fos <= 1.0:
        physics_prob = 0.60 + 0.39 * (1.0 - max(0.1, fos))
    elif fos <= 1.5:
        physics_prob = 0.30 + 0.30 * ((1.5 - fos) / 0.5)
    elif fos <= 2.5:
        physics_prob = 0.05 + 0.25 * ((2.5 - fos) / 1.0)
    else:
        physics_prob = max(0.001, 0.05 * math.exp(-(fos - 2.5)))

    prob = max(ml_prob, physics_prob)
    
    baseline_noise = (slope * 0.0005) + (cumul_7d * 0.0001)
    prob = float(np.clip(prob + baseline_noise, 0.001, 0.999))
    prob_display = round(prob, 4)

    risk = "High" if (prob >= 0.60 or fos < 1.0) else "Moderate" if (prob >= 0.30 or fos < 1.3) else "Low"

    if risk == "High":
        background_tasks.add_task(send_telegram_alert, location_name, req.latitude, req.longitude, risk, prob, fos)

    return {
        "location_name": location_name,
        "land_type": land_type,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "elevation": elevation,
        "slope": slope,
        "temperature_c": temp_c,
        "weather_desc": weather_desc,
        "soil_saturation": soil_sat,
        "live_precipitation": {"daily_mm": daily_rain, "cumul_3d_mm": cumul_3d, "cumul_7d_mm": cumul_7d},
        "soil_properties": {"clay_pct": clay, "sand_pct": sand, "silt_pct": silt, "bulk_density_g_cm3": bulk_density},
        "factor_of_safety": fos,
        "probability_score": prob_display,
        "risk_level": risk,
        "trigger_alert": risk == "High"
    }

@app.post("/api/evacuation-route")
def get_evacuation_route(req: EvacuationRequest):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{req.start_lon},{req.start_lat};{req.end_lon},{req.end_lat}?overview=full&geometries=geojson"
        req_obj = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req_obj, timeout=5.0) as resp:
            data = json.loads(resp.read().decode())
            return data['routes'][0]['geometry']
    except Exception as e:
        return {"error": "Routing unavailable", "details": str(e)}