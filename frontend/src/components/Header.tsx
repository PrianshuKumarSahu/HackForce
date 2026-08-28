import React, { useState, useEffect } from 'react';
import { Clock, ShieldCheck, TrendingUp, AlertTriangle, Building2, Train, CheckCircle2 } from 'lucide-react';
import { Trainset } from '../types';

interface HeaderProps {
  trainsets: Trainset[];
  activeTab: string;
  onTabChange: (tab: string) => void;
  onRunOptimization: () => void;
  isOptimizing: boolean;
  onOpenExportModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  trainsets,
  activeTab,
  onTabChange,
  onRunOptimization,
  isOptimizing,
  onOpenExportModal,
}) => {
  const [currentTime, setCurrentTime] = useState<string>('');
  const [selectedDepot, setSelectedDepot] = useState<string>('Muttom Depot (Primary)');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString('en-IN', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        }) + ' IST'
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const revenueCount = trainsets.filter((t) => t.assignedRole === 'REVENUE_SERVICE').length;
  const standbyCount = trainsets.filter((t) => t.assignedRole === 'HOT_STANDBY').length;
  const iblCount = trainsets.filter((t) => t.assignedRole === 'IBL_MAINTENANCE').length;
  const cleaningCount = trainsets.filter((t) => t.assignedRole === 'CLEANING_BAY').length;

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50 shadow-lg">
      {/* Top Branding Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          
          {/* Logo & Platform Name */}
          <div className="flex items-center space-x-3.5">
            {/* Official KMRL Logo SVG */}
            <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-teal-500/30 flex items-center justify-center p-1.5 shadow-md shadow-teal-500/10">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="-258 191.7 441.7 178.3" className="w-full h-full">
                <path fill="#009999" d="M-170.9,315.8c-15.5,15.3-31,30.7-46.5,46c-6.5,6.5-14.1,9.2-23.2,6.8c-9.6-2.6-16.4-11.3-16.4-21.4c-0.1-44.1-0.1-88.2,0-132.4c0-12.6,10-22.2,22.8-22.2c12.5,0,22.3,9.4,22.4,22c0.1,23.5,0.1,47,0.1,70.5c0,1.8,0,3.5,0,6.5c2.1-1.9,3.4-2.9,4.5-4c28.7-28.9,57.6-57.7,86.5-86.6c11.4-11.3,24.2-11.4,35.5-0.2c15,14.9,29.9,29.9,44.9,44.8c1.2,1.2,2.5,2.1,3.8,3.1c10.6,10.6,21.1,21.2,31.7,31.8c9.7,9.8,19.3,19.7,29,29.5c6.6,6.6,13.2,13.1,19.8,19.7c9.5,9.5,10,23.4,1,32.6c-9.3,9.5-23.2,9.5-33-0.2c-14.8-14.7-29.5-29.4-44.2-44.1c-1.7-1.7-3.8-3.2-5.6-4.8c-2.6-2.9-5.1-6-7.9-8.7c-7.9-7.7-15.9-15.3-23.8-23c-6.1-6.3-12.1-12.6-18.2-19c-4.9-5.1-9.6-10.4-13.8-14.8c-10.5,10-20,19-29.5,28.1c-0.7,0.6-1.3,1.3-2,1.9c-2,2-4,4-6.1,6.1c-8.8,8.8-17.6,17.6-26.4,26.4c-1.1,1.1-2.2,2.2-3.3,3.2C-169.3,314.2-170.1,315-170.9,315.8z" />
                <path fill="#16DDDD" d="M-4.8,280.6c-10.6-10.6-21.1-21.2-31.7-31.8c16.9-17,33.7-34.1,50.9-50.8c7.9-7.7,21.7-7.1,30,1c21.1,20.8,42,41.8,63,62.7c22.7,22.7,45.5,45.4,68.2,68.1c6.9,6.8,9.3,15,6.4,24.2c-2.9,8.8-9.4,14.1-18.6,15.3c-8,1.1-14.5-2-20.2-7.7c-21-21.1-42.1-42.2-63.2-63.2c-15.8-15.8-31.6-31.5-47.4-47.2c-1.1-1.1-2.5-2.1-4-3.3C17.2,258.9,6.2,269.7-4.8,280.6z" />
                <path fill="#16DDDD" d="M-69.5,281.6c7.9,7.7,15.9,15.2,23.8,23c2.8,2.7,5.3,5.8,7.9,8.7C-49.2,324.9-60.6,336.5-72,348c-4.5,4.6-9.1,9.2-13.7,13.8c-10.1,10.2-23.7,10.3-34.1,0.3c-2.3-2.2-4.5-4.4-6.8-6.6c-1.1-1-2.2-2-3.3-3l-0.1,0.2l0.1-0.2c-1.7-1.7-3.3-3.3-5-5l-0.2,0.1l0.2-0.1c-1.4-1.5-2.9-3.1-4.3-4.6l-0.1-0.1c-2.9-2.8-5.8-5.5-8.6-8.3c-3.1-3.1-6.2-6.3-9.3-9.4c-1-1.1-2.1-2.2-3.1-3.3c-0.7-0.7-1.3-1.3-2-2c-0.1-0.7-0.3-1.4-0.4-2.1c8.9-9,17.9-17.9,26.8-26.9c0.6-0.6,1.3-1.2,1.9-1.8c0.4-0.4,0.8-0.8,1.2-1.3c0.3-0.1,0.5-0.2,0.7-0.5c0.7,0,1.3,0,2,0.1c8.9,9.1,17.8,18.2,27.6,28.2C-90.9,303.7-80.2,292.6-69.5,281.6z" />
              </svg>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-heading font-extrabold text-lg text-white tracking-wide">KOCHI METRO</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-300 font-semibold border border-teal-500/30">
                  AI Induction Engine
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">Nightly Train Induction & Multi-Objective Scheduling System (21:00–23:00 IST)</p>
            </div>
          </div>

          {/* Operational Metrics & Actions */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Depot Selector */}
            <div className="flex items-center space-x-1.5 bg-slate-800/90 px-3 py-1.5 rounded-lg border border-slate-700 text-xs">
              <Building2 className="w-4 h-4 text-teal-400" />
              <select
                value={selectedDepot}
                onChange={(e) => setSelectedDepot(e.target.value)}
                className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
              >
                <option value="Muttom Depot (Primary)" className="bg-slate-800">Muttom Depot (25 Rakes)</option>
                <option value="Kakkanad Depot (Phase II)" className="bg-slate-800">Kakkanad Depot (Phase II Planned)</option>
              </select>
            </div>

            {/* Live Clock with Countdown to Dawn Rollout */}
            <div className="flex items-center space-x-2 bg-slate-800/90 px-3 py-1.5 rounded-lg border border-slate-700 text-xs font-mono text-teal-300">
              <Clock className="w-4 h-4 text-teal-400 animate-pulse" />
              <span>{currentTime || '21:45:00 IST'}</span>
              <span className="text-slate-400 text-[10px]">| Dawn: 05:30</span>
            </div>

            {/* Re-Optimize Button */}
            <button
              onClick={onRunOptimization}
              disabled={isOptimizing}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white shadow-md transition-all ${
                isOptimizing
                  ? 'bg-teal-700 opacity-80 cursor-not-allowed'
                  : 'bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 shadow-teal-500/20 active:scale-95'
              }`}
            >
              <TrendingUp className={`w-3.5 h-3.5 ${isOptimizing ? 'animate-spin' : ''}`} />
              <span>{isOptimizing ? 'Solving CP-SAT...' : 'Run Optimization'}</span>
            </button>

            {/* Export Official Chart */}
            <button
              onClick={onOpenExportModal}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-colors"
            >
              <span>Export Chart</span>
            </button>
          </div>
        </div>

        {/* Fleet Allocation Summary Strip */}
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center space-x-3 text-slate-300">
            <span className="text-slate-400">Nightly Allocation (25 Rakes):</span>
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-emerald-950/80 text-emerald-300 border border-emerald-500/30 font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{revenueCount} Revenue (Dawn)</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-amber-950/80 text-amber-300 border border-amber-500/30 font-semibold">
              <Train className="w-3.5 h-3.5" />
              <span>{standbyCount} Hot Standby</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-rose-950/80 text-rose-300 border border-rose-500/30 font-semibold">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{iblCount} IBL Overhaul</span>
            </span>
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 font-semibold">
              <span>{cleaningCount} Deep Wash</span>
            </span>
          </div>

          <div className="flex items-center space-x-4 text-[11px] text-slate-400">
            <span className="flex items-center space-x-1 text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Punctuality KPI: <strong>99.5% Protected</strong></span>
            </span>
            <span className="text-slate-500">|</span>
            <span className="text-teal-400">Branding SLA: <strong>98.4% Compliant</strong></span>
            <span className="text-slate-500">|</span>
            <span className="text-indigo-400">Shunting Moves: <strong>-34% Energy Saved</strong></span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs Bar */}
      <div className="bg-slate-950/90 border-t border-slate-800/90 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex space-x-1 overflow-x-auto py-1 scrollbar-none">
          {[
            { id: 'board', label: '🏆 Nightly Induction Board', badge: `${revenueCount} Active` },
            { id: 'matrix', label: '📊 6-Variable Matrix', badge: 'Tri-Dept / Maximo / Brand' },
            { id: 'solver', label: '⚡ CP-SAT Optimizer', badge: 'Multi-Objective' },
            { id: 'depot', label: '🗺️ Muttom Depot Geometry', badge: '12 Stabling Tracks' },
            { id: 'whatif', label: '🧪 What-If Simulator', badge: 'Fault Injection' },
            { id: 'ingestion', label: '📥 Data Ingestion (Maximo/IoT)', badge: 'UNS Stream' },
            { id: 'analytics', label: '📈 ML Learning & XAI Audit', badge: 'Feedback Loop' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`px-3.5 py-2 text-xs font-semibold rounded-t-lg transition-all flex items-center space-x-2 whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-slate-800 text-teal-300 border-b-2 border-teal-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <span>{tab.label}</span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded ${
                  activeTab === tab.id
                    ? 'bg-teal-500/20 text-teal-200 border border-teal-500/30'
                    : 'bg-slate-800 text-slate-500'
                }`}
              >
                {tab.badge}
              </span>
            </button>
          ))}
        </div>
      </div>
    </header>
  );
};
