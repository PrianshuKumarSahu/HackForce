import React, { useState } from 'react';
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

export const App: React.FC = () => {
  const [trainsets, setTrainsets] = useState<Trainset[]>(INITIAL_TRAINSETS);
  const [weights, setWeights] = useState<OptimizationWeights>(INITIAL_OPTIMIZATION_WEIGHTS);
  const [activeTab, setActiveTab] = useState<string>('board');
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [selectedTrainForOverride, setSelectedTrainForOverride] = useState<Trainset | null>(null);
  const [isExportModalOpen, setIsExportModalOpen] = useState<boolean>(false);

  // Run CP-SAT Optimization simulation
  const handleRunOptimization = () => {
    setIsOptimizing(true);
    setTimeout(() => {
      setIsOptimizing(false);
      // Re-calculate scores based on weights
      const updated = trainsets.map((t, idx) => {
        let score = 95 - idx * 2.8;
        if (t.fitnessCertificates.rollingStock.status !== 'VALID' || t.fitnessCertificates.signalling.status !== 'VALID') {
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
    }, 600);
  };

  // Supervisor Manual Override handler
  const handleSaveOverride = (
    trainId: string,
    newRole: InductionRole,
    justification: string,
    supervisorName: string
  ) => {
    const updated = trainsets.map((t) => {
      if (t.id === trainId) {
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

  // What-If Scenario injection handler
  const handleApplyScenario = (scenario: SimulationScenario) => {
    if (scenario.id === 'sc-1') {
      // Telecom Failure on KM-101
      const updated = trainsets.map((t) => {
        if (t.rakeNumber === 'KM-101') {
          return {
            ...t,
            assignedRole: 'IBL_MAINTENANCE' as InductionRole,
            overallReadinessScore: 28.0,
            fitnessCertificates: {
              ...t.fitnessCertificates,
              telecom: { ...t.fitnessCertificates.telecom, status: 'REVOKED' as any, notes: 'Radio channel handshake failure' },
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

      {/* Main Operational Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'board' && (
          <InductionBoardView
            trainsets={trainsets}
            onOpenOverrideModal={(t) => setSelectedTrainForOverride(t)}
          />
        )}

        {activeTab === 'matrix' && <VariableMatrixView trainsets={trainsets} />}

        {activeTab === 'solver' && (
          <OptimizerControlView
            weights={weights}
            onUpdateWeights={setWeights}
            onRunOptimization={handleRunOptimization}
            isOptimizing={isOptimizing}
          />
        )}

        {activeTab === 'depot' && (
          <DepotYardMap
            trainsets={trainsets}
            onOpenOverrideModal={(t) => setSelectedTrainForOverride(t)}
          />
        )}

        {activeTab === 'whatif' && (
          <WhatIfSimulator trainsets={trainsets} onApplyScenario={handleApplyScenario} />
        )}

        {activeTab === 'ingestion' && <DataIngestionView />}

        {activeTab === 'analytics' && <AnalyticsView trainsets={trainsets} />}
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 py-4 text-xs text-center">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Kochi Metro Rail Limited (KMRL) • AI Nightly Train Induction Decision-Support System</span>
          <span className="text-teal-400 font-medium">Muttom Depot • Fleet Scaling 25 ➔ 40 Trainsets</span>
        </div>
      </footer>

      {/* Modals */}
      <SupervisorOverrideModal
        train={selectedTrainForOverride}
        onClose={() => setSelectedTrainForOverride(null)}
        onSaveOverride={handleSaveOverride}
      />

      {isExportModalOpen && (
        <ExportReportModal trainsets={trainsets} onClose={() => setIsExportModalOpen(false)} />
      )}
    </div>
  );
};
