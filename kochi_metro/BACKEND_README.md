# Kochi Metro AI Fleet Operations & Optimization Engine Backend

**System**: SIH 2026 - AI-Driven Train Induction Planning & Scheduling for Kochi Metro Rail Limited (KMRL)  
**Framework**: FastAPI, scikit-learn, Google OR-Tools CP-SAT, Pydantic, Pandas, NumPy  

---

## 🚀 Quick Start & How to Run

### 1. Install Dependencies
```bash
pip install fastapi uvicorn scikit-learn pandas numpy ortools pydantic
```

### 2. Start the Backend Server
From the project root directory (`C:\Users\JASWANTH\.gemini\antigravity\scratch\sih`):
```bash
python -m uvicorn kochi_metro.api.main:app --reload --port 8000
```
Or directly using `uvicorn`:
```bash
uvicorn kochi_metro.api.main:app --reload --port 8000
```

### 3. Open Swagger / OpenAPI Interactive Documentation
Once started, open your browser to:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 How to Run Tests

Run the full automated unit test suite covering ML predictors, CP-SAT optimizer, and REST API endpoints:
```bash
python -m unittest kochi_metro/tests/test_all.py
```

---

## 📡 Exposed API Endpoints

### 🚆 Train APIs (Phases 2 & 3)

#### 1. `GET /api/v1/trains` (Alias: `GET /api/trains`)
Returns complete operational telemetry and ML health predictions for all 25 fleet units (`KM-101` through `KM-125`).

**Sample Response (`200 OK`)**:
```json
{
  "total_trains": 25,
  "trains": [
    {
      "train_id": "KM-101",
      "train_type": "Alstom Metropolis 3-Car",
      "health_score": 92.4,
      "next_day_failure_prob": 0.076,
      "consequence_score": 9.12,
      "subsystem_risks": {
        "brakes": 0.051,
        "doors": 0.042,
        "hvac": 0.038,
        "traction": 0.025
      },
      "primary_risk_subsystem": "brakes",
      "maintenance_urgency": "LOW",
      "telemetry": {
        "brake_pad_wear_pct": 34.2,
        "door_cycles": 18450,
        "hvac_pressure_psi": 61.5,
        "traction_motor_temp_c": 64.2,
        "mileage_km": 42100.5,
        "days_since_ibl": 14,
        "past_30d_delays": 0,
        "past_30d_faults": 1
      },
      "notes": "Location tracking, fitness certs, and job-card status currently unpopulated in base telemetry."
    }
  ]
}
```

#### 2. `GET /api/v1/trains/{train_id}` (Alias: `GET /api/trains/{train_id}`)
Returns detailed operational telemetry and ML health predictions for a specific train unit by ID.

**Sample Request**: `GET /api/v1/trains/KM-101`  
**Sample Response (`200 OK`)**:
```json
{
  "train_id": "KM-101",
  "train_type": "Alstom Metropolis 3-Car",
  "health_score": 92.4,
  "next_day_failure_prob": 0.076,
  "consequence_score": 9.12,
  "subsystem_risks": {
    "brakes": 0.051,
    "doors": 0.042,
    "hvac": 0.038,
    "traction": 0.025
  },
  "primary_risk_subsystem": "brakes",
  "maintenance_urgency": "LOW",
  "telemetry": {
    "brake_pad_wear_pct": 34.2,
    "door_cycles": 18450,
    "hvac_pressure_psi": 61.5,
    "traction_motor_temp_c": 64.2,
    "mileage_km": 42100.5,
    "days_since_ibl": 14,
    "past_30d_delays": 0,
    "past_30d_faults": 1
  },
  "notes": "Location tracking, fitness certs, and job-card status currently unpopulated in base telemetry."
}
```

**Invalid Request (`404 Not Found`)**: `GET /api/v1/trains/KM-999`  
**Response**:
```json
{
  "detail": "Train 'KM-999' not found in fleet."
}
```

---

### 📡 IoT Telemetry & Event Ingestion APIs (Phase 5 & 6)

#### Architecture & ESP32 / Simulator Compatibility
The IoT ingestion layer accepts sensor telemetry payloads from an **ESP32 micro-controller**, **IoT simulator**, or **onboard sensor gateway**.
Incoming telemetry payloads update the live operational state of the train, feed historical telemetry logs, run threshold-based anomaly checks, and automatically generate deduplicated system events.

