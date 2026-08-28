import numpy as np
import pandas as pd
from typing import Dict, List, Any

# 24 Stations on the Kochi Metro Blue/Pink Line corridor
KOCHI_STATIONS = [
    "Aluva", "Pulinchodu", "Companypady", "Ambattukavu", "Muttom",
    "Kalamassery", "CUSAT", "Pathadipalam", "Edappally", "Changampuzha Park",
    "Palarivattom", "JLN Stadium", "Kaloor", "Lissie", "Maharajas College",
    "Ernakulam South", "Kadavanthra", "Elamkulam", "Vyttila", "Thaikoodam",
    "Petta", "Vadakkekotta", "SN Junction", "Tripunithura"
]

class KochiMetroDataGenerator:
    """
    Synthetic Data Generator modeling 25 Kochi Metro Alstom Metropolis trainsets
    and station-by-station passenger faregate movement.
    """
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.num_trains = 25
        self.train_ids = [f"KM-{101 + i}" for i in range(self.num_trains)]

    def generate_fleet_telemetry(self, num_samples: int = 500) -> pd.DataFrame:
        """
        Generates historical telemetry & subsystem health logs across fleet units.
        """
        records = []
        for _ in range(num_samples):
            train_id = np.random.choice(self.train_ids)
            # Wear and tear indicators
            brake_pad_wear_pct = np.random.uniform(5.0, 95.0)
            door_cycles = np.random.randint(1000, 80000)
            hvac_pressure_psi = np.random.uniform(40.0, 75.0)
            traction_motor_temp = np.random.uniform(45.0, 105.0)
            mileage_km = np.random.uniform(5000, 180000)
            days_since_ibl = np.random.randint(1, 180)
            past_30d_delays = np.random.poisson(lam=1.5)
            past_30d_faults = np.random.poisson(lam=0.8)

            # Subsystem risks (synthetic ground truth target logic)
            brake_risk = min(1.0, (brake_pad_wear_pct / 100.0) ** 2 + past_30d_delays * 0.05)
            door_risk = min(1.0, (door_cycles / 80000.0) ** 1.5 + (past_30d_faults * 0.08))
            hvac_risk = min(1.0, max(0.0, (65.0 - hvac_pressure_psi) / 25.0) + (days_since_ibl / 200.0) * 0.3)
            traction_risk = min(1.0, max(0.0, (traction_motor_temp - 70.0) / 35.0))

            # Overall breakdown risk for next operating day
            combined_risk = 0.35 * brake_risk + 0.25 * door_risk + 0.20 * hvac_risk + 0.20 * traction_risk
            # Next-day failure event (0 or 1) with probabilistic noise
            failure_event = 1 if np.random.rand() < combined_risk * 0.6 else 0

            records.append({
                "train_id": train_id,
                "brake_pad_wear_pct": round(brake_pad_wear_pct, 2),
                "door_cycles": door_cycles,
                "hvac_pressure_psi": round(hvac_pressure_psi, 2),
                "traction_motor_temp_c": round(traction_motor_temp, 2),
                "mileage_km": round(mileage_km, 1),
                "days_since_ibl": days_since_ibl,
                "past_30d_delays": past_30d_delays,
                "past_30d_faults": past_30d_faults,
                "brake_risk": round(brake_risk, 4),
                "door_risk": round(door_risk, 4),
                "hvac_risk": round(hvac_risk, 4),
                "traction_risk": round(traction_risk, 4),
                "next_day_failure_prob": round(combined_risk, 4),
                "failure_event": failure_event
            })
        return pd.DataFrame(records)

    def generate_current_fleet_status(self) -> pd.DataFrame:
        """
        Generates real-time snapshot status for all 25 trains for tomorrow's chart evaluation.
        """
        records = []
        for train_id in self.train_ids:
            brake_wear = np.random.uniform(10.0, 92.0)
            door_cycles = np.random.randint(5000, 75000)
            hvac_psi = np.random.uniform(42.0, 72.0)
            traction_temp = np.random.uniform(50.0, 98.0)
            mileage = np.random.uniform(10000, 160000)
            days_ibl = np.random.randint(5, 160)
            delays = np.random.randint(0, 5)
            faults = np.random.randint(0, 3)

            records.append({
                "train_id": train_id,
                "brake_pad_wear_pct": round(brake_wear, 2),
                "door_cycles": door_cycles,
                "hvac_pressure_psi": round(hvac_psi, 2),
                "traction_motor_temp_c": round(traction_temp, 2),
                "mileage_km": round(mileage, 1),
                "days_since_ibl": days_ibl,
                "past_30d_delays": delays,
                "past_30d_faults": faults
            })
        return pd.DataFrame(records)

    def generate_station_demand(self, is_peak_hour: bool = True, day_type: str = "WEEKDAY") -> List[Dict[str, Any]]:
        """
        Generates station-by-station boarding & alighting forecast.
        """
        station_data = []
        base_multiplier = 1.8 if is_peak_hour else 0.8
        if day_type == "WEEKEND":
            base_multiplier *= 0.75
        elif day_type == "EVENT":
            base_multiplier *= 1.4

        for station in KOCHI_STATIONS:
            # Hub stations like Edappally, Kaloor, Aluva, MG Road have higher flow
            if station in ["Aluva", "Edappally", "Kaloor", "MG Road", "Ernakulam South", "Vyttila"]:
                boarding = int(np.random.normal(450, 60) * base_multiplier)
                alighting = int(np.random.normal(420, 50) * base_multiplier)
            else:
                boarding = int(np.random.normal(180, 30) * base_multiplier)
                alighting = int(np.random.normal(160, 30) * base_multiplier)

            boarding = max(20, boarding)
            alighting = max(15, alighting)
            station_data.append({
                "station_name": station,
                "predicted_boarding": boarding,
                "predicted_alighting": alighting,
                "crowding_accumulation_risk": "HIGH" if boarding > 500 else ("MEDIUM" if boarding > 250 else "LOW")
            })
        return station_data

if __name__ == "__main__":
    gen = KochiMetroDataGenerator()
    df = gen.generate_fleet_telemetry(10)
    print("Sample Fleet Telemetry:")
    print(df.head())
