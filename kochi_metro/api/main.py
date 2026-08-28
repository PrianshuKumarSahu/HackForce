from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from kochi_metro.data.generator import KochiMetroDataGenerator
from kochi_metro.ml.health_predictor import TrainHealthPredictor
from kochi_metro.ml.demand_predictor import PassengerDemandPredictor
from kochi_metro.optimizer.chart_optimizer import ResilienceChartOptimizer
from kochi_metro.ml.chart_evaluator import ChartEfficiencyEvaluator
from kochi_metro.ml.closed_loop import ClosedLoopSimulatorEngine
from kochi_metro.data.state import state_store
from kochi_metro.data.locations import location_manager

app = FastAPI(
    title="Kochi Metro Next-Gen AI Operations & Prediction Engine API",
    description="Production REST API providing ML predictions, CP-SAT resilience optimization, chart efficiency evaluation, IoT Telemetry ingestion, Event management, and Location/Depot stabling topology.",
    version="1.0.0"
)

# Global Engine Instances
data_gen = KochiMetroDataGenerator()
health_predictor = TrainHealthPredictor()
demand_predictor = PassengerDemandPredictor()
optimizer = ResilienceChartOptimizer()
chart_evaluator = ChartEfficiencyEvaluator()
simulator_engine = ClosedLoopSimulatorEngine()

# Pydantic Input Models
class OptimizeChartRequest(BaseModel):
    day_type: Optional[str] = Field("WEEKDAY", description="WEEKDAY, WEEKEND, or EVENT")
    required_active: Optional[int] = Field(18, ge=1, le=25)
    required_standby: Optional[int] = Field(3, ge=0, le=10)

class WhatIfSimulationRequest(BaseModel):
    failed_train_ids: Optional[List[str]] = Field(default_factory=list, description="List of train IDs simulating failure (e.g. ['KM-104'])")
    demand_increase_pct: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Simulated percentage increase in passenger demand")
    day_type: Optional[str] = Field("WEEKDAY", description="WEEKDAY, WEEKEND, or EVENT")

class FeedbackLogRequest(BaseModel):
    predicted_efficiency_score: float
    actual_efficiency_score: float
    predicted_delay_minutes: float
    actual_delay_minutes: float

# Pydantic Response Models for Trains
class SubsystemRisks(BaseModel):
    brakes: float = Field(..., description="Brake subsystem failure risk score (0.0 to 1.0)")
    doors: float = Field(..., description="Door subsystem failure risk score (0.0 to 1.0)")
    hvac: float = Field(..., description="HVAC subsystem failure risk score (0.0 to 1.0)")
    traction: float = Field(..., description="Traction motor failure risk score (0.0 to 1.0)")

class TrainTelemetryMetrics(BaseModel):
    brake_pad_wear_pct: float = Field(..., description="Brake pad wear percentage")
    door_cycles: int = Field(..., description="Total door opening/closing cycles")
    hvac_pressure_psi: float = Field(..., description="HVAC system pressure in PSI")
    traction_motor_temp_c: float = Field(..., description="Traction motor temperature in Celsius")
    mileage_km: float = Field(..., description="Total operational mileage in kilometers")
    days_since_ibl: int = Field(..., description="Days since last Inspection & Maintenance (IBL)")
    past_30d_delays: int = Field(..., description="Number of delays caused in past 30 days")
    past_30d_faults: int = Field(..., description="Number of minor faults logged in past 30 days")

