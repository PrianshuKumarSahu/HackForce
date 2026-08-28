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

# Routes
@app.get("/")
def read_root():
    return {
        "service": "Kochi Metro Next-Gen AI Operations Platform",
        "status": "ONLINE",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/fleet/health",
            "/api/v1/demand/crowding",
            "/api/v1/chart/optimize",
            "/api/v1/chart/evaluate",
            "/api/v1/simulate/whatif",
            "/api/v1/closed-loop/feedback"
        ]
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
