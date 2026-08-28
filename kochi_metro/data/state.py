"""
In-Memory State, Telemetry History, and Event Store for Kochi Metro AI Engine.
Provides threshold configuration, live telemetry storage, anomaly detection,
event creation with deduplication, and state synchronization for trainsets.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

# -----------------------------------------------------------------------------
# 1. Configurable Anomaly Thresholds
# -----------------------------------------------------------------------------
ANOMALY_THRESHOLDS = {
    "HIGH_VIBRATION": {
        "metric": "vibration",
        "threshold": 0.25,
        "operator": ">=",
        "severity": "HIGH",
        "description": "Unusually high structural vibration detected on trainset."
    },
    "HIGH_TRACTION_TEMPERATURE": {
        "metric": "traction_motor_temp_c",
        "threshold": 95.0,
        "operator": ">=",
        "severity": "CRITICAL",
        "description": "Traction motor temperature exceeded thermal safety limit (95.0°C)."
    },
    "HVAC_LOW_PRESSURE": {
        "metric": "hvac_pressure_psi",
        "threshold": 40.0,
        "operator": "<=",
        "severity": "MEDIUM",
        "description": "HVAC refrigerant pressure dropped below operational limit (40 PSI)."
    },
    "HVAC_HIGH_PRESSURE": {
        "metric": "hvac_pressure_psi",
        "threshold": 75.0,
        "operator": ">=",
        "severity": "MEDIUM",
        "description": "HVAC refrigerant pressure exceeded high-pressure safety limit (75 PSI)."
    },
    "BRAKE_WEAR_CRITICAL": {
        "metric": "brake_pad_wear_pct",
        "threshold": 85.0,
        "operator": ">=",
        "severity": "HIGH",
        "description": "Brake pad wear reached critical replacement threshold (85%)."
    },
    "DOOR_CYCLES_WARNING": {
        "metric": "door_cycles",
        "threshold": 75000,
        "operator": ">=",
        "severity": "LOW",
        "description": "Door cycles reached scheduled overhaul inspection threshold (75,000 cycles)."
    }
}

# -----------------------------------------------------------------------------
# 2. In-Memory Data Store Singleton
# -----------------------------------------------------------------------------
class KochiMetroStateStore:
    def __init__(self):
        # Maps train_id -> latest telemetry dictionary
        self._latest_telemetry: Dict[str, Dict[str, Any]] = {}
        # List of all ingested telemetry records
        self._telemetry_history: List[Dict[str, Any]] = []
        # List of all created events
        self._events: List[Dict[str, Any]] = []
        # Deduplication tracker: (train_id, anomaly_type) -> last_event_timestamp
        self._active_events: Dict[str, str] = {}

    def get_latest_telemetry(self, train_id: str) -> Optional[Dict[str, Any]]:
        return self._latest_telemetry.get(train_id.upper())

    def record_telemetry(self, data: Dict[str, Any]) -> Tuple_List_Anomalies_Events:
        """
        Ingests a new telemetry payload, updates current state, runs anomaly checks,
        and creates events with deduplication.
        """
        train_id = data["train_id"].upper()
        now_str = data.get("timestamp") or datetime.now().isoformat()
        
        telemetry_record = {
            "id": f"TEL-{uuid.uuid4().hex[:8].upper()}",
            "train_id": train_id,
            "timestamp": now_str,
            "temperature_c": data.get("temperature_c", 25.0),
            "humidity_pct": data.get("humidity_pct", 50.0),
            "vibration": data.get("vibration", 0.05),
            "brake_pad_wear_pct": data.get("brake_pad_wear_pct", 30.0),
            "door_cycles": data.get("door_cycles", 10000),
            "hvac_pressure_psi": data.get("hvac_pressure_psi", 60.0),
            "traction_motor_temp_c": data.get("traction_motor_temp_c", 60.0),
            "mileage_km": data.get("mileage_km", 10000.0),
            "location_id": data.get("location_id", 1),
            "source": data.get("source", "IOT")
        }

        # Update latest telemetry map & append history
        self._latest_telemetry[train_id] = telemetry_record
        self._telemetry_history.append(telemetry_record)

        # Detect Anomalies
        anomalies = []
        created_events = []

        for rule_name, rule_cfg in ANOMALY_THRESHOLDS.items():
            metric_val = telemetry_record.get(rule_cfg["metric"])
            if metric_val is None:
                continue

            is_anomaly = False
            if rule_cfg["operator"] == ">=" and metric_val >= rule_cfg["threshold"]:
                is_anomaly = True
            elif rule_cfg["operator"] == "<=" and metric_val <= rule_cfg["threshold"]:
                is_anomaly = True

            if is_anomaly:
                anomalies.append({
                    "type": rule_name,
                    "severity": rule_cfg["severity"],
                    "description": rule_cfg["description"]
                })

                # Deduplication check: do not create duplicate events for identical open condition
                dedup_key = f"{train_id}:{rule_name}"
                if dedup_key not in self._active_events:
                    event = {
                        "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                        "train_id": train_id,
                        "event_type": rule_name,
                        "severity": rule_cfg["severity"],
                        "description": rule_cfg["description"],
                        "source": "IOT",
                        "occurred_at": now_str,
                        "processed_at": datetime.now().isoformat(),
                        "status": "OPEN"
                    }
                    self._events.append(event)
                    self._active_events[dedup_key] = event["event_id"]
                    created_events.append(event)

        return anomalies, created_events

    def get_telemetry_history(self, train_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        train_id_upper = train_id.upper()
        history = [t for t in self._telemetry_history if t["train_id"] == train_id_upper]
        # Return newest first
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return history[:limit]

    def get_events(
        self,
        train_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = self._events
        if train_id:
            results = [e for e in results if e["train_id"] == train_id.upper()]
        if severity:
            results = [e for e in results if e["severity"].upper() == severity.upper()]
        if status:
            results = [e for e in results if e["status"].upper() == status.upper()]
        if source:
            results = [e for e in results if e["source"].upper() == source.upper()]
        
        # Newest events first
        return sorted(results, key=lambda x: x["occurred_at"], reverse=True)

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        event_id_upper = event_id.upper()
        for e in self._events:
            if e["event_id"].upper() == event_id_upper:
                return e
        return None

# Global Singleton Instance
state_store = KochiMetroStateStore()
