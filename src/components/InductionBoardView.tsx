import React, { useState } from 'react';
import { Trainset, InductionRole } from '../types';
import {
  CheckCircle2,
  AlertTriangle,
  Wrench,
  Sparkles,
  ChevronRight,
  ShieldCheck,
  Zap,
  TrendingUp,
  Search,
  Filter,
  Info,
  Clock,
  Layers,
  Award,
  ArrowRightLeft
} from 'lucide-react';

interface InductionBoardViewProps {
  trainsets: Trainset[];
  onOpenOverrideModal: (train: Trainset) => void;
}

export const InductionBoardView: React.FC<InductionBoardViewProps> = ({
  trainsets,
  onOpenOverrideModal,
}) => {
  const [selectedRoleFilter, setSelectedRoleFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedTrainId, setExpandedTrainId] = useState<string | null>(null);

  const filteredTrainsets = trainsets
    .filter((t) => {
      if (selectedRoleFilter !== 'ALL' && t.assignedRole !== selectedRoleFilter) {
        return false;
      }
      if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase();
        const matchesRake = t.rakeNumber.toLowerCase().includes(query);
        const matchesBrand = t.branding?.advertiser.toLowerCase().includes(query) ?? false;
        const matchesTrack = t.stabling.trackLine.toLowerCase().includes(query);
        return matchesRake || matchesBrand || matchesTrack;
      }
      return true;
    })
    .sort((a, b) => a.rank - b.rank);

  const getRoleBadge = (role: InductionRole) => {
    switch (role) {
      case 'REVENUE_SERVICE':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Dawn Revenue Service</span>
          </span>
        );
      case 'HOT_STANDBY':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
            <Zap className="w-3.5 h-3.5 text-amber-600" />
            <span>Hot Standby Reserve</span>
          </span>
        );
      case 'IBL_MAINTENANCE':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">
            <Wrench className="w-3.5 h-3.5 text-rose-600" />
            <span>IBL Bay Overhaul</span>
          </span>
        );
      case 'CLEANING_BAY':
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-teal-100 text-teal-800 border border-teal-300">
            <Sparkles className="w-3.5 h-3.5 text-teal-600" />
            <span>Deep Sanitization</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner with Decision Summary */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-md bg-teal-50 text-teal-700 font-bold text-xs uppercase tracking-wider border border-teal-200">
                Nightly Decision Cycle 21:00–23:00 IST
              </span>
              <span className="text-xs text-slate-400 font-medium">Auto-reconciled with IBM Maximo & IoT UNS</span>
            </div>
            <h2 className="text-xl font-heading font-extrabold text-slate-900 mt-1">
              Dawn Train Induction Roster (05:30 IST Deployment)
            </h2>
            <p className="text-xs text-slate-600 mt-0.5 max-w-3xl">
              AI multi-objective algorithm has evaluated all 25 trainsets across <strong>Fitness Certs</strong>, <strong>Maximo Job-Cards</strong>, <strong>Branding SLAs</strong>, <strong>Mileage Balancing</strong>, <strong>Cleaning Bays</strong>, and <strong>Stabling Geometry</strong>.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-emerald-50/70 border border-emerald-200/80 rounded-xl p-3 text-center">
              <div className="text-xs font-semibold text-emerald-700">Dawn Revenue</div>
              <div className="text-2xl font-extrabold text-emerald-900 mt-0.5">18</div>
              <div className="text-[10px] text-emerald-600">Peak Frequency Ready</div>
            </div>
            <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl p-3 text-center">
              <div className="text-xs font-semibold text-amber-700">Hot Standby</div>
              <div className="text-2xl font-extrabold text-amber-900 mt-0.5">4</div>
              <div className="text-[10px] text-amber-600">3-min Rapid Injection</div>
            </div>
            <div className="bg-rose-50/70 border border-rose-200/80 rounded-xl p-3 text-center">
              <div className="text-xs font-semibold text-rose-700">IBL Maintenance</div>
              <div className="text-2xl font-extrabold text-rose-900 mt-0.5">2</div>
              <div className="text-[10px] text-rose-600">Overhaul Holdback</div>
            </div>
            <div className="bg-teal-50/70 border border-teal-200/80 rounded-xl p-3 text-center">
              <div className="text-xs font-semibold text-teal-700">Deep Wash</div>
              <div className="text-2xl font-extrabold text-teal-900 mt-0.5">1</div>
              <div className="text-[10px] text-teal-600">Auto Washing Plant</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-sm">
        {/* Role Filters */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs font-semibold text-slate-500 mr-1 flex items-center">
            <Filter className="w-3.5 h-3.5 mr-1" /> Filter:
          </span>
          {[
            { id: 'ALL', label: 'All 25 Rakes' },
            { id: 'REVENUE_SERVICE', label: 'Revenue (18)' },
            { id: 'HOT_STANDBY', label: 'Standby (4)' },
            { id: 'IBL_MAINTENANCE', label: 'IBL (2)' },
            { id: 'CLEANING_BAY', label: 'Cleaning (1)' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedRoleFilter(tab.id)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                selectedRoleFilter === tab.id
                  ? 'bg-teal-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search Rake (e.g. KM-105, Federal Bank, ST-04)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500/40 w-full sm:w-72"
          />
        </div>
      </div>

      {/* Main Induction Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-900 text-slate-200 font-heading text-[11px] uppercase tracking-wider">
                <th className="py-3 px-4 text-center">Rank</th>
                <th className="py-3 px-4">Trainset</th>
                <th className="py-3 px-4">AI Assigned Role</th>
                <th className="py-3 px-4">Readiness Score</th>
                <th className="py-3 px-4">Tri-Dept Fitness</th>
                <th className="py-3 px-4">Maximo Work Orders</th>
                <th className="py-3 px-4">Branding SLA</th>
                <th className="py-3 px-4">Mileage & Wear</th>
                <th className="py-3 px-4">Stabling & Turnout</th>
                <th className="py-3 px-4 text-right">Supervisor Override</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredTrainsets.map((train) => {
                const isExpanded = expandedTrainId === train.id;
                const openCriticalWOs = train.jobCards.filter((w) => w.status === 'OPEN' && (w.severity === 'CRITICAL' || w.severity === 'HIGH'));
                const certs = train.fitnessCertificates;
                const hasCertIssue = certs.rollingStock.status !== 'VALID' || certs.signalling.status !== 'VALID' || certs.telecom.status !== 'VALID';

                return (
                  <React.Fragment key={train.id}>
                    <tr
                      className={`hover:bg-teal-50/40 transition-colors ${
                        train.isOverridden ? 'bg-amber-50/40' : ''
                      } ${train.assignedRole === 'IBL_MAINTENANCE' ? 'bg-rose-50/20' : ''}`}
                    >
                      {/* Rank */}
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs ${
                            train.rank <= 5
                              ? 'bg-teal-600 text-white shadow-sm'
                              : train.rank <= 18
                              ? 'bg-slate-100 text-slate-700'
                              : train.rank <= 22
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-rose-100 text-rose-800'
                          }`}
                        >
                          {train.rank}
                        </span>
                      </td>

                      {/* Trainset */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => setExpandedTrainId(isExpanded ? null : train.id)}
                            className="p-1 rounded hover:bg-slate-200 text-slate-500"
                            title="Toggle Explainable AI Details"
                          >
                            <ChevronRight
                              className={`w-3.5 h-3.5 transform transition-transform ${
                                isExpanded ? 'rotate-90 text-teal-600' : ''
                              }`}
                            />
                          </button>
                          <div>
                            <div className="font-heading font-extrabold text-slate-900 text-sm flex items-center space-x-1.5">
                              <span>{train.rakeNumber}</span>
                              {train.isOverridden && (
                                <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-500 text-white font-bold">
                                  OVERRIDDEN
                                </span>
                              )}
                            </div>
                            <span className="text-[11px] text-slate-400">4-Car Alstom Metropolis</span>
                          </div>
                        </div>
                      </td>

                      {/* AI Assigned Role */}
                      <td className="py-3.5 px-4">
                        {getRoleBadge(train.assignedRole)}
                      </td>

                      {/* Readiness Score */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-16 bg-slate-200 rounded-full h-2 overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                train.overallReadinessScore >= 95
                                  ? 'bg-teal-500'
                                  : train.overallReadinessScore >= 85
                                  ? 'bg-emerald-500'
                                  : train.overallReadinessScore >= 70
                                  ? 'bg-amber-500'
                                  : 'bg-rose-500'
                              }`}
                              style={{ width: `${train.overallReadinessScore}%` }}
                            ></div>
                          </div>
                          <span className="font-bold text-slate-800 text-xs">{train.overallReadinessScore}%</span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          Conf: {train.reasoning.confidenceScorePct}%
                        </div>
                      </td>

                      {/* Tri-Dept Fitness */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center space-x-1">
                          <span
                            title={`Rolling Stock: ${certs.rollingStock.status} (Exp: ${certs.rollingStock.validUntil})`}
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              certs.rollingStock.status === 'VALID'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-rose-100 text-rose-800 animate-pulse'
                            }`}
                          >
                            RS
                          </span>
                          <span
                            title={`Signalling: ${certs.signalling.status} (Exp: ${certs.signalling.validUntil})`}
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              certs.signalling.status === 'VALID'
                                ? 'bg-emerald-100 text-emerald-800'
                                : certs.signalling.status === 'EXPIRING_SOON'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-rose-100 text-rose-800'
                            }`}
                          >
                            SIG
                          </span>
                          <span
                            title={`Telecom: ${certs.telecom.status} (Exp: ${certs.telecom.validUntil})`}
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              certs.telecom.status === 'VALID'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-rose-100 text-rose-800 animate-pulse'
                            }`}
                          >
                            TEL
                          </span>
                        </div>
                      </td>

                      {/* Maximo Work Orders */}
                      <td className="py-3.5 px-4">
                        {train.jobCards.length === 0 ? (
                          <span className="inline-flex items-center space-x-1 text-emerald-600 font-semibold text-[11px]">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>0 Open</span>
                          </span>
                        ) : openCriticalWOs.length > 0 ? (
                          <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded bg-rose-100 text-rose-800 font-bold text-[10px]">
                            <AlertTriangle className="w-3 h-3" />
                            <span>{openCriticalWOs.length} Critical Open</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-semibold text-[10px]">
                            <span>{train.jobCards.filter((w) => w.status !== 'CLOSED').length} Minor Open</span>
                          </span>
                        )}
                      </td>

                      {/* Branding SLA */}
                      <td className="py-3.5 px-4">
                        {train.branding ? (
                          <div>
                            <div className="font-semibold text-slate-800 flex items-center space-x-1">
                              <span className="truncate max-w-[120px]">{train.branding.advertiser}</span>
                              <span
                                className={`text-[9px] px-1 rounded font-bold ${
                                  train.branding.tier === 'PLATINUM'
                                    ? 'bg-purple-100 text-purple-800'
                                    : train.branding.tier === 'GOLD'
                                    ? 'bg-amber-100 text-amber-800'
                                    : 'bg-slate-100 text-slate-700'
                                }`}
                              >
                                {train.branding.tier}
                              </span>
                            </div>
                            <div className="text-[10px] text-slate-500">
                              {train.branding.currentExposureHours}/{train.branding.targetExposureHours}h (₹{train.branding.penaltyRatePerHour}/h)
                            </div>
                          </div>
                        ) : (
                          <span className="text-slate-400 text-[11px]">Unwrapped Standard</span>
                        )}
                      </td>

                      {/* Mileage & Wear */}
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-800">{train.currentMileageKm.toLocaleString()} km</div>
                        <div className="flex items-center space-x-2 text-[10px] text-slate-500 mt-0.5">
                          <span>Bogie: <strong className={train.componentWear.bogieWearPct > 70 ? 'text-rose-600' : 'text-slate-700'}>{train.componentWear.bogieWearPct}%</strong></span>
                          <span>Brake: <strong className={train.componentWear.brakePadWearPct > 70 ? 'text-rose-600' : 'text-slate-700'}>{train.componentWear.brakePadWearPct}%</strong></span>
                        </div>
                      </td>

                      {/* Stabling & Turnout */}
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-800 flex items-center space-x-1">
                          <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-mono font-bold">
                            {train.stabling.trackLine}
                          </span>
                          <span className="text-[10px] text-slate-500">Pos {train.stabling.positionDepth}</span>
                        </div>
                        <div className="text-[10px] text-teal-700 mt-0.5">
                          Turnout: {train.stabling.turnoutTimeMins}m ({train.stabling.shuntingTurnsNeeded} moves)
                        </div>
                      </td>

                      {/* Supervisor Override */}
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => onOpenOverrideModal(train)}
                          className="px-2.5 py-1 rounded bg-slate-100 hover:bg-teal-100 hover:text-teal-800 text-slate-700 font-semibold text-[11px] border border-slate-300 transition-colors inline-flex items-center space-x-1"
                        >
                          <ArrowRightLeft className="w-3 h-3" />
                          <span>Override</span>
                        </button>
                      </td>
                    </tr>

                    {/* Expandable Explainable AI (XAI) Row */}
                    {isExpanded && (
                      <tr className="bg-slate-50 border-b border-slate-200">
                        <td colSpan={10} className="p-4">
                          <div className="bg-white rounded-xl p-4 border border-teal-200 shadow-sm space-y-3">
                            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                              <div className="flex items-center space-x-2">
                                <Info className="w-4 h-4 text-teal-600" />
                                <span className="font-heading font-bold text-slate-900 text-xs">
                                  Explainable AI (XAI) Decision Rationale for {train.rakeNumber}
                                </span>
                              </div>
                              {train.reasoning.penaltyAvertedINR > 0 && (
                                <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                                  ₹{train.reasoning.penaltyAvertedINR.toLocaleString()} Advertiser SLA Penalty Averted
                                </span>
                              )}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                              {/* Positive Reinforcing Factors */}
                              <div className="bg-emerald-50/60 p-3 rounded-lg border border-emerald-100 space-y-1">
                                <div className="font-bold text-emerald-900 flex items-center space-x-1 mb-1.5">
                                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                                  <span>Optimization Drivers (+Score):</span>
                                </div>
                                <ul className="list-disc list-inside text-emerald-800 space-y-1">
                                  {train.reasoning.positiveFactors.map((factor, idx) => (
                                    <li key={idx}>{factor}</li>
                                  ))}
                                </ul>
                              </div>

                              {/* Risk Factors or Constraint Violations */}
                              <div className="bg-rose-50/60 p-3 rounded-lg border border-rose-100 space-y-1">
                                <div className="font-bold text-rose-900 flex items-center space-x-1 mb-1.5">
                                  <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                                  <span>Identified Constraints & Risks (-Score):</span>
                                </div>
                                {train.reasoning.riskFactors.length === 0 ? (
                                  <p className="text-slate-500 italic">No operational bottlenecks detected.</p>
                                ) : (
                                  <ul className="list-disc list-inside text-rose-800 space-y-1">
                                    {train.reasoning.riskFactors.map((factor, idx) => (
                                      <li key={idx}>{factor}</li>
                                    ))}
                                  </ul>
                                )}
                              </div>
                            </div>

                            {/* Job Cards Details if any */}
                            {train.jobCards.length > 0 && (
                              <div className="mt-2 pt-2 border-t border-slate-100">
                                <span className="font-semibold text-slate-700 text-xs">Linked IBM Maximo Work Orders:</span>
                                <div className="mt-1.5 space-y-1">
                                  {train.jobCards.map((card) => (
                                    <div
                                      key={card.id}
                                      className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-200 text-xs"
                                    >
                                      <div className="flex items-center space-x-2">
                                        <span className="font-mono font-bold text-teal-700">{card.workOrderNumber}</span>
                                        <span className="text-slate-800">{card.title}</span>
                                        <span className="text-slate-400">({card.subsystem})</span>
                                      </div>
                                      <div className="flex items-center space-x-2">
                                        <span className="text-slate-500">Tech: {card.technicianAssigned} (~{card.estimatedFixHours}h)</span>
                                        <span
                                          className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                            card.status === 'CLOSED'
                                              ? 'bg-emerald-100 text-emerald-800'
                                              : card.severity === 'CRITICAL'
                                              ? 'bg-rose-600 text-white'
                                              : 'bg-amber-100 text-amber-800'
                                          }`}
                                        >
                                          {card.status} - {card.severity}
                                        </span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Override Audit if present */}
                            {train.isOverridden && (
                              <div className="bg-amber-100/70 p-2.5 rounded-lg border border-amber-300 text-amber-900 text-xs">
                                <strong>Supervisor Manual Override Logged:</strong> "{train.overrideJustification}" by <em>{train.supervisorName || 'Shift Lead'}</em>. (Captured in ML retraining feedback pipeline).
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
