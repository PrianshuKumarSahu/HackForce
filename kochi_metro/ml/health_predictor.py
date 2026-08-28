import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from kochi_metro.data.generator import KochiMetroDataGenerator

class TrainHealthPredictor:
    """
    ML Engine for Trainset Health & Subsystem Failure Prediction.
    Calculates subsystem risks (Brakes, Doors, HVAC, Traction) and failure probability.
    """
    def __init__(self):
        self.model_failure = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.model_brake = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model_door = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model_hvac = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model_traction = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False

    def train_models(self, df_telemetry: pd.DataFrame):
        """
        Trains ML models on historical fleet telemetry dataset.
        """
        feature_cols = [
            "brake_pad_wear_pct", "door_cycles", "hvac_pressure_psi",
            "traction_motor_temp_c", "mileage_km", "days_since_ibl",
            "past_30d_delays", "past_30d_faults"
        ]
        X = df_telemetry[feature_cols]

        self.model_failure.fit(X, df_telemetry["next_day_failure_prob"])
        self.model_brake.fit(X, df_telemetry["brake_risk"])
        self.model_door.fit(X, df_telemetry["door_risk"])
        self.model_hvac.fit(X, df_telemetry["hvac_risk"])
        self.model_traction.fit(X, df_telemetry["traction_risk"])

        self.is_trained = True

    def predict_fleet_health(self, fleet_status_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Predicts next-day failure probability, subsystem risk breakdown,
        and consequence-weighted operational impact scores for all fleet units.
        """
        if not self.is_trained:
            # Self-train on synthetic baseline dataset if not trained yet
            gen = KochiMetroDataGenerator()
            train_df = gen.generate_fleet_telemetry(num_samples=1000)
            self.train_models(train_df)

        feature_cols = [
            "brake_pad_wear_pct", "door_cycles", "hvac_pressure_psi",
            "traction_motor_temp_c", "mileage_km", "days_since_ibl",
            "past_30d_delays", "past_30d_faults"
        ]
        X_current = fleet_status_df[feature_cols]

        pred_failure_probs = np.clip(self.model_failure.predict(X_current), 0.01, 0.99)
        pred_brake_risks = np.clip(self.model_brake.predict(X_current), 0.01, 0.99)
        pred_door_risks = np.clip(self.model_door.predict(X_current), 0.01, 0.99)
        pred_hvac_risks = np.clip(self.model_hvac.predict(X_current), 0.01, 0.99)
        pred_traction_risks = np.clip(self.model_traction.predict(X_current), 0.01, 0.99)

        results = []
        for idx, row in fleet_status_df.iterrows():
            train_id = row["train_id"]
            fail_prob = float(pred_failure_probs[idx])
            brake_r = float(pred_brake_risks[idx])
            door_r = float(pred_door_risks[idx])
            hvac_r = float(pred_hvac_risks[idx])
            traction_r = float(pred_traction_risks[idx])

            # Calculate Health Score (0-100)
            health_score = round(max(0.0, 100.0 * (1.0 - fail_prob)), 1)

            # Consequence Score: Failure Probability x Expected Peak Operating Intensity (Exposure Factor)
            # High mileage trains scheduled for long express peak runs have higher disruption cost
            exposure_factor = 1.0 + (row["mileage_km"] / 100000.0) * 0.3
            consequence_score = round(fail_prob * exposure_factor * 100.0, 2)

            # Determine primary fault alert if any
            risk_dict = {
                "brakes": brake_r,
                "doors": door_r,
                "hvac": hvac_r,
                "traction": traction_r
            }
            highest_risk_subsystem = max(risk_dict, key=risk_dict.get)

            results.append({
                "train_id": train_id,
                "health_score": health_score,
                "next_day_failure_prob": round(fail_prob, 4),
                "consequence_score": consequence_score,
                "subsystem_risks": {
                    "brakes": round(brake_r, 4),
                    "doors": round(door_r, 4),
                    "hvac": round(hvac_r, 4),
                    "traction": round(traction_r, 4)
                },
                "primary_risk_subsystem": highest_risk_subsystem,
                "maintenance_urgency": "HIGH" if fail_prob > 0.30 else ("MEDIUM" if fail_prob > 0.15 else "LOW")
            })

        # Sort fleet by health score descending (best trains first)
        results.sort(key=lambda x: x["health_score"], reverse=True)
        return results

if __name__ == "__main__":
    gen = KochiMetroDataGenerator()
    fleet_df = gen.generate_current_fleet_status()
    predictor = TrainHealthPredictor()
    predictions = predictor.predict_fleet_health(fleet_df)
    print("Sample Fleet Health Predictions:")
    for p in predictions[:3]:
        print(p)
