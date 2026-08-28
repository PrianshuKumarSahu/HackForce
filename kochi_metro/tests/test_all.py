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

    def test_12_job_cards_api(self):
        # -----------------------------------------------------------------------
        # Test Case 1: Open CRITICAL job card (KM-101)
        # -----------------------------------------------------------------------
        res = self.client.get("/api/v1/trains/KM-101/job-cards")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["train_id"], "KM-101")
        self.assertGreaterEqual(data["total_jobs"], 1)
        self.assertGreaterEqual(data["open_critical_jobs_count"], 1)

        # Verify the critical preset job is present
        jobs = data["job_cards"]
        critical_jobs = [j for j in jobs if j["is_critical"]]
        self.assertGreaterEqual(len(critical_jobs), 1)
        crit = critical_jobs[0]
        self.assertIn(crit["status"], ["OPEN", "IN_PROGRESS"])
        self.assertIn(crit["priority"], ["CRITICAL", "HIGH"])
        self.assertTrue(crit["is_critical"])
        self.assertIn("job_id", crit)
        self.assertIn("job_number", crit)
        self.assertIn("due_date", crit)
        self.assertIn("estimated_duration_hours", crit)
        self.assertIn("source", crit)

        # Retrieve that job by ID
        job_id = crit["job_id"]
        res_single = self.client.get(f"/api/v1/job-cards/{job_id}")
        self.assertEqual(res_single.status_code, 200)
        self.assertEqual(res_single.json()["job_id"], job_id)
        self.assertTrue(res_single.json()["is_critical"])

        # is_critical filter
        res_crit_filter = self.client.get("/api/v1/trains/KM-101/job-cards?is_critical=true")
        self.assertEqual(res_crit_filter.status_code, 200)
        for j in res_crit_filter.json()["job_cards"]:
            self.assertTrue(j["is_critical"])

        # -----------------------------------------------------------------------
        # Test Case 2: Closed / completed job card (KM-102)
        # -----------------------------------------------------------------------
        res_closed = self.client.get("/api/v1/trains/KM-102/job-cards?status=COMPLETED")
        self.assertEqual(res_closed.status_code, 200)
        closed_data = res_closed.json()
        self.assertGreaterEqual(closed_data["total_jobs"], 1)
        for j in closed_data["job_cards"]:
            self.assertEqual(j["status"], "COMPLETED")
            self.assertFalse(j["is_critical"])  # Closed jobs are never critical

        # -----------------------------------------------------------------------
        # Test Case 3: Overdue job card (KM-103 - due 2 days ago, still OPEN)
        # -----------------------------------------------------------------------
        res_overdue = self.client.get("/api/v1/trains/KM-103/job-cards")
        self.assertEqual(res_overdue.status_code, 200)
        overdue_jobs = [j for j in res_overdue.json()["job_cards"] if j["is_overdue"]]
        self.assertGreaterEqual(len(overdue_jobs), 1)
        overdue = overdue_jobs[0]
        self.assertIn(overdue["status"], ["OPEN", "IN_PROGRESS"])
        self.assertTrue(overdue["is_overdue"])

        # -----------------------------------------------------------------------
        # Test Case 4: Invalid train ID -> 404
        # -----------------------------------------------------------------------
        res_bad_train = self.client.get("/api/v1/trains/KM-999/job-cards")
        self.assertEqual(res_bad_train.status_code, 404)
        self.assertIn("not found", res_bad_train.json()["detail"].lower())

        # -----------------------------------------------------------------------
        # Test Case 5: Invalid job ID -> 404
        # -----------------------------------------------------------------------
        res_bad_job = self.client.get("/api/v1/job-cards/JC-INVALID-9999")
        self.assertEqual(res_bad_job.status_code, 404)
        self.assertIn("not found", res_bad_job.json()["detail"].lower())

        # -----------------------------------------------------------------------
        # POST: Create a new CRITICAL emergency job card
        # -----------------------------------------------------------------------
        create_payload = {
            "train_id": "KM-110",
            "description": "Pantograph arm fracture - emergency replacement required",
            "category": "EMERGENCY_REPAIR",
            "priority": "CRITICAL",
            "estimated_duration_hours": 6.0,
            "source": "MAXIMO_CMMS"
        }
        res_create = self.client.post("/api/v1/job-cards", json=create_payload)
        self.assertEqual(res_create.status_code, 201)
        new_job = res_create.json()
        self.assertEqual(new_job["train_id"], "KM-110")
        self.assertEqual(new_job["status"], "OPEN")
        self.assertEqual(new_job["priority"], "CRITICAL")
        self.assertEqual(new_job["category"], "EMERGENCY_REPAIR")
        self.assertTrue(new_job["is_critical"])
        self.assertFalse(new_job["is_overdue"])
        new_job_id = new_job["job_id"]

        # Verify it now appears in KM-110's job list
        res_km110 = self.client.get("/api/v1/trains/KM-110/job-cards")
        job_ids = [j["job_id"] for j in res_km110.json()["job_cards"]]
        self.assertIn(new_job_id, job_ids)

        # -----------------------------------------------------------------------
        # PATCH: Update job card status to IN_PROGRESS, then COMPLETED
        # -----------------------------------------------------------------------
        res_patch = self.client.patch(f"/api/v1/job-cards/{new_job_id}", json={"status": "IN_PROGRESS"})
        self.assertEqual(res_patch.status_code, 200)
        self.assertEqual(res_patch.json()["status"], "IN_PROGRESS")
        self.assertTrue(res_patch.json()["is_critical"])  # Still critical while in-progress

        res_complete = self.client.patch(f"/api/v1/job-cards/{new_job_id}", json={"status": "COMPLETED"})
        self.assertEqual(res_complete.status_code, 200)
        self.assertEqual(res_complete.json()["status"], "COMPLETED")
        self.assertFalse(res_complete.json()["is_critical"])  # No longer critical when closed

        # -----------------------------------------------------------------------
        # POST: Invalid train ID -> 404
        # -----------------------------------------------------------------------
        res_bad_create = self.client.post("/api/v1/job-cards", json={
            "train_id": "KM-999",
            "description": "Bogus job for invalid train"
        })
        self.assertEqual(res_bad_create.status_code, 404)

        # -----------------------------------------------------------------------
        # POST: Invalid category enum -> 422
        # -----------------------------------------------------------------------
        res_bad_cat = self.client.post("/api/v1/job-cards", json={
            "train_id": "KM-101",
            "description": "Test job",
            "category": "INVALID_CATEGORY"
        })
        self.assertEqual(res_bad_cat.status_code, 422)

        # -----------------------------------------------------------------------
        # PATCH: Invalid job_id -> 404
        # -----------------------------------------------------------------------
        res_bad_patch = self.client.patch("/api/v1/job-cards/JC-NONEXISTENT", json={"status": "COMPLETED"})
        self.assertEqual(res_bad_patch.status_code, 404)

        # -----------------------------------------------------------------------
        # Train fleet API: open_critical_jobs_count present and correct for KM-101
        # -----------------------------------------------------------------------
        res_fleet = self.client.get("/api/v1/trains/KM-101")
        self.assertEqual(res_fleet.status_code, 200)
        fleet_train = res_fleet.json()
        self.assertIn("open_critical_jobs_count", fleet_train)
        self.assertGreaterEqual(fleet_train["open_critical_jobs_count"], 1)


if __name__ == "__main__":
    unittest.main()




