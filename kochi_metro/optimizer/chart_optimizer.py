import numpy as np
from typing import Dict, List, Any

try:
    from ortools.sat.python import cp_model
    HAS_OR_TOOLS = True
except ImportError:
    HAS_OR_TOOLS = False

class ResilienceChartOptimizer:
    """
    CP-SAT Resilience & Consequence-Aware Schedule Optimizer.
    Optimizes induction chart into Active Scheduled, Standby Reserve, and Depot Maintenance.
    """
    def __init__(self, required_active: int = 18, required_standby: int = 3):
        self.required_active = required_active
        self.required_standby = required_standby

    def optimize_induction_chart(self, fleet_predictions: List[Dict[str, Any]], day_type: str = "WEEKDAY") -> Dict[str, Any]:
        """
        Formulates and solves the constraint optimization problem.
        Minimizes total disruption cost = sum(Failure_Risk * Consequence_Factor).
        """
        if day_type == "WEEKEND":
            active_needed = 14
            standby_needed = 2
        elif day_type == "EVENT":
            active_needed = 20
            standby_needed = 4
        else:
            active_needed = self.required_active
            standby_needed = self.required_standby

        num_trains = len(fleet_predictions)

        if HAS_OR_TOOLS:
            model = cp_model.CpModel()

            # Variables: x[i] = 0 (Active), 1 (Standby), 2 (Maintenance)
            x = {}
            for i, p in enumerate(fleet_predictions):
                x[i] = model.NewIntVar(0, 2, f"train_{p['train_id']}")

            # Category boolean indicators
            active_bool = {}
            standby_bool = {}
            maint_bool = {}

            for i in range(num_trains):
                active_bool[i] = model.NewBoolVar(f"active_{i}")
                standby_bool[i] = model.NewBoolVar(f"standby_{i}")
                maint_bool[i] = model.NewBoolVar(f"maint_{i}")

                model.Add(x[i] == 0).OnlyEnforceIf(active_bool[i])
                model.Add(x[i] != 0).OnlyEnforceIf(active_bool[i].Not())

                model.Add(x[i] == 1).OnlyEnforceIf(standby_bool[i])
                model.Add(x[i] != 1).OnlyEnforceIf(standby_bool[i].Not())

                model.Add(x[i] == 2).OnlyEnforceIf(maint_bool[i])
                model.Add(x[i] != 2).OnlyEnforceIf(maint_bool[i].Not())

            # Constraint 1: Exact active fleet requirement
            model.Add(sum(active_bool[i] for i in range(num_trains)) == active_needed)

            # Constraint 2: Exact standby fleet requirement
            model.Add(sum(standby_bool[i] for i in range(num_trains)) == standby_needed)

            # Objective: Minimize total risk cost of active fleet
            # Maintenance assignment incurs 0 active risk cost, active incurs full consequence cost
            cost_terms = []
            for i, p in enumerate(fleet_predictions):
                fail_cost = int(p["consequence_score"] * 100) + int(p["next_day_failure_prob"] * 1000)
                # Active trains incur full failure & consequence cost, standby incurs 20%, maintenance incurs 0%
                cost_terms.append(fail_cost * active_bool[i] + int(fail_cost * 0.2) * standby_bool[i])

            model.Minimize(sum(cost_terms))

            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 5.0
            status = solver.Solve(model)

            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                active_list = []
                standby_list = []
                maint_list = []
                for i, p in enumerate(fleet_predictions):
                    val = solver.Value(x[i])
                    if val == 0:
                        active_list.append(p)
                    elif val == 1:
                        standby_list.append(p)
                    else:
                        maint_list.append(p)

                return {
                    "status": "OPTIMAL_FEASIBLE",
                    "day_type": day_type,
                    "active_scheduled": active_list,
                    "standby_reserve": standby_list,
                    "depot_maintenance": maint_list,
                    "active_count": len(active_list),
                    "standby_count": len(standby_list),
                    "maintenance_count": len(maint_list)
                }

        # Fallback Heuristic Solver if OR-Tools CP-SAT is unavailable or infeasible
        sorted_fleet = sorted(fleet_predictions, key=lambda p: p["consequence_score"])
        active_list = sorted_fleet[:active_needed]
        standby_list = sorted_fleet[active_needed:active_needed + standby_needed]
        maint_list = sorted_fleet[active_needed + standby_needed:]

        return {
            "status": "HEURISTIC_FEASIBLE",
            "day_type": day_type,
            "active_scheduled": active_list,
            "standby_reserve": standby_list,
            "depot_maintenance": maint_list,
            "active_count": len(active_list),
            "standby_count": len(standby_list),
            "maintenance_count": len(maint_list)
        }

if __name__ == "__main__":
    from kochi_metro.data.generator import KochiMetroDataGenerator
    from kochi_metro.ml.health_predictor import TrainHealthPredictor

    gen = KochiMetroDataGenerator()
    fleet_df = gen.generate_current_fleet_status()
    predictor = TrainHealthPredictor()
    predictions = predictor.predict_fleet_health(fleet_df)

    optimizer = ResilienceChartOptimizer()
    chart = optimizer.optimize_induction_chart(predictions)
    print("Optimization Result Status:", chart["status"])
    print(f"Active: {chart['active_count']}, Standby: {chart['standby_count']}, Maint: {chart['maintenance_count']}")