class TrainDetailResponse(BaseModel):
    train_id: str = Field(..., description="Unique trainset identifier (e.g., 'KM-101')")
    train_type: str = Field("Alstom Metropolis 3-Car", description="Trainset manufacturer and car configuration")
    current_location_id: int = Field(..., description="ID of current station or depot track location")
    current_location_name: str = Field(..., description="Name of current location")
    health_score: float = Field(..., description="Overall health score (0.0 to 100.0)")
    next_day_failure_prob: float = Field(..., description="Predicted failure probability for next operating day (0.0 to 1.0)")
    consequence_score: float = Field(..., description="Consequence-weighted operational disruption impact score")
    subsystem_risks: SubsystemRisks = Field(..., description="Breakdown of failure risk by component subsystem")
    primary_risk_subsystem: str = Field(..., description="Subsystem with the highest calculated risk")
    maintenance_urgency: str = Field(..., description="Maintenance urgency rating: 'HIGH', 'MEDIUM', or 'LOW'")
    telemetry: TrainTelemetryMetrics = Field(..., description="Raw operational telemetry metrics")
    notes: Optional[str] = Field("Fitness certs and job-card status currently unpopulated in base telemetry.", description="Audit notes")

class FleetTrainsResponse(BaseModel):
    total_trains: int = Field(..., description="Total count of trains returned")
    trains: List[TrainDetailResponse] = Field(..., description="List of train objects")

# Pydantic Models for Depots & Locations
class DepotSummaryResponse(BaseModel):
    depot_id: str = Field(..., description="Depot code identifier")
    name: str = Field(..., description="Full depot name")
    total_stabling_lines: int = Field(..., description="Number of stabling lines")
    total_inspection_bays: int = Field(..., description="Number of inspection bays")
    total_capacity: int = Field(..., description="Maximum train capacity")
    current_occupancy: int = Field(..., description="Current count of stabled trains")
    available_capacity: int = Field(..., description="Remaining available stabling slots")
    stabled_train_ids: List[str] = Field(..., description="IDs of trains currently stabled")
    location_ids: List[int] = Field(..., description="Associated location IDs")

class DepotsListResponse(BaseModel):
    total_depots: int = Field(..., description="Total count of depots")
    depots: List[DepotSummaryResponse] = Field(..., description="List of depot summaries")

class LocationDetailResponse(BaseModel):
    location_id: int = Field(..., description="Unique location integer ID")
    name: str = Field(..., description="Location name")
    depot: str = Field(..., description="Associated depot or line section")
    type: str = Field(..., description="Location type ('MAINLINE_STATION', 'STABLING_LINE', 'INSPECTION_BAY', 'WASH_PLANT')")
    capacity: int = Field(..., description="Maximum train capacity")
    occupied_count: int = Field(..., description="Number of trains currently present")
    available_capacity: int = Field(..., description="Available capacity slots")
    stabled_train_ids: List[str] = Field(..., description="List of train IDs currently present")
    is_depot_track: bool = Field(..., description="Whether this location is inside a depot facility")

class LocationsListResponse(BaseModel):
    total_locations: int = Field(..., description="Total count of locations")
    locations: List[LocationDetailResponse] = Field(..., description="List of locations")

class TrackConnectionResponse(BaseModel):
    from_location_id: int = Field(..., description="Origin location ID")
    from_location_name: str = Field(..., description="Origin location name")
    to_location_id: int = Field(..., description="Destination location ID")
    to_location_name: str = Field(..., description="Destination location name")
    distance_meters: float = Field(..., description="Track distance in meters")
    movement_time_minutes: float = Field(..., description="Estimated shunting/transit time in minutes")
    movement_cost: float = Field(..., description="Energy/shunting cost index")
    track_type: str = Field(..., description="Track classification ('MAINLINE', 'DEPOT_SHUNTING')")

class LocationConnectionsResponse(BaseModel):
    location_id: int = Field(..., description="Origin location ID")
    location_name: str = Field(..., description="Origin location name")
    total_connections: int = Field(..., description="Count of outbound track connections")
    connections: List[TrackConnectionResponse] = Field(..., description="List of outbound track connections")

class TrainLocationResponse(BaseModel):
    train_id: str = Field(..., description="Trainset ID")
    location_id: int = Field(..., description="Current location ID")
    location_name: str = Field(..., description="Current location name")
    depot: str = Field(..., description="Associated depot or mainline section")
    type: str = Field(..., description="Location type")
    is_depot_track: bool = Field(..., description="Whether train is parked in a depot track")


