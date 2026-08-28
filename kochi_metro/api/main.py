from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from kochi_metro.data.generator import KochiMetroDataGenerator
from kochi_metro.ml.health_predictor import TrainHealthPredictor
from kochi_metro.ml.demand_predictor import PassengerDemandPredictor
from kochi_metro.optimizer.chart_optimizer import ResilienceChartOptimizer
from kochi_metro.ml.chart_evaluator import ChartEfficiencyEvaluator
from kochi_metro.ml.closed_loop import ClosedLoopSimulatorEngine

app = FastAPI(
    title="Kochi Metro Next-Gen AI Operations & Prediction Engine API",
    description="Production REST API providing ML predictions, CP-SAT resilience optimization, chart efficiency evaluation, and What-If disruption simulations.",
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
    health_score: float = Field(..., description="Overall health score (0.0 to 100.0)")
    next_day_failure_prob: float = Field(..., description="Predicted failure probability for next operating day (0.0 to 1.0)")
    consequence_score: float = Field(..., description="Consequence-weighted operational disruption impact score")
    subsystem_risks: SubsystemRisks = Field(..., description="Breakdown of failure risk by component subsystem")
    primary_risk_subsystem: str = Field(..., description="Subsystem with the highest calculated risk")
    maintenance_urgency: str = Field(..., description="Maintenance urgency rating: 'HIGH', 'MEDIUM', or 'LOW'")
    telemetry: TrainTelemetryMetrics = Field(..., description="Raw operational telemetry metrics")
    notes: Optional[str] = Field("Location tracking, fitness certs, and job-card status currently unpopulated in base telemetry.", description="Audit notes on unpopulated enterprise fields")

class FleetTrainsResponse(BaseModel):
    total_trains: int = Field(..., description="Total count of trains returned")
    trains: List[TrainDetailResponse] = Field(..., description="List of train objects")

# Helper function to compile complete train objects
def _get_all_trains_data() -> List[Dict[str, Any]]:
    fleet_status_df = data_gen.generate_current_fleet_status()
    predictions = health_predictor.predict_fleet_health(fleet_status_df)
    
    telemetry_map = {row["train_id"]: row.to_dict() for _, row in fleet_status_df.iterrows()}
    
    trains_list = []
    for pred in predictions:
        t_id = pred["train_id"]
        raw = telemetry_map.get(t_id, {})
        train_data = {
            "train_id": t_id,
            "train_type": "Alstom Metropolis 3-Car",
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
            "notes": "Location tracking, fitness certs, and job-card status currently unpopulated in base telemetry."
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
            "/api/v1/fleet/health",
            "/api/v1/demand/crowding",
            "/api/v1/chart/optimize",
            "/api/v1/chart/evaluate",
            "/api/v1/simulate/whatif",
            "/api/v1/closed-loop/feedback"
        ]
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
