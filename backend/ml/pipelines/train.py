import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import joblib

# Define paths relative to the current script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
PROCESSED_DATA_PATH = os.path.join(BACKEND_DIR, "data", "processed", "processed_landslides.csv")
MODEL_DIR = os.path.join(BACKEND_DIR, "ml", "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_landslide_model.joblib")

def train_model():
    print("=" * 60)
    print("STARTING XGBOOST MODEL TRAINING")
    print("=" * 60)

    # 1. Load the processed dataset
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"ERROR: Processed data not found at {PROCESSED_DATA_PATH}")
        sys.exit(1)

    print("Loading processed dataset...")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    # 2. Select Features and Target
    # We deliberately EXCLUDE latitude and longitude. 
    # We want the model to learn the PHYSICS of a landslide (rainfall + slope), 
    # not just memorize specific GPS coordinates.
    features = [
        'month', 
        'elevation', 
        'slope', 
        'daily_rainfall', 
        'cumulative_rainfall_3d', 
        'cumulative_rainfall_7d'
    ]
    target = 'is_landslide'

    X = df[features]
    y = df[target]

    # 3. Train / Test Split (80% training, 20% evaluation)
    # stratify=y ensures the 1:3 positive/negative ratio is maintained in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training set size: {len(X_train)} samples")
    print(f"Testing set size: {len(X_test)} samples")

    # 4. Handle Class Imbalance
    # We have more non-landslides than landslides. 
    # scale_pos_weight forces the model to pay more attention to the minority class (landslides).
    negative_cases = (y_train == 0).sum()
    positive_cases = (y_train == 1).sum()
    imbalance_ratio = negative_cases / positive_cases
    print(f"Class imbalance ratio (Negative/Positive): {imbalance_ratio:.2f}")

    # 5. Initialize and Train XGBoost
    print("\nTraining XGBoost Classifier...")
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        scale_pos_weight=imbalance_ratio,
        max_depth=5,
        learning_rate=0.1,
        n_estimators=100,
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)

    # 6. Evaluate the Model
    print("\nEvaluating Model Performance on Test Set...")
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print("\n--- MODEL METRICS ---")
    print(f"Accuracy:  {acc:.4f} (Overall correctness)")
    print(f"Precision: {prec:.4f} (When it predicts landslide, how often is it right?)")
    print(f"Recall:    {rec:.4f} (Out of all actual landslides, how many did it catch?)")
    print(f"F1-Score:  {f1:.4f} (Balance of Precision and Recall)")
    
    print("\n--- CONFUSION MATRIX ---")
    cm = confusion_matrix(y_test, y_pred)
    print(f"True Negatives (Safe correctly identified): {cm[0][0]}")
    print(f"False Positives (False Alarms):             {cm[0][1]}")
    print(f"False Negatives (MISSED LANDSLIDES):        {cm[1][0]}")
    print(f"True Positives (Landslides caught):         {cm[1][1]}")

    # 7. Feature Importance
    print("\n--- FEATURE IMPORTANCE ---")
    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    
    for _, row in feature_importance_df.iterrows():
        print(f"{row['Feature']:<25}: {row['Importance']:.4f}")

    # 8. Save the Model for FastAPI
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nSUCCESS: Model saved securely to {MODEL_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    train_model()