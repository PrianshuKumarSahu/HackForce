export type InductionRole = 'REVENUE_SERVICE' | 'HOT_STANDBY' | 'IBL_MAINTENANCE' | 'CLEANING_BAY';

export interface DepartmentFitnessCert {
  department: 'Rolling-Stock' | 'Signalling' | 'Telecom';
  status: 'VALID' | 'EXPIRING_SOON' | 'EXPIRED' | 'REVOKED';
  validUntil: string;
  issuedBy: string;
  notes?: string;
}

export interface MaximoJobCard {
  id: string;
  workOrderNumber: string;
  title: string;
  subsystem: 'Brakes' | 'HVAC' | 'Traction' | 'Doors' | 'Pantograph' | 'Bogie' | 'TCMS';
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'OPEN' | 'IN_PROGRESS' | 'CLOSED' | 'DEFERRED';
  technicianAssigned: string;
  estimatedFixHours: number;
}

export interface BrandingContract {
  advertiser: string;
  campaignTitle: string;
  tier: 'PLATINUM' | 'GOLD' | 'SILVER';
  targetExposureHours: number;
  currentExposureHours: number;
  penaltyRatePerHour: number; // in INR
  priorityScore: number; // 1-10
}

export interface ComponentWearMetrics {
  bogieWearPct: number;
  brakePadWearPct: number;
  hvacHealthScore: number; // 0 - 100
  doorCycleCount: number;
  pantographWearPct: number;
}

export interface CleaningStatus {
  lastCleanedDate: string;
  deepCleaningRequired: boolean;
  assignedBay: string;
  manpowerAllocated: number;
  cleaningSlot: 'NIGHT_SHIFT_A' | 'NIGHT_SHIFT_B' | 'COMPLETED';
}

export interface StablingPosition {
  trackLine: string; // e.g., "ST-04", "IBL-02", "WASH-01"
  positionDepth: number; // 1 = First out, 2 = Second out, 3 = Trapped behind
  shuntingTurnsNeeded: number; // estimated moves required to exit
  turnoutTimeMins: number;
  isObstructed: boolean;
}

export interface ExplainableReasoning {
  positiveFactors: string[];
  riskFactors: string[];
  penaltyAvertedINR: number;
  confidenceScorePct: number;
}

export interface Trainset {
  id: string;
  rakeNumber: string; // e.g. "KM-101"
  trainCarCount: number; // 4-car
  fitnessCertificates: {
    rollingStock: DepartmentFitnessCert;
    signalling: DepartmentFitnessCert;
    telecom: DepartmentFitnessCert;
  };
  jobCards: MaximoJobCard[];
  branding: BrandingContract | null;
  currentMileageKm: number;
  targetDailyMileageKm: number;
  componentWear: ComponentWearMetrics;
  cleaning: CleaningStatus;
  stabling: StablingPosition;
  
  // AI Optimization outputs
  overallReadinessScore: number; // 0 - 100
  assignedRole: InductionRole;
  rank: number;
  reasoning: ExplainableReasoning;
  isOverridden: boolean;
  overrideJustification?: string;
  supervisorName?: string;
}

export interface OptimizationWeights {
  punctualityWeight: number; // Hard constraint enforcement
  brandingWeight: number;    // Advertiser SLA compliance
  mileageBalanceWeight: number; // Wear equalization
  shuntingMinimizationWeight: number; // Stabling turn-out time
  cleaningAdherenceWeight: number; // Deep cleaning slots
}

export interface SimulationScenario {
  id: string;
  name: string;
  description: string;
  affectedTrain: string;
  disruptionType: 'TELECOM_FAILURE' | 'MAXIMO_BRAKE_EMERGENCY' | 'RAIN_SURGE_DEMAND' | 'BRANDING_BREACH_ALERT' | 'TRACK_SHUNTING_BLOCK';
  impactSeverity: 'HIGH' | 'MEDIUM' | 'LOW';
  recommendedAction: string;
}