# Pydantic Models for IoT Telemetry & Events
class IoTTelemetryRequest(BaseModel):
    train_id: str = Field(..., description="Target train ID (e.g. 'KM-101')")
    temperature_c: Optional[float] = Field(25.0, ge=-50.0, le=100.0, description="Ambient compartment temperature in Celsius")
    humidity_pct: Optional[float] = Field(50.0, ge=0.0, le=100.0, description="Ambient humidity percentage")
    vibration: Optional[float] = Field(0.05, ge=0.0, le=50.0, description="Structural vibration level")
    brake_pad_wear_pct: Optional[float] = Field(30.0, ge=0.0, le=100.0, description="Brake pad wear percentage")
    door_cycles: Optional[int] = Field(10000, ge=0, description="Total door cycles")
    hvac_pressure_psi: Optional[float] = Field(60.0, ge=0.0, le=200.0, description="HVAC pressure in PSI")
    traction_motor_temp_c: Optional[float] = Field(60.0, ge=-50.0, le=200.0, description="Traction motor temperature in Celsius")
    mileage_km: Optional[float] = Field(10000.0, ge=0.0, description="Total mileage in km")
    location_id: Optional[int] = Field(1, ge=1, description="Station or depot location ID")
    timestamp: Optional[str] = Field(None, description="ISO timestamp string")

class AnomalyDetail(BaseModel):
    type: str = Field(..., description="Anomaly classification code")
    severity: str = Field(..., description="Severity level: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'")
    description: str = Field(..., description="Detailed anomaly narrative")

class IoTTelemetryResponse(BaseModel):
    status: str = Field(..., description="'accepted' or 'accepted_with_alert'")
    train_id: str = Field(..., description="Target train ID")
    anomalies: List[AnomalyDetail] = Field(default_factory=list, description="Detected telemetry anomalies")
    event_ids: List[str] = Field(default_factory=list, description="IDs of newly created events")
    timestamp: str = Field(..., description="Processing timestamp")

