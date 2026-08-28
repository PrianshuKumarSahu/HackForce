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

    def test_08_trains_api(self):
        # GET /api/v1/trains (All trains)
        res_trains = self.client.get("/api/v1/trains")
        self.assertEqual(res_trains.status_code, 200)
        data = res_trains.json()
        self.assertEqual(data["total_trains"], 25)
        self.assertEqual(len(data["trains"]), 25)
        first_train = data["trains"][0]
        self.assertIn("train_id", first_train)
        self.assertIn("health_score", first_train)
        self.assertIn("subsystem_risks", first_train)
        self.assertIn("telemetry", first_train)

        # GET /api/v1/trains/{train_id} (Valid train ID)
        train_id = first_train["train_id"]
        res_single = self.client.get(f"/api/v1/trains/{train_id}")
        self.assertEqual(res_single.status_code, 200)
        single_data = res_single.json()
        self.assertEqual(single_data["train_id"], train_id)
        self.assertIn("brake_pad_wear_pct", single_data["telemetry"])

        # GET /api/v1/trains/{train_id} (Alias path)
        res_alias = self.client.get(f"/api/trains/{train_id}")
        self.assertEqual(res_alias.status_code, 200)

        # GET /api/v1/trains/{train_id} (Invalid train ID)
        res_invalid = self.client.get("/api/v1/trains/KM-999")
        self.assertEqual(res_invalid.status_code, 404)
        self.assertIn("not found", res_invalid.json()["detail"].lower())

    def test_09_iot_telemetry_and_events(self):
        # 1. Normal telemetry payload -> Accepted without alerts
        normal_payload = {
            "train_id": "KM-101",
            "vibration": 0.08,
            "traction_motor_temp_c": 62.0,
            "brake_pad_wear_pct": 35.0,
            "door_cycles": 12000,
            "hvac_pressure_psi": 58.0,
            "mileage_km": 45000.0,
            "location_id": 2
        }
        res_norm = self.client.post("/api/v1/iot/telemetry", json=normal_payload)
        self.assertEqual(res_norm.status_code, 200)
        norm_data = res_norm.json()
        self.assertEqual(norm_data["status"], "accepted")
        self.assertEqual(norm_data["train_id"], "KM-101")
        self.assertEqual(len(norm_data["anomalies"]), 0)

        # 2. Unknown train ID -> 404 Not Found
        bad_train_payload = dict(normal_payload, train_id="KM-999")
        res_bad_train = self.client.post("/api/v1/iot/telemetry", json=bad_train_payload)
        self.assertEqual(res_bad_train.status_code, 404)

        # 3. Invalid telemetry values -> 422 Unprocessable Entity (Validation error)
        invalid_val_payload = dict(normal_payload, vibration=-1.0)
        res_invalid = self.client.post("/api/v1/iot/telemetry", json=invalid_val_payload)
        self.assertEqual(res_invalid.status_code, 422)

        # 4. Anomaly payload: High vibration & high motor temperature
        anomaly_payload = {
            "train_id": "KM-101",
            "vibration": 0.45,  # Threshold > 0.25
            "traction_motor_temp_c": 105.0,  # Threshold >= 95.0
            "brake_pad_wear_pct": 40.0
        }
        res_anom = self.client.post("/api/v1/iot/telemetry", json=anomaly_payload)
        self.assertEqual(res_anom.status_code, 200)
        anom_data = res_anom.json()
        self.assertEqual(anom_data["status"], "accepted_with_alert")
        self.assertEqual(len(anom_data["anomalies"]), 2)
        anomaly_types = [a["type"] for a in anom_data["anomalies"]]
        self.assertIn("HIGH_VIBRATION", anomaly_types)
        self.assertIn("HIGH_TRACTION_TEMPERATURE", anomaly_types)
        self.assertGreaterEqual(len(anom_data["event_ids"]), 1)

        # 5. Deduplication check: Sending identical payload immediately should not create duplicate events
        res_anom_dup = self.client.post("/api/v1/iot/telemetry", json=anomaly_payload)
        self.assertEqual(res_anom_dup.status_code, 200)
        dup_data = res_anom_dup.json()
        self.assertEqual(len(dup_data["event_ids"]), 0)  # Deduplicated

        # 6. Retrieve telemetry history
        res_hist = self.client.get("/api/v1/iot/KM-101/telemetry?limit=10")
        self.assertEqual(res_hist.status_code, 200)
        hist_data = res_hist.json()
        self.assertEqual(hist_data["train_id"], "KM-101")
        self.assertGreaterEqual(hist_data["record_count"], 3)

        # 7. Retrieve events
        res_events = self.client.get("/api/v1/events?train_id=KM-101")
        self.assertEqual(res_events.status_code, 200)
        events_data = res_events.json()
        self.assertGreaterEqual(events_data["total_events"], 2)

        # Retrieve specific event by ID
        event_id = events_data["events"][0]["event_id"]
        res_single_evt = self.client.get(f"/api/v1/events/{event_id}")
        self.assertEqual(res_single_evt.status_code, 200)
        self.assertEqual(res_single_evt.json()["event_id"], event_id)

        # Retrieve events via train sub-resource
        res_train_evts = self.client.get("/api/v1/trains/KM-101/events")
        self.assertEqual(res_train_evts.status_code, 200)

        # 8. Verify TRAIN API reflects updated IoT telemetry overlay
        res_train = self.client.get("/api/v1/trains/KM-101")
        self.assertEqual(res_train.status_code, 200)
        train_obj = res_train.json()
        self.assertEqual(train_obj["telemetry"]["traction_motor_temp_c"], 105.0)

    def test_10_locations_and_depots_api(self):
        # 1. GET /api/v1/depots
        res_depots = self.client.get("/api/v1/depots")
        self.assertEqual(res_depots.status_code, 200)
        depots_data = res_depots.json()
        self.assertEqual(depots_data["total_depots"], 2)
        depot_names = [d["name"] for d in depots_data["depots"]]
        self.assertTrue(any("Muttom" in n for n in depot_names))

        # 2. GET /api/v1/locations
        res_locs = self.client.get("/api/v1/locations")
        self.assertEqual(res_locs.status_code, 200)
        locs_data = res_locs.json()
        self.assertGreaterEqual(locs_data["total_locations"], 36)

        # 3. GET /api/v1/locations/1 (Aluva Station)
        res_loc_single = self.client.get("/api/v1/locations/1")
        self.assertEqual(res_loc_single.status_code, 200)
        loc_obj = res_loc_single.json()
        self.assertEqual(loc_obj["location_id"], 1)
        self.assertIn("Aluva", loc_obj["name"])

        # 4. GET /api/v1/locations/999 (Invalid Location -> 404)
        res_loc_bad = self.client.get("/api/v1/locations/999")
        self.assertEqual(res_loc_bad.status_code, 404)

        # 5. GET /api/v1/locations/5/connections (Muttom Station connections)
        res_conn = self.client.get("/api/v1/locations/5/connections")
        self.assertEqual(res_conn.status_code, 200)
        conn_data = res_conn.json()
        self.assertEqual(conn_data["location_id"], 5)
        self.assertGreaterEqual(conn_data["total_connections"], 2)
        first_conn = conn_data["connections"][0]
        self.assertIn("distance_meters", first_conn)
        self.assertIn("movement_time_minutes", first_conn)
        self.assertIn("movement_cost", first_conn)

        # 6. GET /api/v1/trains/KM-101/location
        res_tloc = self.client.get("/api/v1/trains/KM-101/location")
        self.assertEqual(res_tloc.status_code, 200)
        tloc_data = res_tloc.json()
        self.assertEqual(tloc_data["train_id"], "KM-101")
        self.assertIn("location_id", tloc_data)

        # 7. Telemetry validation: invalid location_id -> 422
        bad_loc_payload = {
            "train_id": "KM-101",
            "location_id": 999
        }
        res_bad_loc = self.client.post("/api/v1/iot/telemetry", json=bad_loc_payload)
        self.assertEqual(res_bad_loc.status_code, 422)

        # 8. Telemetry update: valid location_id -> 200 and location updated
        good_loc_payload = {
            "train_id": "KM-101",
            "location_id": 1
        }
        res_good_loc = self.client.post("/api/v1/iot/telemetry", json=good_loc_payload)
        self.assertEqual(res_good_loc.status_code, 200)
        
        res_tloc_updated = self.client.get("/api/v1/trains/KM-101/location")
        self.assertEqual(res_tloc_updated.json()["location_id"], 1)

    def test_11_fitness_certificates_api(self):
        # 1. Valid certificate query (KM-101)
        res_valid = self.client.get("/api/v1/trains/KM-101/fitness")
        self.assertEqual(res_valid.status_code, 200)
        valid_data = res_valid.json()
        self.assertTrue(valid_data["is_fit_for_service"])
        self.assertEqual(valid_data["overall_fitness_status"], "FIT_FOR_SERVICE")
        self.assertEqual(len(valid_data["department_certificates"]), 3)

        # Department specific valid query
        res_dept = self.client.get("/api/v1/trains/KM-101/fitness/Signalling")
        self.assertEqual(res_dept.status_code, 200)
        dept_data = res_dept.json()
        self.assertEqual(dept_data["department"], "Signalling")
        self.assertTrue(dept_data["is_valid_now"])
        self.assertEqual(dept_data["status"], "APPROVED")

        # 2. Expired certificate query (KM-104 has expired Signalling cert)
        res_exp = self.client.get("/api/v1/trains/KM-104/fitness")
        self.assertEqual(res_exp.status_code, 200)
        exp_data = res_exp.json()
        self.assertFalse(exp_data["is_fit_for_service"])
        self.assertEqual(exp_data["overall_fitness_status"], "UNFIT_SAFETY_CERTIFICATE_EXPIRED")
        
        res_exp_dept = self.client.get("/api/v1/trains/KM-104/fitness/Signalling")
        self.assertEqual(res_exp_dept.status_code, 200)
        self.assertFalse(res_exp_dept.json()["is_valid_now"])
        self.assertEqual(res_exp_dept.json()["status"], "EXPIRED")

        # 3. Invalid train ID query (KM-999 -> 404)
        res_bad_train = self.client.get("/api/v1/trains/KM-999/fitness")
        self.assertEqual(res_bad_train.status_code, 404)

        # 4. Certificate approaching expiry query (KM-105 Rolling Stock expires in 3 days)
        res_appr = self.client.get("/api/v1/trains/KM-105/fitness")
        self.assertEqual(res_appr.status_code, 200)
        appr_data = res_appr.json()
        self.assertTrue(appr_data["has_approaching_expiry"])
        
        res_appr_dept = self.client.get("/api/v1/trains/KM-105/fitness/Rolling Stock")
        self.assertEqual(res_appr_dept.status_code, 200)
        self.assertTrue(res_appr_dept.json()["approaching_expiry"])
        self.assertLessEqual(res_appr_dept.json()["days_until_expiry"], 7.0)

        # 5. Issue/Update certificate (Renew KM-104 Signalling cert)
        update_payload = {
            "department": "Signalling",
            "status": "APPROVED",
            "days_valid": 90,
            "source": "KMRL_SAFETY_BOARD"
        }
        res_renew = self.client.post("/api/v1/trains/KM-104/fitness", json=update_payload)
        self.assertEqual(res_renew.status_code, 200)
        self.assertTrue(res_renew.json()["is_valid_now"])

        # Re-query KM-104 fitness summary to verify it is now FIT_FOR_SERVICE
        res_recheck = self.client.get("/api/v1/trains/KM-104/fitness")
        self.assertTrue(res_recheck.json()["is_fit_for_service"])
        self.assertEqual(res_recheck.json()["overall_fitness_status"], "FIT_FOR_SERVICE")

if __name__ == "__main__":
    unittest.main()




