import numpy as np
from typing import Dict, List, Any
from kochi_metro.optimizer.chart_optimizer import ResilienceChartOptimizer
from kochi_metro.ml.chart_evaluator import ChartEfficiencyEvaluator

class ClosedLoopSimulatorEngine:
    """
    Simulation & Closed-Loop Feedback Learning Engine.
    Handles 'What-If' scenario stress testing and predicted vs actual error feedback.
    """
    def __init__(self):
        self.optimizer = ResilienceChartOptimizer()
        self.evaluator = ChartEfficiencyEvaluator()
        self.performance_logs = []

    def simulate_what_if_scenario(
        self,
        fleet_predictions: List[Dict[str, Any]],
        corridor_flow: Dict[str, Any],
        failed_train_ids: List[str] = None,
        demand_increase_pct: float = 0.0
    ) -> Dict[str, Any]:
        """
        Simulates disruption scenarios ('What if Train X fails?' or 'What if demand increases by 20%?')
        and calculates network impact + revised optimization plan.
        """
        if failed_train_ids is None:
            failed_train_ids = []

        # 1. Modify fleet predictions for simulated failure
        simulated_fleet = []
        for p in fleet_predictions:
            p_copy = dict(p)
            if p["train_id"] in failed_train_ids:
                # Mark as 100% failure / IBL maintenance required
                p_copy["next_day_failure_prob"] = 0.99
                p_copy["health_score"] = 0.0
                p_copy["consequence_score"] = 999.0
                p_copy["maintenance_urgency"] = "HIGH"
            simulated_fleet.append(p_copy)

        # 2. Modify demand for simulated surge
        simulated_flow = dict(corridor_flow)
        if demand_increase_pct > 0.0:
            simulated_flow["peak_crowding_pct"] = round(corridor_flow.get("peak_crowding_pct", 85.0) * (1.0 + demand_increase_pct / 100.0), 1)

        # 3. Re-optimize schedule under stress
        revised_chart = self.optimizer.optimize_induction_chart(simulated_fleet)
        evaluation = self.evaluator.evaluate_candidate_chart(revised_chart, simulated_flow)

        cascade_impact = "LOW"
        if len(failed_train_ids) >= 2 or demand_increase_pct >= 25.0:
            cascade_impact = "CRITICAL"
        elif len(failed_train_ids) == 1:
            cascade_impact = "MODERATE"

        return {
            "scenario": f"Simulated failure of {failed_train_ids} with {demand_increase_pct}% demand surge",
            "cascade_disruption_impact": cascade_impact,
            "revised_efficiency_score_pct": evaluation["expected_chart_efficiency_pct"],
            "revised_expected_delay_mins": evaluation["expected_delay_minutes"],
            "revised_reserve_adequacy": evaluation["reserve_adequacy"],
            "revised_chart": evaluation
        }

    def log_actual_outcome(self, predicted_score: float, actual_score: float, predicted_delay: float, actual_delay: float) -> Dict[str, Any]:
        """
        Closed-loop learning: records predicted vs actual operational performance.
        Calculates error and model drift metrics.
        """
        score_error = abs(predicted_score - actual_score)
        delay_error = abs(predicted_delay - actual_delay)

        self.performance_logs.append({
            "predicted_score": predicted_score,
            "actual_score": actual_score,
            "score_error": score_error,
            "predicted_delay": predicted_delay,
            "actual_delay": actual_delay,
            "delay_error": delay_error
        })

        avg_score_mae = float(np.mean([log["score_error"] for log in self.performance_logs]))
        avg_delay_mae = float(np.mean([log["delay_error"] for log in self.performance_logs]))

        drift_detected = avg_score_mae > 8.0 or avg_delay_mae > 5.0

        return {
            "total_logged_days": len(self.performance_logs),
            "efficiency_score_mae": round(avg_score_mae, 2),
            "delay_minutes_mae": round(avg_delay_mae, 2),
            "model_drift_detected": drift_detected,
            "status": "RETRAINING_RECOMMENDED" if drift_detected else "MODEL_STABLE"
        }

if __name__ == "__main__":
    from kochi_metro.data.generator import KochiMetroDataGenerator
    from kochi_metro.ml.health_predictor import TrainHealthPredictor
    from kochi_metro.ml.demand_predictor import PassengerDemandPredictor

    gen = KochiMetroDataGenerator()
    fleet_df = gen.generate_current_fleet_status()
    predictor = TrainHealthPredictor()
    predictions = predictor.predict_fleet_health(fleet_df)

    demand_pred = PassengerDemandPredictor()
    flow = demand_pred.predict_corridor_flow(is_peak_hour=True)

    engine = ClosedLoopSimulatorEngine()
    sim_res = engine.simulate_what_if_scenario(predictions, flow, failed_train_ids=["KM-104"], demand_increase_pct=20.0)
    print("What-If Simulation Result:")
    print(f"Impact: {sim_res['cascade_disruption_impact']}")
    print(f"Revised Efficiency: {sim_res['revised_efficiency_score_pct']}%")
