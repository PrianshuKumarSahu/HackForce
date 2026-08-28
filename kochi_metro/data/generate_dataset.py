import os
import pandas as pd
from kochi_metro.data.generator import KochiMetroDataGenerator

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def build_and_save_datasets(num_telemetry_samples: int = 10000) -> tuple[str, str]:
    """
    Generates and saves persistent historical training datasets for telemetry and station demand.
    """
    gen = KochiMetroDataGenerator(seed=42)

    # 1. Telemetry Dataset
    print(f"Generating {num_telemetry_samples} historical telemetry records for Kochi Metro fleet...")
    df_telemetry = gen.generate_fleet_telemetry(num_samples=num_telemetry_samples)
    telemetry_path = os.path.join(DATA_DIR, "telemetry_dataset.csv")
    df_telemetry.to_csv(telemetry_path, index=False)

    # 2. Demand Dataset
    print("Generating station passenger flow datasets...")
    demand_records = []
    for day in range(90):  # 90 days of passenger flow
        for hour in range(6, 23):
            is_peak = (7 <= hour <= 10) or (17 <= hour <= 20)
            day_type = "WEEKEND" if (day % 7 >= 5) else "WEEKDAY"
            flow = gen.generate_station_demand(is_peak_hour=is_peak, day_type=day_type)
            for st in flow:
                demand_records.append({
                    "day": day,
                    "hour": hour,
                    "is_peak": 1 if is_peak else 0,
                    "day_type": day_type,
                    "station_name": st["station_name"],
                    "boarding": st["predicted_boarding"],
                    "alighting": st["predicted_alighting"]
                })
    df_demand = pd.DataFrame(demand_records)
    demand_path = os.path.join(DATA_DIR, "demand_dataset.csv")
    df_demand.to_csv(demand_path, index=False)

    print(f"Datasets generated and saved successfully:\n- {telemetry_path}\n- {demand_path}")
    return telemetry_path, demand_path

if __name__ == "__main__":
    build_and_save_datasets()