class EventDetailResponse(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    train_id: str = Field(..., description="Associated train ID")
    event_type: str = Field(..., description="Event rule type")
    severity: str = Field(..., description="Event severity rating")
    description: str = Field(..., description="Event description")
    source: str = Field("IOT", description="Originating source")
    occurred_at: str = Field(..., description="Timestamp when event occurred")
    processed_at: str = Field(..., description="Timestamp when event was ingested")
    status: str = Field("OPEN", description="Event lifecycle status")

class EventsListResponse(BaseModel):
    total_events: int = Field(..., description="Total count of matching events")
    events: List[EventDetailResponse] = Field(..., description="List of event objects")

class TelemetryHistoryResponse(BaseModel):
    train_id: str = Field(..., description="Target train ID")
    record_count: int = Field(..., description="Count of historical telemetry records returned")
    history: List[Dict[str, Any]] = Field(..., description="List of telemetry records")

# Helper function to compile complete train objects with live IoT overlay
def _get_all_trains_data() -> List[Dict[str, Any]]:
    fleet_status_df = data_gen.generate_current_fleet_status()
    
    # Overlay live IoT telemetry if recorded
    for idx, row in fleet_status_df.iterrows():
        t_id = row["train_id"]
        latest_iot = state_store.get_latest_telemetry(t_id)
        if latest_iot:
            fleet_status_df.at[idx, "brake_pad_wear_pct"] = latest_iot["brake_pad_wear_pct"]
            fleet_status_df.at[idx, "door_cycles"] = latest_iot["door_cycles"]
            fleet_status_df.at[idx, "hvac_pressure_psi"] = latest_iot["hvac_pressure_psi"]
            fleet_status_df.at[idx, "traction_motor_temp_c"] = latest_iot["traction_motor_temp_c"]
            fleet_status_df.at[idx, "mileage_km"] = latest_iot["mileage_km"]

    predictions = health_predictor.predict_fleet_health(fleet_status_df)
    telemetry_map = {row["train_id"]: row.to_dict() for _, row in fleet_status_df.iterrows()}
    
    trains_list = []
    for pred in predictions:
        t_id = pred["train_id"]
        raw = telemetry_map.get(t_id, {})
        loc_id = location_manager.get_train_location_id(t_id) or 1
        loc_details = location_manager.get_location_details(loc_id)
        loc_name = loc_details["name"] if loc_details else "Unknown Location"

        train_data = {
            "train_id": t_id,
            "train_type": "Alstom Metropolis 3-Car",
            "current_location_id": loc_id,
            "current_location_name": loc_name,
            "health_score": pred["health_score"],
            "next_day_failure_prob": pred["next_day_failure_prob"],
            "consequence_score": pred["consequence_score"],
            "subsystem_risks": pred["subsystem_risks"],
            "primary_risk_subsystem": pred["primary_risk_subsystem"],
            "maintenance_urgency": pred["maintenance_urgency"],
            "telemetry": {
                "brake_pad_wear_pct": raw.get("brake_pad_wear_pct", 0.0),
                "door_cycles": raw.get("door_cycles", 0),
                "hvac_pressure_psi": raw.get("hvac_pressure_psi", 0.0),
                "traction_motor_temp_c": raw.get("traction_motor_temp_c", 0.0),
                "mileage_km": raw.get("mileage_km", 0.0),
                "days_since_ibl": raw.get("days_since_ibl", 0),
                "past_30d_delays": raw.get("past_30d_delays", 0),
                "past_30d_faults": raw.get("past_30d_faults", 0)
            },
            "notes": "Fitness certs and job-card status currently unpopulated in base telemetry."
        }
        trains_list.append(train_data)
    return trains_list

# Routes
@app.get("/")
def read_root():
    return {
        "service": "Kochi Metro Next-Gen AI Operations Platform",
        "status": "ONLINE",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/trains",
            "/api/v1/trains/{train_id}",
            "/api/v1/trains/{train_id}/location",
            "/api/v1/depots",
            "/api/v1/locations",
            "/api/v1/locations/{location_id}",
            "/api/v1/locations/{location_id}/connections",
            "/api/v1/iot/telemetry",
            "/api/v1/events",
            "/api/v1/fleet/health",
            "/api/v1/demand/crowding",
            "/api/v1/chart/optimize"
        ]
    }

# -----------------------------------------------------------------------------
# KMRL Location & Depot APIs
# -----------------------------------------------------------------------------
@app.get("/api/v1/depots", response_model=DepotsListResponse, tags=["Depots & Locations"])
@app.get("/api/depots", response_model=DepotsListResponse, tags=["Depots & Locations"], include_in_schema=False)
def get_all_depots():
    """
    Returns list of all KMRL depots (Muttom & Kakkanad) with capacity, line counts, and current occupancy.
    """
    depots = location_manager.get_depot_summaries()
    return {
        "total_depots": len(depots),
        "depots": depots
    }

@app.get("/api/v1/locations", response_model=LocationsListResponse, tags=["Depots & Locations"])
@app.get("/api/locations", response_model=LocationsListResponse, tags=["Depots & Locations"], include_in_schema=False)
def get_all_locations():
    """
    Returns complete list of all 24 stations and depot tracks with capacities and current occupancy.
    """
    locations = location_manager.get_all_locations_with_occupancy()
    return {
        "total_locations": len(locations),
        "locations": locations
    }

@app.get("/api/v1/locations/{location_id}", response_model=LocationDetailResponse, tags=["Depots & Locations"])
@app.get("/api/locations/{location_id}", response_model=LocationDetailResponse, tags=["Depots & Locations"], include_in_schema=False)
def get_location_by_id(location_id: int):
    """
    Returns detailed capacity, occupancy, and stabled train IDs for a specific location. Raises 404 if invalid.
    """
    details = location_manager.get_location_details(location_id)
    if not details:
        raise HTTPException(status_code=404, detail=f"Location ID '{location_id}' not found in network.")
    return details

