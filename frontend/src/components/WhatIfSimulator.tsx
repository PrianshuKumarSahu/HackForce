import React, { useState } from 'react';
import { SIMULATION_SCENARIOS } from '../data/mockData';
import { SimulationScenario, Trainset } from '../types';
import {
  FlaskConical,
  Play,
  CheckCircle2,
  AlertTriangle,
  Zap,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  Sparkles,
  Info
} from 'lucide-react';

interface WhatIfSimulatorProps {
  trainsets: Trainset[];
  onApplyScenario: (scenario: SimulationScenario) => void;
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({ trainsets, onApplyScenario }) => {
  const [selectedScenario, setSelectedScenario] = useState<SimulationScenario>(SIMULATION_SCENARIOS[0]);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simulationResult, setSimulationResult] = useState<SimulationScenario | null>(null);

  const handleRunSimulation = (scenario: SimulationScenario) => {
    setSelectedScenario(scenario);
    setIsSimulating(true);
    setTimeout(() => {
      setIsSimulating(false);
      setSimulationResult(scenario);
      onApplyScenario(scenario);
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-teal-50 text-teal-700 font-bold text-xs border border-teal-200">
              <FlaskConical className="w-3.5 h-3.5" />
              <span>Real-Time Disruption & Contingency Engine</span>
            </div>
            <h2 className="text-xl font-heading font-extrabold text-slate-900 mt-1">
              "What-If" Scenario Simulator & Rapid Re-Induction
            </h2>
            <p className="text-xs text-slate-600 mt-0.5 max-w-2xl">
              Simulate midnight emergency withdrawals, sudden monsoon ridership spikes, or advertiser SLA threats to verify automated resilience.
            </p>
          </div>

          <span className="text-xs font-semibold px-3 py-1.5 rounded-full bg-slate-900 text-teal-300">
            Punctuality Recovery Target: &lt; 4.0 mins
          </span>
        </div>
      </div>

      {/* Scenarios Selection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {SIMULATION_SCENARIOS.map((sc) => {
          const isSelected = selectedScenario.id === sc.id;
          return (
            <div
              key={sc.id}
              onClick={() => setSelectedScenario(sc)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'bg-teal-50/80 border-teal-500 ring-2 ring-teal-500/20 shadow-md'
                  : 'bg-white border-slate-200 hover:border-teal-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800">
                  {sc.disruptionType}
                </span>
                <span className="text-xs font-mono font-bold text-slate-700">{sc.affectedTrain}</span>
              </div>
              <h3 className="font-heading font-bold text-slate-900 text-sm mt-2">{sc.name}</h3>
              <p className="text-xs text-slate-600 mt-1 line-clamp-2">{sc.description}</p>

              <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400">Severity: <strong>{sc.impactSeverity}</strong></span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRunSimulation(sc);
                  }}
                  className="px-3 py-1 rounded bg-slate-900 hover:bg-teal-600 text-white font-semibold text-xs transition-colors flex items-center space-x-1"
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>Test Scenario</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Simulation Result & AI Mitigation Console */}
      <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800 shadow-xl text-white space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-teal-400" />
            <span className="font-heading font-bold text-sm text-slate-200">
              AI Dynamic Contingency Response for "{selectedScenario.name}"
            </span>
          </div>
          {isSimulating && (
            <span className="text-xs font-mono text-teal-300 animate-pulse">
              Running CP-SAT Disruption Re-solve...
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
          {/* Scenario Trigger */}
          <div className="bg-slate-800/80 p-4 rounded-xl border border-slate-700 space-y-2">
            <div className="font-bold text-rose-400 flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4" />
              <span>Simulated Event Description:</span>
            </div>
            <p className="text-slate-300 leading-relaxed">{selectedScenario.description}</p>
            <div className="text-slate-400 pt-2 border-t border-slate-700/60">
              Targeted Units: <strong className="text-teal-300">{selectedScenario.affectedTrain}</strong>
            </div>
          </div>

          {/* AI Recommended Mitigation Action */}
          <div className="bg-teal-950/60 p-4 rounded-xl border border-teal-800/60 space-y-2">
            <div className="font-bold text-teal-300 flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4" />
              <span>Autonomous AI Mitigation Protocol:</span>
            </div>
            <p className="text-teal-100 leading-relaxed font-medium">{selectedScenario.recommendedAction}</p>
            <div className="text-teal-300/80 pt-2 border-t border-teal-800/60 flex items-center justify-between">
              <span>99.5% Punctuality: <strong className="text-white">Protected</strong></span>
              <span>Advertiser SLA: <strong className="text-white">Preserved</strong></span>
            </div>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={() => handleRunSimulation(selectedScenario)}
            disabled={isSimulating}
            className="px-4 py-2 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow-md transition-all flex items-center space-x-2"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isSimulating ? 'Recalculating Schedule...' : 'Apply Mitigation to Live Board'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
