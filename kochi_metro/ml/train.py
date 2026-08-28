import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from kochi_metro.data.generate_dataset import build_and_save_datasets, DATA_DIR

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_all_models():
    """
    Main ML Training Pipeline: Trains health, demand, and chart evaluation models,
    evaluates validation metrics, and serializes trained .joblib artifacts.
    """
    telemetry_path = os.path.join(DATA_DIR, "telemetry_dataset.csv")
    demand_path = os.path.join(DATA_DIR, "demand_dataset.csv")

    if not os.path.exists(telemetry_path) or not os.path.exists(demand_path):
        telemetry_path, demand_path = build_and_save_datasets(num_telemetry_samples=10000)

    print("\n=======================================================")
    print(" [START] KOCHI METRO ML MODEL TRAINING PIPELINE")
    print("=======================================================")

    # ----------------------------------------------------
    # 1. Train Fleet Health & Subsystem Risk Predictors
    # ----------------------------------------------------
    df_telemetry = pd.read_csv(telemetry_path)
    feature_cols = [
        "brake_pad_wear_pct", "door_cycles", "hvac_pressure_psi",
        "traction_motor_temp_c", "mileage_km", "days_since_ibl",
        "past_30d_delays", "past_30d_faults"
    ]
    X_telemetry = df_telemetry[feature_cols]

    X_train, X_val, y_train, y_val = train_test_split(
        X_telemetry, df_telemetry["next_day_failure_prob"], test_size=0.2, random_state=42
    )

    print("\n1. Training Fleet Failure Risk Model (Gradient Boosting Regressor)...")
    model_failure = GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=5, random_state=42)
    model_failure.fit(X_train, y_train)

    val_preds = model_failure.predict(X_val)
    r2_fail = r2_score(y_val, val_preds)
    mae_fail = mean_absolute_error(y_val, val_preds)
    rmse_fail = np.sqrt(mean_squared_error(y_val, val_preds))
    print(f"   [Failure Model Metrics] R2: {r2_fail:.4f} | MAE: {mae_fail:.4f} | RMSE: {rmse_fail:.4f}")

    print("   Training Subsystem Models (Brakes, Doors, HVAC, Traction)...")
    model_brake = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42).fit(X_telemetry, df_telemetry["brake_risk"])
    model_door = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42).fit(X_telemetry, df_telemetry["door_risk"])
    model_hvac = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42).fit(X_telemetry, df_telemetry["hvac_risk"])
    model_traction = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42).fit(X_telemetry, df_telemetry["traction_risk"])

    health_bundle = {
        "model_failure": model_failure,
        "model_brake": model_brake,
        "model_door": model_door,
        "model_hvac": model_hvac,
        "model_traction": model_traction,
        "feature_cols": feature_cols
    }
    health_model_path = os.path.join(MODELS_DIR, "health_models.joblib")
    joblib.dump(health_bundle, health_model_path, compress=3)
    print(f"   [OK] Saved Health Models -> {health_model_path}")

    # ----------------------------------------------------
    # 2. Train Station Passenger Demand Model
    # ----------------------------------------------------
    print("\n2. Training Station Passenger Demand Model...")
    df_demand = pd.read_csv(demand_path)
    df_demand["station_code"] = df_demand["station_name"].astype("category").cat.codes

    X_demand = df_demand[["hour", "is_peak", "station_code"]]
    y_boarding = df_demand["boarding"]
    y_alighting = df_demand["alighting"]

    demand_boarding_model = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42).fit(X_demand, y_boarding)
    demand_alighting_model = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42).fit(X_demand, y_alighting)

    demand_bundle = {
        "boarding_model": demand_boarding_model,
        "alighting_model": demand_alighting_model,
        "station_categories": list(df_demand["station_name"].astype("category").cat.categories)
    }
    demand_model_path = os.path.join(MODELS_DIR, "demand_models.joblib")
    joblib.dump(demand_bundle, demand_model_path, compress=3)
    print(f"   [OK] Saved Demand Models -> {demand_model_path}")

    # ----------------------------------------------------
    # 3. Train Chart Efficiency Evaluator Model
    # ----------------------------------------------------
    print("\n3. Training Chart Efficiency Evaluator Model...")
    # Synthetic chart evaluation training log
    chart_records = []
    for _ in range(2000):
        avg_fail_p = np.random.uniform(0.02, 0.40)
        max_fail_p = np.random.uniform(avg_fail_p, 0.85)
        num_high_risk = np.random.randint(0, 6)
        num_standby = np.random.randint(1, 5)
        peak_crowding = np.random.uniform(60.0, 110.0)

        chart_eff = max(50.0, 100.0 - (avg_fail_p * 70.0 + max_fail_p * 25.0 + max(0, peak_crowding - 85.0) * 0.15))
        delay_mins = 2.5 + (avg_fail_p * 50.0) + (max(0, peak_crowding - 80.0) * 0.2)

        chart_records.append({
            "avg_fail_p": avg_fail_p,
            "max_fail_p": max_fail_p,
            "num_high_risk": num_high_risk,
            "num_standby": num_standby,
            "peak_crowding": peak_crowding,
            "chart_efficiency": round(chart_eff, 2),
            "expected_delay": round(delay_mins, 2)
        })

    df_charts = pd.DataFrame(chart_records)
    X_chart = df_charts[["avg_fail_p", "max_fail_p", "num_high_risk", "num_standby", "peak_crowding"]]

    chart_eff_model = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42).fit(X_chart, df_charts["chart_efficiency"])
    chart_delay_model = RandomForestRegressor(n_estimators=40, max_depth=8, random_state=42).fit(X_chart, df_charts["expected_delay"])

    evaluator_bundle = {
        "efficiency_model": chart_eff_model,
        "delay_model": chart_delay_model
    }
    evaluator_model_path = os.path.join(MODELS_DIR, "chart_evaluator_models.joblib")
    joblib.dump(evaluator_bundle, evaluator_model_path, compress=3)
    print(f"   [OK] Saved Chart Evaluator Models -> {evaluator_model_path}")

    print("\n=======================================================")
    print(" [FINISHED] ALL KOCHI METRO ML MODELS TRAINED & PERSISTED SUCCESSFULLY!")
    print("=======================================================\n")

if __name__ == "__main__":
    train_all_models()
