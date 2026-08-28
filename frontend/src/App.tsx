import React, { useState, useEffect } from 'react';
import { INITIAL_TRAINSETS, INITIAL_OPTIMIZATION_WEIGHTS } from './data/mockData';
import { Trainset, OptimizationWeights, InductionRole, SimulationScenario } from './types';
import { Header } from './components/Header';
import { InductionBoardView } from './components/InductionBoardView';
import { VariableMatrixView } from './components/VariableMatrixView';
import { OptimizerControlView } from './components/OptimizerControlView';
import { DepotYardMap } from './components/DepotYardMap';
import { WhatIfSimulator } from './components/WhatIfSimulator';
import { DataIngestionView } from './components/DataIngestionView';
import { AnalyticsView } from './components/AnalyticsView';
import { SupervisorOverrideModal } from './components/SupervisorOverrideModal';
import { ExportReportModal } from './components/ExportReportModal';
import {
  checkBackendHealth,
  fetchLiveFleetTrains,
  runCpsatOptimization,
  runWhatIfSimulation,
  ApiTrainDetail,
} from './api';

export const App: React.FC = () => {
  const [trainsets, setTrainsets] = useState<Trainset[]>(INITIAL_TRAINSETS);
  const [weights, setWeights] = useState<OptimizationWeights>(INITIAL_OPTIMIZATION_WEIGHTS);
  const [activeTab, setActiveTab] = useState<string>('board');
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [selectedTrainForOverride, setSelectedTrainForOverride] = useState<Trainset | null>(null);
  const [isExportModalOpen, setIsExportModalOpen] = useState<boolean>(false);
  const [isApiConnected, setIsApiConnected] = useState<boolean>(false);

  // Load live ML predictions from FastAPI backend on mount
  useEffect(() => {
    async function initBackendConnection() {
      const isConnected = await checkBackendHealth();
      setIsApiConnected(isConnected);

      if (isConnected) {
        const liveTrains = await fetchLiveFleetTrains();
        if (liveTrains && liveTrains.length > 0) {
          setTrainsets((prev) => mapApiTrainsToTrainsets(liveTrains, prev));
        }
      }
    }
    initBackendConnection();
  }, []);

  // Maps live FastAPI predictions onto frontend Trainset structure
  const mapApiTrainsToTrainsets = (apiTrains: ApiTrainDetail[], existing: Trainset[]): Trainset[] => {
    const existingMap = new Map(existing.map((t) => [t.rakeNumber.toUpperCase(), t]));

    return apiTrains.map((apiT, idx) => {
      const rake = apiT.train_id.toUpperCase();
      const prev = existingMap.get(rake);

      let assignedRole: InductionRole = 'REVENUE_SERVICE';
      if (apiT.maintenance_urgency === 'HIGH' || !apiT.is_fit_for_service) {
        assignedRole = 'IBL_MAINTENANCE';
      } else if (idx >= 18 && idx < 21) {
        assignedRole = 'HOT_STANDBY';
      } else if (idx >= 21) {
        assignedRole = 'CLEANING_BAY';
      }

      return {
        id: apiT.train_id.toLowerCase(),
        rakeNumber: apiT.train_id,
        trainCarCount: 3,
        fitnessCertificates: prev
          ? prev.fitnessCertificates
          : {
              rollingStock: {
                department: 'Rolling-Stock',
                status: apiT.is_fit_for_service ? 'VALID' : 'EXPIRED',
                validUntil: '2026-09-15 23:59',
                issuedBy: 'Eng. Rajesh Nair',
              },
              signalling: {
                department: 'Signalling',
                status: apiT.is_fit_for_service ? 'VALID' : 'EXPIRED',
                validUntil: '2026-09-15 23:59',
                issuedBy: 'Eng. Sunitha Varma',
              },
              telecom: {
                department: 'Telecom',
                status: apiT.is_fit_for_service ? 'VALID' : 'EXPIRED',
                validUntil: '2026-09-15 23:59',
                issuedBy: 'Eng. George Mathew',
              },
            },
        jobCards: prev ? prev.jobCards : [],
        branding: prev ? prev.branding : null,
        currentMileageKm: apiT.telemetry.mileage_km,
        targetDailyMileageKm: 340,
        componentWear: {
          bogieWearPct: Math.round(apiT.subsystem_risks.traction * 100),
          brakePadWearPct: Math.round(apiT.telemetry.brake_pad_wear_pct),
          hvacHealthScore: Math.round(100 - apiT.subsystem_risks.hvac * 100),
          doorCycleCount: apiT.telemetry.door_cycles,
          pantographWearPct: Math.round(apiT.subsystem_risks.doors * 50),
        },
        cleaning: prev
          ? prev.cleaning
          : {
              lastCleanedDate: '2026-08-28',
              deepCleaningRequired: false,
              assignedBay: 'BAY-A',
              manpowerAllocated: 4,
              cleaningSlot: 'COMPLETED',
            },
        stabling: prev
          ? prev.stabling
          : {
              trackLine: `ST-0${(idx % 6) + 1}`,
              positionDepth: (idx % 3) + 1,
              shuntingTurnsNeeded: idx % 2,
              turnoutTimeMins: 2.5 + idx * 0.5,
              isObstructed: false,
            },
        overallReadinessScore: apiT.health_score,
        assignedRole: assignedRole,
        rank: idx + 1,
        reasoning: {
          positiveFactors: [
            `ML Health Score: ${apiT.health_score}%`,
            `Predicted Next-Day Failure Risk: ${(apiT.next_day_failure_prob * 100).toFixed(1)}%`,
            `Subsystem Primary Risk: ${apiT.primary_risk_subsystem.toUpperCase()}`,
          ],
          riskFactors:
            apiT.next_day_failure_prob > 0.2
              ? [`Elevated failure risk detected in ${apiT.primary_risk_subsystem}`]
              : [],
          penaltyAvertedINR: 45000,
          confidenceScorePct: Math.round(98 - apiT.next_day_failure_prob * 20),
        },
        isOverridden: false,
      };
    });
  };

  // Run CP-SAT Optimization via FastAPI Engine
  const handleRunOptimization = async () => {
    setIsOptimizing(true);

    const optResult = await runCpsatOptimization('WEEKDAY', 18, 3);

    if (optResult && optResult.active_scheduled) {
      const activeIds = new Set(optResult.active_scheduled.map((t: any) => t.train_id));
      const standbyIds = new Set(optResult.standby_reserve.map((t: any) => t.train_id));
      const maintIds = new Set(optResult.depot_maintenance.map((t: any) => t.train_id));

      const updated = trainsets.map((t) => {
        let role: InductionRole = 'REVENUE_SERVICE';
        if (maintIds.has(t.rakeNumber)) role = 'IBL_MAINTENANCE';
        else if (standbyIds.has(t.rakeNumber)) role = 'HOT_STANDBY';
        else if (activeIds.has(t.rakeNumber)) role = 'REVENUE_SERVICE';
        return {
          ...t,
          assignedRole: role,
        };
      });
      setTrainsets(updated);
    } else {
      // Re-calculate scores locally if offline
      const updated = trainsets.map((t, idx) => {
        let score = 95 - idx * 2.8;
        if (
          t.fitnessCertificates.rollingStock.status !== 'VALID' ||
          t.fitnessCertificates.signalling.status !== 'VALID'
        ) {
          score = 22.0;
        } else if (t.branding && t.branding.tier === 'PLATINUM') {
          score += 4.5;
        }
        return {
          ...t,
          overallReadinessScore: Math.min(100, Math.max(15, Math.round(score * 10) / 10)),
        };
      });
      setTrainsets(updated);
    }

    setIsOptimizing(false);
  };

  // Supervisor Manual Override handler
  const handleSaveOverride = (
    trainId: string,
    newRole: InductionRole,
    justification: string,
    supervisorName: string
  ) => {
    const updated = trainsets.map((t) => {
      if (t.id === trainId || t.rakeNumber === trainId) {
        return {
          ...t,
          assignedRole: newRole,
          isOverridden: true,
          overrideJustification: justification,
          supervisorName: supervisorName,
        };
      }
      return t;
    });
    setTrainsets(updated);
  };

  // What-If Scenario injection handler via ML backend API
  const handleApplyScenario = async (scenario: SimulationScenario) => {
    if (scenario.id === 'sc-1') {
      const simRes = await runWhatIfSimulation(['KM-101'], 20.0);

      const updated = trainsets.map((t) => {
        if (t.rakeNumber === 'KM-101') {
          return {
            ...t,
            assignedRole: 'IBL_MAINTENANCE' as InductionRole,
            overallReadinessScore: 28.0,
            fitnessCertificates: {
              ...t.fitnessCertificates,
              telecom: {
                ...t.fitnessCertificates.telecom,
                status: 'REVOKED' as any,
                notes: 'Radio channel handshake failure',
              },
            },
          };
        }
        if (t.rakeNumber === 'KM-108') {
          return {
            ...t,
            assignedRole: 'REVENUE_SERVICE' as InductionRole,
            overallReadinessScore: 95.0,
          };
        }
        return t;
      });
      setTrainsets(updated);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans text-slate-800">
      {/* Official Kochi Metro Header */}
      <Header
        trainsets={trainsets}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onRunOptimization={handleRunOptimization}
        isOptimizing={isOptimizing}
        onOpenExportModal={() => setIsExportModalOpen(true)}
      />

      {/* Backend API Live Connection Banner */}
      <div className="bg-slate-800 text-white px-4 py-1.5 border-b border-slate-700 text-xs flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {isApiConnected ? (
            <>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-medium text-emerald-300">FastAPI ML Engine Connected (Port 8000)</span>
            </>
          ) : (
            <>
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              <span className="font-medium text-amber-300">Offline / Mock Mode (Start backend server with `python -m uvicorn kochi_metro.api.main:app --reload`)</span>
            </>
          )}
        </div>
        <span className="text-slate-400">CP-SAT Optimizer & Dual-ML Active</span>
      </div>

      {/* Main App Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'board' && (
          <InductionBoardView
            trainsets={trainsets}
            onOpenOverrideModal={(t) => setSelectedTrainForOverride(t)}
          />
        )}
        {activeTab === 'matrix' && <VariableMatrixView trainsets={trainsets} />}
        {activeTab === 'optimizer' && (
          <OptimizerControlView
            weights={weights}
            onWeightsChange={setWeights}
            onRunOptimization={handleRunOptimization}
            isOptimizing={isOptimizing}
          />
        )}
        {activeTab === 'map' && <DepotYardMap trainsets={trainsets} />}
        {activeTab === 'simulator' && <WhatIfSimulator onApplyScenario={handleApplyScenario} />}
        {activeTab === 'ingestion' && <DataIngestionView />}
        {activeTab === 'analytics' && <AnalyticsView trainsets={trainsets} />}
      </main>

      {/* Manual Supervisor Override Modal */}
      {selectedTrainForOverride && (
        <SupervisorOverrideModal
          train={selectedTrainForOverride}
          onClose={() => setSelectedTrainForOverride(null)}
          onSave={handleSaveOverride}
        />
      )}

      {/* Export Report Modal */}
      {isExportModalOpen && (
        <ExportReportModal
          trainsets={trainsets}
          weights={weights}
          onClose={() => setIsExportModalOpen(false)}
        />
      )}
    </div>
  );
};

export default App;
