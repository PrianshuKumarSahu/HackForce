import os
import joblib
import numpy as np
from typing import Dict, List, Any
from kochi_metro.data.generator import KOCHI_STATIONS, KochiMetroDataGenerator

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
DEMAND_MODEL_PATH = os.path.join(MODELS_DIR, "demand_models.joblib")

class PassengerDemandPredictor:
    """
    ML Predictor for Station-Level Boarding/Alighting, Onboard Passenger Load,
    and Proactive Crowding Alerts across the Kochi Metro Corridor.
    """
    def __init__(self):
        self.train_capacity = 900  # 3-car Alstom Metropolis trainset standard capacity
        self.is_trained = os.path.exists(DEMAND_MODEL_PATH)
        if self.is_trained:
            self.bundle = joblib.load(DEMAND_MODEL_PATH)

    def predict_corridor_flow(self, is_peak_hour: bool = True, day_type: str = "WEEKDAY") -> Dict[str, Any]:
        """
        Forecasts station boarding/alighting and computes onboard train load profile.
        """
        gen = KochiMetroDataGenerator()
        station_demands = gen.generate_station_demand(is_peak_hour=is_peak_hour, day_type=day_type)

        cumulative_onboard = 0
        station_profiles = []
        bottleneck_stations = []
        proactive_alerts = []

        for item in station_demands:
            station_name = item["station_name"]
            boarding = item["predicted_boarding"]
            alighting = item["predicted_alighting"]

            # Calculate net onboard change
            cumulative_onboard = max(0, cumulative_onboard + boarding - alighting)
            crowding_pct = round((cumulative_onboard / self.train_capacity) * 100.0, 1)

            status = "NORMAL"
            if crowding_pct >= 95.0:
                status = "CRITICAL_OVERCROWDING"
                bottleneck_stations.append(station_name)
                proactive_alerts.append({
                    "station_name": station_name,
                    "severity": "HIGH",
                    "message": f"Critical passenger crowding projected at {station_name} ({crowding_pct}% train capacity). Advise platform staff for crowd control and display deboarding guidance."
                })
            elif crowding_pct >= 80.0:
                status = "HIGH_CROWDING"
                if station_name in ["Edappally", "Kaloor", "MG Road"]:
                    bottleneck_stations.append(station_name)

            station_profiles.append({
                "station_name": station_name,
                "predicted_boarding": boarding,
                "predicted_alighting": alighting,
                "onboard_passengers": cumulative_onboard,
                "crowding_pct": min(120.0, crowding_pct),
                "crowding_status": status
            })

        return {
            "peak_hour": is_peak_hour,
            "day_type": day_type,
            "max_onboard_passengers": max([sp["onboard_passengers"] for sp in station_profiles]),
            "peak_crowding_pct": max([sp["crowding_pct"] for sp in station_profiles]),
            "bottleneck_stations": bottleneck_stations,
            "station_profiles": station_profiles,
            "proactive_passenger_alerts": proactive_alerts
        }

if __name__ == "__main__":
    predictor = PassengerDemandPredictor()
    flow = predictor.predict_corridor_flow(is_peak_hour=True)
    print("Peak Hour Corridor Flow Summary:")
    print(f"Peak Crowding: {flow['peak_crowding_pct']}%")
    print(f"Bottlenecks: {flow['bottleneck_stations']}")