#### Configurable Anomaly Thresholds
| Anomaly Code | Sensor Metric | Threshold Rule | Severity | Description |
| :--- | :--- | :--- | :--- | :--- |
| `HIGH_VIBRATION` | `vibration` | `>= 0.25` | `HIGH` | Excessive structural vibration detected on trainset. |
| `HIGH_TRACTION_TEMPERATURE` | `traction_motor_temp_c` | `>= 95.0` °C | `CRITICAL` | Motor temperature exceeded thermal safety limit. |
| `HVAC_LOW_PRESSURE` | `hvac_pressure_psi` | `<= 40.0` PSI | `MEDIUM` | HVAC refrigerant pressure below operational limit. |
| `HVAC_HIGH_PRESSURE` | `hvac_pressure_psi` | `>= 75.0` PSI | `MEDIUM` | HVAC pressure exceeded high-pressure limit. |
| `BRAKE_WEAR_CRITICAL` | `brake_pad_wear_pct` | `>= 85.0` % | `HIGH` | Brake pad wear reached critical replacement limit. |
| `DOOR_CYCLES_WARNING` | `door_cycles` | `>= 75,000` | `LOW` | Door cycles reached overhaul inspection threshold. |

---

#### 1. `POST /api/v1/iot/telemetry`
Ingests live sensor telemetry for a train set.

**Sample Request (cURL)**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/iot/telemetry" \
     -H "Content-Type: application/json" \
     -d '{
           "train_id": "KM-101",
           "temperature_c": 28.4,
           "humidity_pct": 61.0,
           "vibration": 0.45,
           "brake_pad_wear_pct": 34.2,
           "door_cycles": 18450,
           "hvac_pressure_psi": 61.5,
           "traction_motor_temp_c": 105.0,
           "mileage_km": 42100.5,
           "location_id": 2
         }'