@app.get("/api/v1/locations/{location_id}/connections", response_model=LocationConnectionsResponse, tags=["Depots & Locations"])
@app.get("/api/locations/{location_id}/connections", response_model=LocationConnectionsResponse, tags=["Depots & Locations"], include_in_schema=False)
def get_location_connections(location_id: int):
    """
    Returns outbound track connections from location_id including track distance, movement time, and shunting cost.
    """
    loc_details = location_manager.get_location_details(location_id)
    if not loc_details:
        raise HTTPException(status_code=404, detail=f"Location ID '{location_id}' not found in network.")

    connections = location_manager.get_connections_for_location(location_id)
    return {
        "location_id": location_id,
        "location_name": loc_details["name"],
        "total_connections": len(connections),
        "connections": connections
    }

@app.get("/api/v1/trains/{train_id}/location", response_model=TrainLocationResponse, tags=["Trains"])
@app.get("/api/trains/{train_id}/location", response_model=TrainLocationResponse, tags=["Trains"], include_in_schema=False)
def get_train_location(train_id: str):
    """
    Returns current location, depot name, track type, and stabling state of a specific trainset.
    """
    train_id_upper = train_id.upper()
    valid_train_ids = [f"KM-{101 + i}" for i in range(25)]
    if train_id_upper not in valid_train_ids:
        raise HTTPException(status_code=404, detail=f"Train '{train_id}' not found in fleet.")

    loc_id = location_manager.get_train_location_id(train_id_upper) or 1
    loc_details = location_manager.get_location_details(loc_id)
    if not loc_details:
        raise HTTPException(status_code=500, detail=f"Location ID '{loc_id}' has invalid details.")

    return {
        "train_id": train_id_upper,
        "location_id": loc_id,
        "location_name": loc_details["name"],
        "depot": loc_details["depot"],
        "type": loc_details["type"],
        "is_depot_track": loc_details["is_depot_track"]
    }


@app.get("/api/v1/trains", response_model=FleetTrainsResponse, tags=["Trains"])
@app.get("/api/trains", response_model=FleetTrainsResponse, tags=["Trains"], include_in_schema=False)
def get_all_trains():
    """
    Returns complete operational telemetry and ML health predictions for all 25 fleet units.
    
    Exposes existing fleet telemetry (mileage, subsystem sensors, fault history)
    merged with ML predictions (health score, failure risk, subsystem breakdown, maintenance urgency).
    """
    trains = _get_all_trains_data()
    return {
        "total_trains": len(trains),
        "trains": trains
    }

@app.get("/api/v1/trains/{train_id}", response_model=TrainDetailResponse, tags=["Trains"])
@app.get("/api/trains/{train_id}", response_model=TrainDetailResponse, tags=["Trains"], include_in_schema=False)
def get_train_by_id(train_id: str):
    """
    Returns detailed operational telemetry and ML health predictions for a specific train unit by ID (e.g. 'KM-101').
    
    Raises HTTP 404 if the specified train ID is not found in the fleet.
    """
    trains = _get_all_trains_data()
    for train in trains:
        if train["train_id"].upper() == train_id.upper():
            return train
    raise HTTPException(status_code=404, detail=f"Train '{train_id}' not found in fleet.")

