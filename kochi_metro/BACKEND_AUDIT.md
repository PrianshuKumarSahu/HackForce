# Kochi Metro AI Engine Backend Audit

**Project**: SIH 2026 - AI-Driven Train Induction Planning & Scheduling for Kochi Metro Rail Limited (KMRL)  
**Scope**: `kochi_metro/` directory inspection & gap analysis  
**Audit Date**: August 29, 2026  

---

## 1. Existing System Architecture Overview

The `kochi_metro/` module contains an end-to-end Python AI/ML operations and optimization engine built with **FastAPI**, **scikit-learn**, and **Google OR-Tools CP-SAT**.

```
kochi_metro/
├── api/
│   ├── __init__.py
│   └── main.py                   # FastAPI REST API exposing fleet health, demand, optimization, & simulation
├── data/
│   ├── __init__.py
│   └── generator.py              # Fleet status & station demand data generator (25 Alstom Metropolis trainsets)
├── ml/
│   ├── __init__.py
│   ├── health_predictor.py       # Dual-ML Subsystem Risk & Failure Predictor (GradientBoosting + RandomForest)
│   ├── demand_predictor.py       # Station-level boarding/alighting forecast & corridor crowding engine
│   ├── chart_evaluator.py        # ML Chart Efficiency Evaluator & Explainable Evidence Generator
│   └── closed_loop.py            # Stress simulator & model drift closed-loop feedback engine
├── optimizer/
│   ├── __init__.py
│   └── chart_optimizer.py        # CP-SAT Constraint Programming Resilience Schedule Optimizer
└── tests/
    ├── __init__.py
    └── test_all.py               # Unit test suite covering data gen, ML models, optimizer, & API endpoints
```

---

## 2. Inventory of Existing Functionality

### 2.1 Existing APIs (`api/main.py`)
Currently exposed endpoints under `/api/v1/`:
- `GET /`: Health check & API index.
- `GET /api/v1/fleet/health`: Returns next-day failure probability, subsystem risk breakdown (brakes, doors, HVAC, traction), and consequence-weighted impact scores for all 25 trainsets (`KM-101` to `KM-125`).
- `GET /api/v1/demand/crowding`: Station-level passenger boarding/alighting forecasts, corridor load profile, bottleneck station alerts, and passenger guidance.
- `POST /api/v1/chart/optimize`: Runs CP-SAT optimization to partition fleet into `active_scheduled` (18), `standby_reserve` (3), and `depot_maintenance` (4).
- `POST /api/v1/chart/evaluate`: Evaluates a candidate induction chart returning efficiency score %, failure probability %, delay minutes, and reserve adequacy.
- `POST /api/v1/simulate/whatif`: Simulates failed train IDs and passenger demand surges, returning cascade impact and re-optimized plans.
- `POST /api/v1/closed-loop/feedback`: Logs predicted vs actual outcomes and tracks model drift.

### 2.2 Existing Optimizer Functionality (`optimizer/chart_optimizer.py`)
- **Class**: `ResilienceChartOptimizer`
- **Engine**: Uses Google OR-Tools `cp_model.CpModel()` with integer variables `x[i] ∈ {0: Active, 1: Standby, 2: Maintenance}`.
- **Constraints**:
  - Hard constraint on exact active count (e.g. 18 for Weekday, 14 for Weekend, 20 for Event).
  - Hard constraint on exact standby count (e.g. 3 for Weekday, 2 for Weekend, 4 for Event).
- **Objective Function**: Minimizes `∑ (Consequence_Score * Active_Status + 0.2 * Consequence_Score * Standby_Status)`.
- **Fallback**: Includes a deterministic heuristic sorter if OR-Tools is uninstalled or infeasible.

### 2.3 Existing ML & Prediction Functionality (`ml/`)
- **`health_predictor.py`**:
  - Ensemble models (`GradientBoostingRegressor` for failure probability, `RandomForestRegressor` for subsystem risks: brakes, doors, HVAC, traction).
  - Calculates `health_score` (0–100), `consequence_score` (weighted by mileage exposure), and `maintenance_urgency` (`HIGH`, `MEDIUM`, `LOW`).
- **`demand_predictor.py`**:
  - Station boarding/alighting demand predictor across 24 Kochi Metro stations.
  - Detects corridor bottlenecks and overcrowding risks (>80% and >95% capacity).