```

**Sample Response (`200 OK` - Accepted with Alert)**:
```json
{
  "status": "accepted_with_alert",
  "train_id": "KM-101",
  "anomalies": [
    {
      "type": "HIGH_VIBRATION",
      "severity": "HIGH",
      "description": "Unusually high structural vibration detected on trainset."
    },
    {
      "type": "HIGH_TRACTION_TEMPERATURE",
      "severity": "CRITICAL",
      "description": "Traction motor temperature exceeded thermal safety limit (95.0°C)."
    }
  ],
  "event_ids": [
    "EVT-A1B2C3D4",
    "EVT-E5F6G7H8"
  ],
  "timestamp": "2026-08-29T02:25:00.000000"
}
```

---

#### 2. `GET /api/v1/iot/{train_id}/telemetry`
Retrieves historical telemetry log entries for a train (newest first).

**Sample Request**: `GET /api/v1/iot/KM-101/telemetry?limit=20`  
**Sample Response (`200 OK`)**:
```json
{
  "train_id": "KM-101",
  "record_count": 1,
  "history": [
    {
      "id": "TEL-9F8E7D6C",
      "train_id": "KM-101",
      "timestamp": "2026-08-29T02:25:00.000000",
      "temperature_c": 28.4,
      "humidity_pct": 61.0,
      "vibration": 0.45,
      "brake_pad_wear_pct": 34.2,
      "door_cycles": 18450,
      "hvac_pressure_psi": 61.5,
      "traction_motor_temp_c": 105.0,
      "mileage_km": 42100.5,
      "location_id": 2,
      "source": "IOT"
    }
  ]
}
```

---

#### 3. `GET /api/v1/events` (Alias: `GET /api/events`)
Queries all system events and IoT alerts with optional filters (`train_id`, `severity`, `status`, `source`).

**Sample Request**: `GET /api/v1/events?train_id=KM-101&severity=CRITICAL`  
**Sample Response (`200 OK`)**:
```json
{
  "total_events": 1,
  "events": [
    {
      "event_id": "EVT-E5F6G7H8",
      "train_id": "KM-101",
      "event_type": "HIGH_TRACTION_TEMPERATURE",
      "severity": "CRITICAL",
      "description": "Traction motor temperature exceeded thermal safety limit (95.0°C).",
      "source": "IOT",
      "occurred_at": "2026-08-29T02:25:00.000000",
      "processed_at": "2026-08-29T02:25:00.005000",
      "status": "OPEN"
    }
  ]
}
```

#### 4. `GET /api/v1/events/{event_id}`
Retrieves specific event detail by ID.

#### 5. `GET /api/v1/trains/{train_id}/events`
Retrieves all events logged for a specific train unit.

---

### 🗺️ KMRL Location, Depot & Stabling Geometry APIs

#### Network Topology Overview
The location layer models all **24 Blue Line Mainline stations** (IDs 1–24), **Muttom Depot stabling lines & maintenance bays** (IDs 101–108), and **Kakkanad Depot lines** (IDs 201–204).
Track connections detail inter-station distances, low-speed depot shunting times, and shunting cost indices.

#### 1. `GET /api/v1/depots` (Alias: `GET /api/depots`)
Returns list of all depots with capacities, stabling line counts, and live occupancy.

**Sample Response (`200 OK`)**:
```json
{
  "total_depots": 2,
  "depots": [
    {
      "depot_id": "DEPOT-MUTTOM",
      "name": "Muttom Main Depot & Maintenance Workshop",
      "total_stabling_lines": 8,
      "total_inspection_bays": 4,
      "total_capacity": 20,
      "current_occupancy": 8,
      "available_capacity": 12,
      "stabled_train_ids": ["KM-101", "KM-102", "KM-103", "KM-104", "KM-105", "KM-106", "KM-107", "KM-108"],
      "location_ids": [101, 102, 103, 104, 105, 106, 107, 108]
    }
  ]
}
```

#### 2. `GET /api/v1/locations` (Alias: `GET /api/locations`)
Returns complete list of all 36 stations and depot tracks with capacities and current occupancy.

#### 3. `GET /api/v1/locations/{location_id}`
Returns details for a specific location.

**Sample Request**: `GET /api/v1/locations/101`  
**Sample Response (`200 OK`)**:
```json
{
  "location_id": 101,
  "name": "Muttom Depot Stabling Line 1",
  "depot": "Muttom Depot",
  "type": "STABLING_LINE",
  "capacity": 2,
  "occupied_count": 1,
  "available_capacity": 1,
  "stabled_train_ids": ["KM-101"],
  "is_depot_track": true
}
```

#### 4. `GET /api/v1/locations/{location_id}/connections`
Returns outbound track connections from a location including distance, movement time, and shunting cost.

**Sample Request**: `GET /api/v1/locations/5/connections` (Muttom Station)  
**Sample Response (`200 OK`)**:
```json
{
  "location_id": 5,
  "location_name": "Muttom Station",
  "total_connections": 10,
  "connections": [
    {
      "from_location_id": 5,
      "from_location_name": "Muttom Station",
      "to_location_id": 6,
      "to_location_name": "Kalamassery Station",
      "distance_meters": 1700.0,
      "movement_time_minutes": 2.8,
      "movement_cost": 85.0,
      "track_type": "MAINLINE"
    },
    {
      "from_location_id": 5,
      "from_location_name": "Muttom Station",
      "to_location_id": 101,
      "to_location_name": "Muttom Depot Stabling Line 1",
      "distance_meters": 450.0,
      "movement_time_minutes": 3.0,
      "movement_cost": 45.0,
      "track_type": "DEPOT_SHUNTING"
    }
  ]
}
```

#### 5. `GET /api/v1/trains/{train_id}/location`
Returns current location, depot name, track type, and stabling state of a specific trainset.

**Sample Request**: `GET /api/v1/trains/KM-101/location`  
**Sample Response (`200 OK`)**:
```json
{
  "train_id": "KM-101",
  "location_id": 101,
  "location_name": "Muttom Depot Stabling Line 1",
  "depot": "Muttom Depot",
  "type": "STABLING_LINE",
  "is_depot_track": true
}
```

---

### 🔮 Additional Engine Endpoints

- `GET /api/v1/fleet/health` - Subsystem risk breakdown across the fleet.
- `GET /api/v1/demand/crowding` - Station passenger flow and bottleneck alerts.
- `POST /api/v1/chart/optimize` - CP-SAT schedule optimization.
- `POST /api/v1/chart/evaluate` - Induction chart efficiency & delay evaluator.
- `POST /api/v1/simulate/whatif` - Stress testing simulated train failures.
- `POST /api/v1/closed-loop/feedback` - Continuous learning & model drift tracker.

---

## 📌 Field Availability Notice

* **Available Fields**: `train_id`, `train_type`, `current_location_id`, `current_location_name`, `health_score`, `next_day_failure_prob`, `consequence_score`, `subsystem_risks` (`brakes`, `doors`, `hvac`, `traction`), `primary_risk_subsystem`, `maintenance_urgency`, `brake_pad_wear_pct`, `door_cycles`, `hvac_pressure_psi`, `traction_motor_temp_c`, `mileage_km`, `days_since_ibl`, `past_30d_delays`, `past_30d_faults`.
* **Live IoT & Location Overlay**: Submitting IoT telemetry with `location_id` dynamically updates the train's position and reflects on `GET /api/v1/trains`, `GET /api/v1/trains/{train_id}`, and `GET /api/v1/locations`!


