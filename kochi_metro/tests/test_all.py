import unittest
from fastapi.testclient import TestClient

from kochi_metro.data.generator import KochiMetroDataGenerator, KOCHI_STATIONS
from kochi_metro.ml.health_predictor import TrainHealthPredictor
from kochi_metro.ml.demand_predictor import PassengerDemandPredictor
from kochi_metro.optimizer.chart_optimizer import ResilienceChartOptimizer
from kochi_metro.ml.chart_evaluator import ChartEfficiencyEvaluator
from kochi_metro.ml.closed_loop import ClosedLoopSimulatorEngine
from kochi_metro.api.main import app

class TestKochiMetroEngine(unittest.TestCase):
    """
    Comprehensive Unit Test Suite for Kochi Metro ML, Optimizer, and API Engine.
    """

    def setUp(self):
        self.gen = KochiMetroDataGenerator()
        self.health_predictor = TrainHealthPredictor()
        self.demand_predictor = PassengerDemandPredictor()
        self.optimizer = ResilienceChartOptimizer()
        self.evaluator = ChartEfficiencyEvaluator()
        self.simulator = ClosedLoopSimulatorEngine()
        self.client = TestClient(app)

    def test_01_data_generator(self):
        fleet_df = self.gen.generate_current_fleet_status()
        self.assertEqual(len(fleet_df), 25)
        self.assertIn("brake_pad_wear_pct", fleet_df.columns)
        self.assertIn("door_cycles", fleet_df.columns)

        demand = self.gen.generate_station_demand()
        self.assertEqual(len(demand), len(KOCHI_STATIONS))

    def test_02_health_predictor(self):
        fleet_df = self.gen.generate_current_fleet_status()
        predictions = self.health_predictor.predict_fleet_health(fleet_df)
        self.assertEqual(len(predictions), 25)

        for p in predictions:
            self.assertGreaterEqual(p["health_score"], 0.0)
            self.assertLessEqual(p["health_score"], 100.0)
            self.assertGreaterEqual(p["next_day_failure_prob"], 0.0)
            self.assertLessEqual(p["next_day_failure_prob"], 1.0)
            self.assertIn("brakes", p["subsystem_risks"])
            self.assertIn(p["maintenance_urgency"], ["HIGH", "MEDIUM", "LOW"])

    def test_03_demand_predictor(self):
        flow = self.demand_predictor.predict_corridor_flow(is_peak_hour=True)
        self.assertIn("station_profiles", flow)
        self.assertEqual(len(flow["station_profiles"]), 24)
        self.assertGreater(flow["max_onboard_passengers"], 0)
        self.assertIsInstance(flow["proactive_passenger_alerts"], list)

    def test_04_chart_optimizer(self):
        fleet_df = self.gen.generate_current_fleet_status()
        predictions = self.health_predictor.predict_fleet_health(fleet_df)
        chart = self.optimizer.optimize_induction_chart(predictions)

        self.assertIn(chart["status"], ["OPTIMAL_FEASIBLE", "HEURISTIC_FEASIBLE"])
        self.assertEqual(chart["active_count"], 18)
        self.assertEqual(chart["standby_count"], 3)
        self.assertEqual(chart["active_count"] + chart["standby_count"] + chart["maintenance_count"], 25)

    def test_05_chart_evaluator(self):
        fleet_df = self.gen.generate_current_fleet_status()
        predictions = self.health_predictor.predict_fleet_health(fleet_df)
        flow = self.demand_predictor.predict_corridor_flow(is_peak_hour=True)
        chart = self.optimizer.optimize_induction_chart(predictions)

        eval_res = self.evaluator.evaluate_candidate_chart(chart, flow)
        self.assertGreaterEqual(eval_res["expected_chart_efficiency_pct"], 0.0)
        self.assertLessEqual(eval_res["expected_chart_efficiency_pct"], 100.0)
        self.assertGreaterEqual(eval_res["expected_delay_minutes"], 0.0)
        self.assertIn(eval_res["reserve_adequacy"], ["HIGH", "MEDIUM", "LOW"])

    def test_06_whatif_simulator(self):
        fleet_df = self.gen.generate_current_fleet_status()
        predictions = self.health_predictor.predict_fleet_health(fleet_df)
        flow = self.demand_predictor.predict_corridor_flow(is_peak_hour=True)

        sim_res = self.simulator.simulate_what_if_scenario(
            fleet_predictions=predictions,
            corridor_flow=flow,
            failed_train_ids=["KM-102"],
            demand_increase_pct=15.0
        )
        self.assertIn("cascade_disruption_impact", sim_res)
        self.assertIn(sim_res["cascade_disruption_impact"], ["LOW", "MODERATE", "CRITICAL"])

    def test_07_api_endpoints(self):
        # Root Endpoint
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

        # Fleet Health API
        res_health = self.client.get("/api/v1/fleet/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["total_fleet_units"], 25)

        # Demand Crowding API
        res_demand = self.client.get("/api/v1/demand/crowding?is_peak_hour=true")
        self.assertEqual(res_demand.status_code, 200)

        # Optimize Chart API
        res_opt = self.client.post("/api/v1/chart/optimize", json={"day_type": "WEEKDAY", "required_active": 18, "required_standby": 3})
        self.assertEqual(res_opt.status_code, 200)
        self.assertEqual(res_opt.json()["active_count"], 18)

        # Evaluate Chart API
        res_eval = self.client.post("/api/v1/chart/evaluate", json={"day_type": "WEEKDAY"})
        self.assertEqual(res_eval.status_code, 200)
        self.assertIn("expected_chart_efficiency_pct", res_eval.json())

        # WhatIf API
        res_whatif = self.client.post("/api/v1/simulate/whatif", json={"failed_train_ids": ["KM-105"], "demand_increase_pct": 20.0})
        self.assertEqual(res_whatif.status_code, 200)
        self.assertIn("revised_efficiency_score_pct", res_whatif.json())

if __name__ == "__main__":
    unittest.main()