# -----------------------------------------------------------------------------
# IoT Telemetry & Anomaly Ingestion APIs (Phase 5)
# -----------------------------------------------------------------------------
@app.post("/api/v1/iot/telemetry", response_model=IoTTelemetryResponse, tags=["IoT Telemetry"])
def ingest_iot_telemetry(req: IoTTelemetryRequest):
    """
    Ingests live sensor telemetry payload from IoT sensors (ESP32) or simulator.
    
    Validates train_id, runs threshold-based anomaly detection, creates events for alerts,
    updates train state, and stores record in telemetry history.
    """
    # 1. Validate train_id exists in fleet
    train_id_upper = req.train_id.upper()
    valid_train_ids = [f"KM-{101 + i}" for i in range(25)]
    if train_id_upper not in valid_train_ids:
        raise HTTPException(status_code=404, detail=f"Train '{req.train_id}' not found in fleet.")

    # Validate location_id if provided
    if req.location_id is not None:
        if not location_manager.is_valid_location_id(req.location_id):
            raise HTTPException(status_code=422, detail=f"Invalid location_id '{req.location_id}'. Location does not exist in network.")
        location_manager.update_train_location(train_id_upper, req.location_id)

    # 2. Ingest telemetry into state store
    raw_dict = req.dict()
    anomalies, created_events = state_store.record_telemetry(raw_dict)

    status_str = "accepted_with_alert" if anomalies else "accepted"
    event_ids = [e["event_id"] for e in created_events]
    timestamp_str = req.timestamp or datetime.now().isoformat()

    return {
        "status": status_str,
        "train_id": train_id_upper,
        "anomalies": anomalies,
        "event_ids": event_ids,
        "timestamp": timestamp_str
    }

@app.get("/api/v1/iot/{train_id}/telemetry", response_model=TelemetryHistoryResponse, tags=["IoT Telemetry"])
def get_train_telemetry_history(
    train_id: str,
    limit: int = Query(20, ge=1, le=500, description="Max historical telemetry records to return")
):
    """
    Returns recent telemetry history logs for a specific train set (newest first).
    """
    train_id_upper = train_id.upper()
    valid_train_ids = [f"KM-{101 + i}" for i in range(25)]
    if train_id_upper not in valid_train_ids:
        raise HTTPException(status_code=404, detail=f"Train '{train_id}' not found in fleet.")

    history = state_store.get_telemetry_history(train_id_upper, limit=limit)
    return {
        "train_id": train_id_upper,
        "record_count": len(history),
        "history": history
    }

# -----------------------------------------------------------------------------
# Event Management APIs (Phase 6)
# -----------------------------------------------------------------------------
@app.get("/api/v1/events", response_model=EventsListResponse, tags=["Events"])
@app.get("/api/events", response_model=EventsListResponse, tags=["Events"], include_in_schema=False)
def get_all_events(
    train_id: Optional[str] = Query(None, description="Filter events by train ID (e.g. 'KM-101')"),
    severity: Optional[str] = Query(None, description="Filter by severity: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'"),
    status: Optional[str] = Query(None, description="Filter by status: 'OPEN', 'RESOLVED'"),
    source: Optional[str] = Query(None, description="Filter by source: 'IOT'")
):
    """
    Returns system events and IoT anomaly alerts with optional filters.
    """
    events = state_store.get_events(train_id=train_id, severity=severity, status=status, source=source)
    return {
        "total_events": len(events),
        "events": events
    }

@app.get("/api/v1/events/{event_id}", response_model=EventDetailResponse, tags=["Events"])
def get_event_by_id(event_id: str):
    """
    Returns details for a specific event by event_id. Raises 404 if not found.
    """
    event = state_store.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found.")
    return event

@app.get("/api/v1/trains/{train_id}/events", response_model=EventsListResponse, tags=["Events"])
@app.get("/api/trains/{train_id}/events", response_model=EventsListResponse, tags=["Events"], include_in_schema=False)
def get_events_for_train(train_id: str):
    """
    Returns all event records associated with a specific train set.
    """
    train_id_upper = train_id.upper()
    valid_train_ids = [f"KM-{101 + i}" for i in range(25)]
    if train_id_upper not in valid_train_ids:
        raise HTTPException(status_code=404, detail=f"Train '{train_id}' not found in fleet.")

    events = state_store.get_events(train_id=train_id_upper)
    return {
        "total_events": len(events),
        "events": events
    }



