/**
 * Kochi Metro FastAPI ML & Optimization Service Client
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface ApiTrainDetail {
  train_id: string;
  train_type: string;
  current_location_id: number;
  current_location_name: string;
  is_fit_for_service: boolean;
  overall_fitness_status: string;
  health_score: number;
  next_day_failure_prob: number;
  consequence_score: number;
  subsystem_risks: {
    brakes: number;
    doors: number;
    hvac: number;
    traction: number;
  };
  primary_risk_subsystem: string;
  maintenance_urgency: string;
  telemetry: {
    brake_pad_wear_pct: number;
    door_cycles: number;
    hvac_pressure_psi: number;
    traction_motor_temp_c: number;
    mileage_km: number;
    days_since_ibl: number;
    past_30d_delays: number;
    past_30d_faults: number;
  };
}

export interface ChartEvaluationResponse {
  chart_id: string;
  expected_chart_efficiency_pct: number;
  failure_probability_pct: number;
  expected_delay_minutes: number;
  reserve_adequacy: 'HIGH' | 'MEDIUM' | 'LOW';
  confidence_score_pct: number;
  top_recommended_trains: string[];
  standby_trains: string[];
  reasons_and_evidence: string[];
}

export interface WhatIfSimulationResponse {
  scenario: string;
  cascade_disruption_impact: 'LOW' | 'MODERATE' | 'CRITICAL';
  revised_efficiency_score_pct: number;
  revised_expected_delay_mins: number;
  revised_reserve_adequacy: 'HIGH' | 'MEDIUM' | 'LOW';
  revised_chart: ChartEvaluationResponse;
}

export interface StationCrowdingResponse {
  peak_hour: boolean;
  day_type: string;
  max_onboard_passengers: number;
  peak_crowding_pct: number;
  bottleneck_stations: string[];
  station_profiles: Array<{
    station_name: string;
    predicted_boarding: number;
    predicted_alighting: number;
    onboard_passengers: number;
    crowding_pct: number;
    crowding_status: string;
  }>;
  proactive_passenger_alerts: Array<{
    station_name: string;
    severity: string;
    message: string;
  }>;
}

/**
 * Checks if the FastAPI backend server is alive and reachable.
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch('http://localhost:8000/', { method: 'GET' });
    return res.ok;
  } catch (err) {
    return false;
  }
}

/**
 * Fetches all fleet trains with ML health predictions and safety fitness certs.
 */
export async function fetchLiveFleetTrains(): Promise<ApiTrainDetail[] | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/trains`);
    if (!res.ok) throw new Error('API server returned error');
    const data = await res.json();
    return data.trains;
  } catch (err) {
    console.warn('Backend API unreachable, using mock data fallback:', err);
    return null;
  }
}

/**
 * Solves CP-SAT resilience optimization for induction chart.
 */
export async function runCpsatOptimization(
  dayType: string = 'WEEKDAY',
  requiredActive: number = 18,
  requiredStandby: number = 3
) {
  try {
    const res = await fetch(`${API_BASE_URL}/chart/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        day_type: dayType,
        required_active: requiredActive,
        required_standby: requiredStandby,
      }),
    });
    if (!res.ok) throw new Error('Optimization failed');
    return await res.json();
  } catch (err) {
    console.warn('API Optimization failed, falling back:', err);
    return null;
  }
}

/**
 * Evaluates candidate chart efficiency % and delay metrics.
 */
export async function evaluateChartEfficiency(dayType: string = 'WEEKDAY'): Promise<ChartEvaluationResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/chart/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ day_type: dayType }),
    });
    if (!res.ok) throw new Error('Chart evaluation failed');
    return await res.json();
  } catch (err) {
    console.warn('API Chart Evaluation failed:', err);
    return null;
  }
}

/**
 * Runs What-If disruption simulation.
 */
export async function runWhatIfSimulation(
  failedTrainIds: string[],
  demandIncreasePct: number = 0.0,
  dayType: string = 'WEEKDAY'
): Promise<WhatIfSimulationResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/simulate/whatif`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        failed_train_ids: failedTrainIds,
        demand_increase_pct: demandIncreasePct,
        day_type: dayType,
      }),
    });
    if (!res.ok) throw new Error('Simulation failed');
    return await res.json();
  } catch (err) {
    console.warn('API What-If Simulation failed:', err);
    return null;
  }
}

/**
 * Fetches station passenger crowding & proactive deboarding advice.
 */
export async function fetchStationCrowding(isPeakHour: boolean = true): Promise<StationCrowdingResponse | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/demand/crowding?is_peak_hour=${isPeakHour}`);
    if (!res.ok) throw new Error('Station crowding API failed');
    return await res.json();
  } catch (err) {
    console.warn('Station crowding fetch failed:', err);
    return null;
  }
}