- **`chart_evaluator.py`**:
  - Generates efficiency ratings, expected delay minutes, reserve adequacy (`HIGH`/`MEDIUM`/`LOW`), and textual explainability evidence.
- **`closed_loop.py`**:
  - Simulates what-if disruptions and tracks Mean Absolute Error (MAE) between predicted and actual operational metrics to detect model drift (`avg_score_mae > 8.0`).

### 2.4 Existing Data Structures (`data/generator.py`)
- **Fleet Representation**: 25 Alstom Metropolis trainsets identified by `KM-101` through `KM-125`.
- **Telemetry Record**: `train_id`, `brake_pad_wear_pct`, `door_cycles`, `hvac_pressure_psi`, `traction_motor_temp_c`, `mileage_km`, `days_since_ibl`, `past_30d_delays`, `past_30d_faults`.

---

## 3. Analysis of Gaps & Missing APIs

To align the codebase with the full KMRL operational requirements, the following APIs and capabilities are missing:

| Domain | Missing Endpoint / Feature | Description & Requirement |
| :--- | :--- | :--- |
| **Train Management** | `GET /api/trains`<br>`GET /api/trains/{train_id}` | Expose unified train metadata including train status, location, component health, fitness certs, job-card status, mileage, branding priority, and maintenance risk. |
| **IoT Telemetry** | `POST /api/iot/telemetry` | Accept live sensor telemetry (`temperature`, `humidity`, `vibration`, `component_health`, `location_id`, `timestamp`), update train state, and detect anomalies. |
| **Event System** | `GET /api/events`<br>`GET /api/events/{event_id}`<br>`GET /api/trains/{train_id}/events` | In-memory event registry to record and query system alerts, IoT anomalies, and maintenance warnings. |
| **Train Eligibility** | `GET /api/trains/{train_id}/eligibility` | Safety check endpoint verifying if a train is eligible for active service (evaluating critical job cards, fitness certificates, and health thresholds). |
| **LLM Explainability** | `POST /api/llm/explain` | API endpoint wrapping the existing explainability & evidence generator (`chart_evaluator.py`) to provide natural language explanations for train scheduling decisions. |
| **Standard Optimization** | `POST /api/optimization/run` | Standardized wrapper endpoint over `ResilienceChartOptimizer` returning active, standby, and maintenance assignments with decision reasons. |
| **Standard Plan APIs** | `GET /api/plans/{plan_id}`<br>`GET /api/plans/{plan_id}/assignments` | Query generated induction plans and individual train role assignments. |
| **Standard What-If** | `POST /api/optimization/what-if` | Standardized alias endpoint matching the required spec for temporary disruption stress testing. |
| **Human Override** | `POST /api/plans/{plan_id}/override` | Endpoint to record manual operator overrides (train, original assignment, new assignment, reason, operator ID, timestamp). |

---

## 4. Persistent DB & Implementation Status

- **Database**: Currently operates fully **in-memory** using synthetic generators. Persistence layer is not required by existing logic and can be handled via in-memory state stores to avoid introducing unnecessary dependencies.
- **LLM Mechanism**: The codebase uses rule-based evidence synthesis in `chart_evaluator.py` rather than an external LLM API key. Wrapping this in a clean `/api/llm/explain` endpoint exposes the required natural language explanations seamlessly.

---

## 5. Recommended Implementation Order

To preserve existing working code and execute Phases 2 through 15 cleanly:

1. **State Store & Event Registry (`kochi_metro/data/state.py`)**: Create an in-memory repository to hold current train states, IoT telemetry history, events, generated plans, and override logs.
2. **Train & Eligibility APIs (Phases 3 & 7)**: Implement `GET /api/trains`, `GET /api/trains/{train_id}`, and `GET /api/trains/{train_id}/eligibility`.
3. **IoT Telemetry & Events APIs (Phases 5 & 6)**: Implement `POST /api/iot/telemetry` with anomaly detection and event creation, plus `GET /api/events` family.
4. **Optimization, Plan & Override APIs (Phases 8, 9, 10 & 11)**: Implement `POST /api/optimization/run`, `GET /api/plans/{plan_id}`, `POST /api/optimization/what-if`, and `POST /api/plans/{plan_id}/override`.
5. **LLM Explanation API (Phase 4)**: Implement `POST /api/llm/explain` exposing the existing evidence generation logic.
6. **Documentation & Test Suite (Phases 13, 14 & 15)**: Update `test_all.py` and create `BACKEND_README.md`.