@app.get("/api/v1/fleet/health")
def get_fleet_health():
    """
    Returns next-day failure probability, subsystem risk breakdown (Brakes, Doors, HVAC, Traction),
    and consequence-weighted operational impact for all 25 trainsets.
    """
    fleet_status = data_gen.generate_current_fleet_status()
    predictions = health_predictor.predict_fleet_health(fleet_status)
    return {
        "total_fleet_units": len(predictions),
        "predictions": predictions
    }

@app.get("/api/v1/demand/crowding")
def get_corridor_crowding(
    is_peak_hour: bool = Query(True, description="Whether to simulate peak-hour demand"),
    day_type: str = Query("WEEKDAY", description="WEEKDAY, WEEKEND, or EVENT")
):
    """
    Returns station-level passenger boarding/alighting forecasts, train load accumulation,
    bottleneck station alerts, and proactive passenger guidance messages.
    """
    flow = demand_predictor.predict_corridor_flow(is_peak_hour=is_peak_hour, day_type=day_type)
    return flow

@app.post("/api/v1/chart/optimize")
def optimize_induction_chart(req: OptimizeChartRequest):
    """
    Runs CP-SAT resilience optimization to generate the optimal nightly induction plan:
    Active Scheduled, Standby Reserve, and Depot Maintenance.
    """
    fleet_status = data_gen.generate_current_fleet_status()
    predictions = health_predictor.predict_fleet_health(fleet_status)

    optimizer_inst = ResilienceChartOptimizer(required_active=req.required_active, required_standby=req.required_standby)
    chart = optimizer_inst.optimize_induction_chart(predictions, day_type=req.day_type)
    return chart

@app.post("/api/v1/chart/evaluate")
def evaluate_induction_chart(req: OptimizeChartRequest):
    """
    Evaluates candidate induction chart to output Expected Chart Efficiency %, Failure Risk %,
    Expected Delay Minutes, Reserve Adequacy, and Explainable Evidence ('Why?').
    """
    fleet_status = data_gen.generate_current_fleet_status()
    predictions = health_predictor.predict_fleet_health(fleet_status)
    flow = demand_predictor.predict_corridor_flow(is_peak_hour=True, day_type=req.day_type)

    optimizer_inst = ResilienceChartOptimizer(required_active=req.required_active, required_standby=req.required_standby)
    chart = optimizer_inst.optimize_induction_chart(predictions, day_type=req.day_type)

    evaluation = chart_evaluator.evaluate_candidate_chart(chart, flow)
    return evaluation

@app.post("/api/v1/simulate/whatif")
def run_whatif_simulation(req: WhatIfSimulationRequest):
    """
    Simulates operational disruptions ('What if Train X fails?' or 'What if demand spikes by 20%?')
    and returns cascade impact + revised optimization plan.
    """
    fleet_status = data_gen.generate_current_fleet_status()
    predictions = health_predictor.predict_fleet_health(fleet_status)
    flow = demand_predictor.predict_corridor_flow(is_peak_hour=True, day_type=req.day_type)

    res = simulator_engine.simulate_what_if_scenario(
        fleet_predictions=predictions,
        corridor_flow=flow,
        failed_train_ids=req.failed_train_ids,
        demand_increase_pct=req.demand_increase_pct
    )
    return res

@app.post("/api/v1/closed-loop/feedback")
def log_closed_loop_feedback(req: FeedbackLogRequest):
    """
    Logs actual operational performance vs. predictions to track model drift
    and calculate continuous learning error metrics.
    """
    res = simulator_engine.log_actual_outcome(
        predicted_score=req.predicted_efficiency_score,
        actual_score=req.actual_efficiency_score,
        predicted_delay=req.predicted_delay_minutes,
        actual_delay=req.actual_delay_minutes
    )
    return res
