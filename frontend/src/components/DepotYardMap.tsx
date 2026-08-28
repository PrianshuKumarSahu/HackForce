import React, { useState } from 'react';
import { Trainset } from '../types';
import { Layers, Train, CheckCircle2, AlertTriangle, Sparkles, Zap, Wrench, Info } from 'lucide-react';

interface DepotYardMapProps {
  trainsets: Trainset[];
  onOpenOverrideModal: (train: Trainset) => void;
}

export const DepotYardMap: React.FC<DepotYardMapProps> = ({ trainsets, onOpenOverrideModal }) => {
  const [selectedTrain, setSelectedTrain] = useState<Trainset | null>(trainsets[0] || null);

  const stablingLines = Array.from({ length: 12 }, (_, i) => {
    const num = String(i + 1).padStart(2, '0');
    return `ST-${num}`;
  });

  const getRakeColor = (train: Trainset) => {
    switch (train.assignedRole) {
      case 'REVENUE_SERVICE':
        return 'bg-emerald-600 border-emerald-400 text-white shadow-emerald-600/30';
      case 'HOT_STANDBY':
        return 'bg-amber-500 border-amber-300 text-white shadow-amber-500/30';
      case 'IBL_MAINTENANCE':
        return 'bg-rose-600 border-rose-400 text-white shadow-rose-600/30';
      case 'CLEANING_BAY':
        return 'bg-teal-500 border-teal-300 text-white shadow-teal-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-teal-50 text-teal-700 font-bold text-xs border border-teal-200">
              <Layers className="w-3.5 h-3.5" />
              <span>Muttom Depot Track Topology Visualizer</span>
            </div>
            <h2 className="text-xl font-heading font-extrabold text-slate-900 mt-1">
              2D Depot Stabling Yard Layout & Turn-Out Sequencing
            </h2>
            <p className="text-xs text-slate-600 mt-0.5 max-w-2xl">
              Real-time map of all 12 Stabling Tracks, Inspection Bay Lines (IBL), and Automatic Wash Plant. Click any rake to inspect turn-out paths.
            </p>
          </div>

          {/* Legend */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="flex items-center space-x-1 px-2 py-1 rounded bg-emerald-100 text-emerald-800 font-semibold">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
              <span>Revenue (Dawn 05:30)</span>
            </span>
            <span className="flex items-center space-x-1 px-2 py-1 rounded bg-amber-100 text-amber-800 font-semibold">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
              <span>Hot Standby Siding</span>
            </span>
            <span className="flex items-center space-x-1 px-2 py-1 rounded bg-rose-100 text-rose-800 font-semibold">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-600"></span>
              <span>IBL Maintenance</span>
            </span>
            <span className="flex items-center space-x-1 px-2 py-1 rounded bg-teal-100 text-teal-800 font-semibold">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-500"></span>
              <span>Wash Plant</span>
            </span>
          </div>
        </div>
      </div>

      {/* Main Depot Map & Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visual Depot Yard Lines (2 cols) */}
        <div className="lg:col-span-2 bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-5 text-white">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <Train className="w-5 h-5 text-teal-400" />
              <span className="font-heading font-bold text-sm text-slate-200">
                Muttom Depot Track Geometry (12 Stabling Lines + IBL + Wash Bay)
              </span>
            </div>
            <span className="text-xs text-teal-400 font-mono">Mainline Egress ➔ Aluva (North)</span>
          </div>

          {/* Stabling Lines 1-12 */}
          <div className="space-y-3">
            {stablingLines.map((line) => {
              const trainsOnLine = trainsets.filter((t) => t.stabling.trackLine === line);
              const pos1Train = trainsOnLine.find((t) => t.stabling.positionDepth === 1);
              const pos2Train = trainsOnLine.find((t) => t.stabling.positionDepth === 2);

              return (
                <div key={line} className="flex items-center space-x-3 text-xs">
                  {/* Track Label */}
                  <div className="w-14 font-mono font-bold text-teal-400 text-right shrink-0">{line}</div>

                  {/* Track Rails Line */}
                  <div className="flex-1 h-9 bg-slate-800/80 rounded-lg border border-slate-700/80 p-1 flex items-center justify-between relative overflow-hidden">
                    {/* Rail ties lines */}
                    <div className="absolute inset-0 flex justify-around items-center opacity-10 pointer-events-none">
                      {Array.from({ length: 16 }).map((_, idx) => (
                        <div key={idx} className="w-0.5 h-full bg-slate-400"></div>
                      ))}
                    </div>

                    {/* Position 2 Rake (Inner) */}
                    <div className="w-[48%] h-full z-10">
                      {pos2Train ? (
                        <button
                          onClick={() => setSelectedTrain(pos2Train)}
                          className={`w-full h-full rounded flex items-center justify-between px-2 text-[11px] font-bold border transition-all ${getRakeColor(
                            pos2Train
                          )} ${selectedTrain?.id === pos2Train.id ? 'ring-2 ring-white scale-[1.02]' : 'hover:opacity-90'}`}
                        >
                          <span className="flex items-center space-x-1">
                            <span>{pos2Train.rakeNumber}</span>
                            <span className="text-[9px] opacity-80">(Pos 2)</span>
                          </span>
                          <span className="text-[10px] opacity-90">{pos2Train.stabling.turnoutTimeMins}m</span>
                        </button>
                      ) : (
                        <div className="w-full h-full border border-dashed border-slate-700/60 rounded flex items-center justify-center text-[10px] text-slate-600">
                          Empty Slot
                        </div>
                      )}
                    </div>

                    {/* Position 1 Rake (Front / Departure Line) */}
                    <div className="w-[48%] h-full z-10">
                      {pos1Train ? (
                        <button
                          onClick={() => setSelectedTrain(pos1Train)}
                          className={`w-full h-full rounded flex items-center justify-between px-2 text-[11px] font-bold border transition-all ${getRakeColor(
                            pos1Train
                          )} ${selectedTrain?.id === pos1Train.id ? 'ring-2 ring-white scale-[1.02]' : 'hover:opacity-90'}`}
                        >
                          <span className="flex items-center space-x-1">
                            <span>{pos1Train.rakeNumber}</span>
                            <span className="text-[9px] opacity-80">(Front)</span>
                          </span>
                          <span className="text-[10px] opacity-90">{pos1Train.stabling.turnoutTimeMins}m</span>
                        </button>
                      ) : (
                        <div className="w-full h-full border border-dashed border-slate-700/60 rounded flex items-center justify-center text-[10px] text-slate-600">
                          Empty Slot
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Special Lines (IBL & Wash) */}
          <div className="pt-3 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            {/* Inspection Bay Lines */}
            <div className="bg-slate-800/60 p-3 rounded-xl border border-rose-900/40 space-y-2">
              <div className="font-bold text-rose-400 flex items-center space-x-1.5">
                <Wrench className="w-4 h-4" />
                <span>Inspection Bay Lines (IBL 1–3)</span>
              </div>
              <div className="space-y-1.5">
                {trainsets
                  .filter((t) => t.assignedRole === 'IBL_MAINTENANCE')
                  .map((train) => (
                    <button
                      key={train.id}
                      onClick={() => setSelectedTrain(train)}
                      className={`w-full p-2 rounded bg-rose-950/80 border border-rose-700/60 text-left flex items-center justify-between text-xs text-rose-200 transition-all ${
                        selectedTrain?.id === train.id ? 'ring-2 ring-white' : ''
                      }`}
                    >
                      <span className="font-bold">{train.rakeNumber} ({train.stabling.trackLine})</span>
                      <span className="text-[10px] text-rose-300">Overhaul Hold</span>
                    </button>
                  ))}
              </div>
            </div>

            {/* Wash Bay */}
            <div className="bg-slate-800/60 p-3 rounded-xl border border-teal-900/40 space-y-2">
              <div className="font-bold text-teal-400 flex items-center space-x-1.5">
                <Sparkles className="w-4 h-4" />
                <span>Automatic Washing Plant (WASH-01)</span>
              </div>
              <div className="space-y-1.5">
                {trainsets
                  .filter((t) => t.assignedRole === 'CLEANING_BAY')
                  .map((train) => (
                    <button
                      key={train.id}
                      onClick={() => setSelectedTrain(train)}
                      className={`w-full p-2 rounded bg-teal-950/80 border border-teal-700/60 text-left flex items-center justify-between text-xs text-teal-200 transition-all ${
                        selectedTrain?.id === train.id ? 'ring-2 ring-white' : ''
                      }`}
                    >
                      <span className="font-bold">{train.rakeNumber} (WASH-01)</span>
                      <span className="text-[10px] text-teal-300">Deep Bio-Sanitize</span>
                    </button>
                  ))}
              </div>
            </div>
          </div>
        </div>

        {/* Selected Rake Deep Inspector (1 col) */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="border-b border-slate-100 pb-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
              Track Bay Telemetry
            </span>
            <h3 className="font-heading font-extrabold text-slate-900 text-lg mt-1 flex items-center justify-between">
              <span>{selectedTrain ? selectedTrain.rakeNumber : 'Select a Rake'}</span>
              {selectedTrain && (
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                  {selectedTrain.stabling.trackLine} - Pos {selectedTrain.stabling.positionDepth}
                </span>
              )}
            </h3>
          </div>

          {selectedTrain ? (
            <div className="space-y-4 text-xs">
              {/* Role & Readiness */}
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">AI Assigned Role:</span>
                  <strong className="text-slate-900">{selectedTrain.assignedRole}</strong>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Readiness Score:</span>
                  <strong className="text-teal-700">{selectedTrain.overallReadinessScore}% (Rank #{selectedTrain.rank})</strong>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Turnout Time:</span>
                  <strong className="text-slate-900">{selectedTrain.stabling.turnoutTimeMins} mins ({selectedTrain.stabling.shuntingTurnsNeeded} shunts)</strong>
                </div>
              </div>

              {/* Tri-Dept Fitness */}
              <div>
                <span className="font-bold text-slate-800">Tri-Department Certifications:</span>
                <div className="grid grid-cols-3 gap-2 mt-1.5 text-center">
                  <div className="p-2 rounded bg-slate-50 border border-slate-200">
                    <div className="text-[10px] text-slate-500">Rolling-Stock</div>
                    <div className="font-bold text-emerald-700 mt-0.5">{selectedTrain.fitnessCertificates.rollingStock.status}</div>
                  </div>
                  <div className="p-2 rounded bg-slate-50 border border-slate-200">
                    <div className="text-[10px] text-slate-500">Signalling</div>
                    <div className="font-bold text-emerald-700 mt-0.5">{selectedTrain.fitnessCertificates.signalling.status}</div>
                  </div>
                  <div className="p-2 rounded bg-slate-50 border border-slate-200">
                    <div className="text-[10px] text-slate-500">Telecom</div>
                    <div className="font-bold text-emerald-700 mt-0.5">{selectedTrain.fitnessCertificates.telecom.status}</div>
                  </div>
                </div>
              </div>

              {/* Branding Info */}
              <div>
                <span className="font-bold text-slate-800">Branding Contract:</span>
                {selectedTrain.branding ? (
                  <div className="mt-1.5 p-2.5 rounded bg-purple-50 border border-purple-200 text-purple-900 space-y-1">
                    <div className="font-bold">{selectedTrain.branding.advertiser}</div>
                    <div className="text-[11px]">{selectedTrain.branding.campaignTitle}</div>
                    <div className="text-[10px] text-purple-700 pt-1 border-t border-purple-200 flex justify-between">
                      <span>Tier: {selectedTrain.branding.tier}</span>
                      <span>₹{selectedTrain.branding.penaltyRatePerHour}/hr SLA Risk</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-400 mt-1 italic">No active commercial wrap.</p>
                )}
              </div>

              {/* Wear Indicators */}
              <div>
                <span className="font-bold text-slate-800">Component Wear Telemetry:</span>
                <div className="space-y-1.5 mt-1.5">
                  <div>
                    <div className="flex justify-between text-[11px] text-slate-600">
                      <span>Bogie Wear</span>
                      <span>{selectedTrain.componentWear.bogieWearPct}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-1.5">
                      <div
                        className="bg-teal-500 h-full rounded-full"
                        style={{ width: `${selectedTrain.componentWear.bogieWearPct}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] text-slate-600">
                      <span>Brake-Pad Wear</span>
                      <span>{selectedTrain.componentWear.brakePadWearPct}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-1.5">
                      <div
                        className="bg-teal-500 h-full rounded-full"
                        style={{ width: `${selectedTrain.componentWear.brakePadWearPct}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Override Button */}
              <button
                onClick={() => onOpenOverrideModal(selectedTrain)}
                className="w-full py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs transition-colors flex items-center justify-center space-x-1.5 shadow-md"
              >
                <span>Manual Supervisor Override for {selectedTrain.rakeNumber}</span>
              </button>
            </div>
          ) : (
            <p className="text-slate-500 text-xs">Click any rake in the yard to view details.</p>
          )}
        </div>
      </div>
    </div>
  );
};
