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

### 🔮 Additional Engine Endpoints

- `GET /api/v1/fleet/health` - Subsystem risk breakdown across the fleet.
- `GET /api/v1/demand/crowding` - Station passenger flow and bottleneck alerts.
- `POST /api/v1/chart/optimize` - CP-SAT schedule optimization.
- `POST /api/v1/chart/evaluate` - Induction chart efficiency & delay evaluator.
- `POST /api/v1/simulate/whatif` - Stress testing simulated train failures.
- `POST /api/v1/closed-loop/feedback` - Continuous learning & model drift tracker.

---

## 📌 Field Availability Notice

* **Available Fields**: `train_id`, `train_type`, `health_score`, `next_day_failure_prob`, `consequence_score`, `subsystem_risks` (`brakes`, `doors`, `hvac`, `traction`), `primary_risk_subsystem`, `maintenance_urgency`, `brake_pad_wear_pct`, `door_cycles`, `hvac_pressure_psi`, `traction_motor_temp_c`, `mileage_km`, `days_since_ibl`, `past_30d_delays`, `past_30d_faults`.
* **Currently Unpopulated Fields**: GPS real-time location, fitness certificate expiry dates, job-card status, and branding priority (to be connected in IoT / Eligibility phases).
