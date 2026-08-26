import os
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
import joblib

# Ensure output directory exists
os.makedirs("saved_models", exist_ok=True)

# Generate synthetic dataset matching high-risk landslide parameters
np.random.seed(42)
num_samples = 2500

months = np.random.randint(1, 13, size=num_samples)
elevations = np.random.uniform(200, 3500, size=num_samples)
slopes = np.random.uniform(2, 60, size=num_samples)
daily_rain = np.random.exponential(scale=35, size=num_samples)
cumul_3d = daily_rain + np.random.exponential(scale=40, size=num_samples)
cumul_7d = cumul_3d + np.random.exponential(scale=50, size=num_samples)

# Rule-based target label generation for realistic ground truth
# High risk if steep slope (>25°) AND high 3-day rainfall (>100mm)
risk_score = (slopes / 60.0) * 0.5 + (cumul_3d / 250.0) * 0.5
labels = (risk_score > 0.45).astype(int)

df = pd.DataFrame({
    'month': months,
    'elevation': elevations,
    'slope': slopes,
    'daily_rainfall': daily_rain,
    'cumulative_rainfall_3d': cumul_3d,
    'cumulative_rainfall_7d': cumul_7d,
    'landslide': labels
})

X = df.drop(columns=['landslide'])
y = df['landslide']

# Train XGBoost Classifier
model = XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.05,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)
model.fit(X, y)

# Save model weights to specified backend path
save_path = os.path.join("saved_models", "xgboost_landslide_model.joblib")
joblib.dump(model, save_path)
print(f"✅ Model successfully trained and saved to: {save_path}")