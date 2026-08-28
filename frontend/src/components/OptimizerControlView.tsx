import React, { useState } from 'react';
import { OptimizationWeights } from '../types';
import {
  Sliders,
  Play,
  CheckCircle2,
  AlertCircle,
  Zap,
  TrendingUp,
  Cpu,
  RotateCcw,
  ShieldCheck,
  Award,
  Gauge,
  Layers,
  Sparkles
} from 'lucide-react';

interface OptimizerControlViewProps {
  weights: OptimizationWeights;
  onUpdateWeights: (newWeights: OptimizationWeights) => void;
  onRunOptimization: () => void;
  isOptimizing: boolean;
}

export const OptimizerControlView: React.FC<OptimizerControlViewProps> = ({
  weights,
  onUpdateWeights,
  onRunOptimization,
  isOptimizing,
}) => {
  const [localWeights, setLocalWeights] = useState<OptimizationWeights>(weights);

  const handleSliderChange = (key: keyof OptimizationWeights, value: number) => {
    const updated = { ...localWeights, [key]: value };
    setLocalWeights(updated);
    onUpdateWeights(updated);
  };

  const handleReset = () => {
    const defaultWeights: OptimizationWeights = {
      punctualityWeight: 95,
      brandingWeight: 80,
      mileageBalanceWeight: 75,
      shuntingMinimizationWeight: 85,
      cleaningAdherenceWeight: 70,
    };
    setLocalWeights(defaultWeights);
    onUpdateWeights(defaultWeights);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-teal-50 text-teal-700 font-bold text-xs border border-teal-200">
              <Cpu className="w-3.5 h-3.5" />
              <span>Google OR-Tools CP-SAT Solver Engine</span>
            </div>
            <h2 className="text-xl font-heading font-extrabold text-slate-900 mt-1">
              Multi-Objective Induction Optimizer
            </h2>
            <p className="text-xs text-slate-600 mt-0.5 max-w-2xl">
              Configure mathematical weights for constraint relaxation, branding prioritization, and shunting minimization. Hard safety constraints are non-negotiable.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleReset}
              className="px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Defaults</span>
            </button>
            <button
              onClick={onRunOptimization}
              disabled={isOptimizing}
              className={`px-5 py-2 rounded-lg text-xs font-bold text-white shadow-md flex items-center space-x-2 transition-all ${
                isOptimizing
                  ? 'bg-teal-700 opacity-80 cursor-not-allowed'
                  : 'bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 shadow-teal-500/25 active:scale-95'
              }`}
            >
              <Play className={`w-3.5 h-3.5 fill-current ${isOptimizing ? 'animate-spin' : ''}`} />
              <span>{isOptimizing ? 'Executing CP-SAT...' : 'Run Full Solve'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Solver Diagnostics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-xs font-semibold text-slate-500">Solver Status</div>
          <div className="text-xl font-heading font-extrabold text-emerald-600 mt-1 flex items-center justify-center space-x-1">
            <CheckCircle2 className="w-5 h-5" />
            <span>OPTIMAL_FOUND</span>
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">Solve time: 384 ms (CP-SAT v9.8)</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-xs font-semibold text-slate-500">Hard Constraints</div>
          <div className="text-xl font-heading font-extrabold text-slate-900 mt-1">100% Satisfied</div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-0.5">0 Safety Violations</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-xs font-semibold text-slate-500">Total Penalties Averted</div>
          <div className="text-xl font-heading font-extrabold text-purple-600 mt-1">₹3,72,500</div>
          <div className="text-[11px] text-slate-400 mt-0.5">7 Advertiser SLAs Saved</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
          <div className="text-xs font-semibold text-slate-500">Shunting Moves Saved</div>
          <div className="text-xl font-heading font-extrabold text-teal-600 mt-1">-34% Less Energy</div>
          <div className="text-[11px] text-slate-400 mt-0.5">Muttom Depot Track Optimization</div>
        </div>
      </div>

      {/* Interactive Weight Sliders */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
        <h3 className="font-heading font-bold text-slate-900 text-base flex items-center space-x-2">
          <Sliders className="w-5 h-5 text-teal-600" />
          <span>Multi-Objective Mathematical Weight Matrix</span>
        </h3>

        <div className="space-y-6">
          {/* 1. Punctuality Hard Constraint */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span className="font-semibold text-slate-800 text-sm">
                  1. Punctuality & Tri-Department Safety Clearances
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">
                  HARD CONSTRAINT
                </span>
              </div>
              <span className="font-mono font-bold text-slate-800 text-sm">{localWeights.punctualityWeight}%</span>
            </div>
            <p className="text-xs text-slate-500">
              Enforces strict 99.5% Punctuality SLA. Rakes with missing Rolling-Stock, Signalling, or Telecom clearances are mathematically locked from dawn induction.
            </p>
            <input
              type="range"
              min="50"
              max="100"
              value={localWeights.punctualityWeight}
              onChange={(e) => handleSliderChange('punctualityWeight', Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
            />
          </div>

          {/* 2. Branding SLA Exposure Weight */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Award className="w-4 h-4 text-purple-600" />
                <span className="font-semibold text-slate-800 text-sm">
                  2. Branding Wrap Contract SLA Exposure Priority
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-purple-100 text-purple-800 font-bold">
                  FINANCIAL PENALTY MITIGATION
                </span>
              </div>
              <span className="font-mono font-bold text-slate-800 text-sm">{localWeights.brandingWeight}%</span>
            </div>
            <p className="text-xs text-slate-500">
              Prioritizes rakes with high advertiser penalty rates (Federal Bank, Muthoot, Kalyan Silks) to prevent contract default.
            </p>
            <input
              type="range"
              min="0"
              max="100"
              value={localWeights.brandingWeight}
              onChange={(e) => handleSliderChange('brandingWeight', Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
            />
          </div>

          {/* 3. Mileage & Bogie Wear Balancing */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Gauge className="w-4 h-4 text-teal-600" />
                <span className="font-semibold text-slate-800 text-sm">
                  3. Fleet Mileage Balancing & Bogie/Brake Wear Equalization
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-teal-100 text-teal-800 font-bold">
                  LIFECYCLE COST CONTROL
                </span>
              </div>
              <span className="font-mono font-bold text-slate-800 text-sm">{localWeights.mileageBalanceWeight}%</span>
            </div>
            <p className="text-xs text-slate-500">
              Assigns higher daily targets to low-mileage rakes (e.g. KM-115 at 165k km) while holding back high-fatigue rakes to balance lifecycle wear.
            </p>
            <input
              type="range"
              min="0"
              max="100"
              value={localWeights.mileageBalanceWeight}
              onChange={(e) => handleSliderChange('mileageBalanceWeight', Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
            />
          </div>

          {/* 4. Stabling Geometry & Shunting Minimization */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-indigo-600" />
                <span className="font-semibold text-slate-800 text-sm">
                  4. Stabling Track Geometry & Shunting Turn-Out Minimization
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 font-bold">
                  DEPOT ENERGY EFFICIENCY
                </span>
              </div>
              <span className="font-mono font-bold text-slate-800 text-sm">{localWeights.shuntingMinimizationWeight}%</span>
            </div>
            <p className="text-xs text-slate-500">
              Minimizes night-time shunting movements across Muttom Depot's 12 stabling tracks, prioritizing front-lane rakes for 05:30 launch.
            </p>
            <input
              type="range"
              min="0"
              max="100"
              value={localWeights.shuntingMinimizationWeight}
              onChange={(e) => handleSliderChange('shuntingMinimizationWeight', Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
            />
          </div>

          {/* 5. Deep Cleaning Slot Adherence */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-amber-600" />
                <span className="font-semibold text-slate-800 text-sm">
                  5. Interior Deep Cleaning & Washing Slot Adherence
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold">
                  PASSENGER HYGIENE
                </span>
              </div>
              <span className="font-mono font-bold text-slate-800 text-sm">{localWeights.cleaningAdherenceWeight}%</span>
            </div>
            <p className="text-xs text-slate-500">
              Guarantees designated rakes are routed through the Automatic Washing Plant and given deep sanitization cycles every 7 days.
            </p>
            <input
              type="range"
              min="0"
              max="100"
              value={localWeights.cleaningAdherenceWeight}
              onChange={(e) => handleSliderChange('cleaningAdherenceWeight', Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
