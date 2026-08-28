import React, { useState } from 'react';
import { Trainset } from '../types';
import {
  ShieldCheck,
  Wrench,
  Award,
  Gauge,
  Sparkles,
  Layers,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Coins,
  TrendingDown,
  Info
} from 'lucide-react';

interface VariableMatrixViewProps {
  trainsets: Trainset[];
}

export const VariableMatrixView: React.FC<VariableMatrixViewProps> = ({ trainsets }) => {
  const [activeSubTab, setActiveSubTab] = useState<number>(1);

  return (
    <div className="space-y-6">
      {/* Overview Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-teal-50 text-teal-700 font-bold text-xs border border-teal-200">
              <Layers className="w-3.5 h-3.5" />
              <span>Multi-Source Ingestion & Constraint Engine</span>
            </div>
            <h2 className="text-xl font-heading font-extrabold text-slate-900 mt-1">
              6 Inter-Dependent Decision Variables
            </h2>
            <p className="text-xs text-slate-600 mt-0.5 max-w-2xl">
              Inspect granular departmental inputs that replace siloed spreadsheets, manual logbooks, and WhatsApp groups.
            </p>
          </div>

          {/* 6 Tabs Switcher */}
          <div className="flex flex-wrap gap-1.5 bg-slate-100 p-1.5 rounded-xl border border-slate-200">
            {[
              { id: 1, label: '1. Fitness Certs', icon: ShieldCheck },
              { id: 2, label: '2. Maximo Job-Cards', icon: Wrench },
              { id: 3, label: '3. Branding SLAs', icon: Award },
              { id: 4, label: '4. Mileage Balancing', icon: Gauge },
              { id: 5, label: '5. Cleaning Slots', icon: Sparkles },
              { id: 6, label: '6. Stabling Geometry', icon: Layers },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveSubTab(tab.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeSubTab === tab.id
                      ? 'bg-teal-600 text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Sub-Tab 1: Fitness Certificates */}
      {activeSubTab === 1 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-heading font-bold text-slate-900 text-base flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-teal-600" />
                <span>Tri-Department Fitness Clearances (Rolling-Stock, Signalling, Telecom)</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Every inducted trainset MUST have 3 green clearances. Missing even one forces unscheduled withdrawal, eroding the 99.5% Punctuality KPI.
              </p>
            </div>
            <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 font-bold text-xs border border-emerald-300">
              Hard Constraint Enforced
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900 text-slate-200 uppercase font-heading text-[11px]">
                  <th className="py-2.5 px-4">Trainset</th>
                  <th className="py-2.5 px-4">Rolling-Stock Dept</th>
                  <th className="py-2.5 px-4">Signalling Dept</th>
                  <th className="py-2.5 px-4">Telecom Dept</th>
                  <th className="py-2.5 px-4">Clearance Verdict</th>
                  <th className="py-2.5 px-4">Notes / Remarks</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {trainsets.map((train) => {
                  const certs = train.fitnessCertificates;
                  const allValid =
                    certs.rollingStock.status === 'VALID' &&
                    certs.signalling.status === 'VALID' &&
                    certs.telecom.status === 'VALID';

                  return (
                    <tr key={train.id} className="hover:bg-teal-50/30">
                      <td className="py-2.5 px-4 font-bold text-slate-900">{train.rakeNumber}</td>
                      <td className="py-2.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded font-semibold text-[11px] ${
                            certs.rollingStock.status === 'VALID'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-rose-100 text-rose-800 font-bold'
                          }`}
                        >
                          {certs.rollingStock.status} (until {certs.rollingStock.validUntil.split(' ')[1]})
                        </span>
                      </td>
                      <td className="py-2.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded font-semibold text-[11px] ${
                            certs.signalling.status === 'VALID'
                              ? 'bg-emerald-100 text-emerald-800'
                              : certs.signalling.status === 'EXPIRING_SOON'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-rose-100 text-rose-800'
                          }`}
                        >
                          {certs.signalling.status}
                        </span>
                      </td>
                      <td className="py-2.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded font-semibold text-[11px] ${
                            certs.telecom.status === 'VALID'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-rose-100 text-rose-800'
                          }`}
                        >
                          {certs.telecom.status}
                        </span>
                      </td>
                      <td className="py-2.5 px-4">
                        {allValid ? (
                          <span className="inline-flex items-center space-x-1 text-emerald-700 font-bold text-[11px]">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            <span>100% Fit</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 text-rose-700 font-bold text-[11px]">
                            <AlertTriangle className="w-3.5 h-3.5 text-rose-600" />
                            <span>REJECTED (Missing Clearances)</span>
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-4 text-slate-500">
                        {certs.rollingStock.notes || certs.signalling.notes || 'All checks passed'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sub-Tab 2: IBM Maximo Job-Cards */}
      {activeSubTab === 2 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-heading font-bold text-slate-900 text-base flex items-center space-x-2">
                <Wrench className="w-5 h-5 text-teal-600" />
                <span>IBM Maximo Work Orders & Defect Logbook</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Ingested in near-real-time from Maximo REST API / CSV exports. Open Critical/High safety work orders trigger automated quarantine.
              </p>
            </div>
            <span className="px-3 py-1 rounded-full bg-slate-900 text-teal-300 font-mono text-xs">
              Live Maximo Sync: Active
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {trainsets
              .filter((t) => t.jobCards.length > 0)
              .map((train) => (
                <div key={train.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-heading font-extrabold text-slate-900 text-sm">{train.rakeNumber}</span>
                    <span className="px-2 py-0.5 rounded bg-slate-200 text-slate-700 text-xs font-semibold">
                      {train.jobCards.length} Work Orders
                    </span>
                  </div>
                  <div className="space-y-2">
                    {train.jobCards.map((card) => (
                      <div key={card.id} className="p-2.5 rounded-lg bg-white border border-slate-200 text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-bold text-teal-700">{card.workOrderNumber}</span>
                          <span
                            className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                              card.severity === 'CRITICAL'
                                ? 'bg-rose-600 text-white'
                                : card.severity === 'HIGH'
                                ? 'bg-rose-100 text-rose-800'
                                : 'bg-amber-100 text-amber-800'
                            }`}
                          >
                            {card.severity}
                          </span>
                        </div>
                        <p className="font-medium text-slate-800">{card.title}</p>
                        <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-100">
                          <span>Subsystem: {card.subsystem}</span>
                          <span>Est: {card.estimatedFixHours}h</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Sub-Tab 3: Branding Priorities */}
      {activeSubTab === 3 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-heading font-bold text-slate-900 text-base flex items-center space-x-2">
                <Award className="w-5 h-5 text-teal-600" />
                <span>Advertiser Branding Contracts & Exposure Commitments</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Contractual advertiser wrap exposure hours. Minimizes SLA breach penalty exposure for KMRL.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-1 rounded-md bg-purple-100 text-purple-800 font-bold text-xs">
                Total Penalties Averted: ₹3,72,500
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {trainsets
              .filter((t) => t.branding !== null)
              .map((train) => {
                const brand = train.branding!;
                const progressPct = Math.min(100, Math.round((brand.currentExposureHours / brand.targetExposureHours) * 100));
                const deficitHours = Math.max(0, brand.targetExposureHours - brand.currentExposureHours);

                return (
                  <div key={train.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/80 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-heading font-extrabold text-slate-900 text-sm">{train.rakeNumber}</span>
                        <span
                          className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                            brand.tier === 'PLATINUM'
                              ? 'bg-purple-100 text-purple-800 border border-purple-300'
                              : 'bg-amber-100 text-amber-800 border border-amber-300'
                          }`}
                        >
                          {brand.tier}
                        </span>
                      </div>
                      <span className="text-xs font-bold text-teal-700">₹{brand.penaltyRatePerHour.toLocaleString()}/hr penalty</span>
                    </div>

                    <div>
                      <div className="font-bold text-slate-800 text-sm">{brand.advertiser}</div>
                      <div className="text-xs text-slate-500">{brand.campaignTitle}</div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-slate-600">
                        <span>Accumulated Exposure:</span>
                        <span className="font-bold">{brand.currentExposureHours} / {brand.targetExposureHours} hrs ({progressPct}%)</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            progressPct >= 90 ? 'bg-emerald-500' : progressPct >= 75 ? 'bg-teal-500' : 'bg-amber-500'
                          }`}
                          style={{ width: `${progressPct}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-200/80">
                      <span className="text-slate-500">Deficit: <strong className="text-rose-600">{deficitHours} hrs</strong></span>
                      <span className="text-teal-700 font-semibold">Priority: {brand.priorityScore}/10</span>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* Sub-Tab 4: Mileage Balancing */}
      {activeSubTab === 4 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-heading font-bold text-slate-900 text-base flex items-center space-x-2">
                <Gauge className="w-5 h-5 text-teal-600" />
                <span>Mileage Balancing & Component Wear Equalization</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Dynamic kilometer allocation equalizes bogie, brake-pad, and HVAC compressor fatigue across all 25 rakes.
              </p>
            </div>
            <span className="text-xs font-semibold text-slate-700 bg-slate-100 px-3 py-1 rounded-full">
              Fleet Average: 189,450 km
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900 text-slate-200 uppercase font-heading text-[11px]">
                  <th className="py-2.5 px-4">Trainset</th>
                  <th className="py-2.5 px-4">Odometer (km)</th>
                  <th className="py-2.5 px-4">Today's Target (km)</th>
                  <th className="py-2.5 px-4">Bogie Wear %</th>
                  <th className="py-2.5 px-4">Brake-Pad Wear %</th>
                  <th className="py-2.5 px-4">HVAC Health Score</th>
                  <th className="py-2.5 px-4">Wear State</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {trainsets.map((train) => (
                  <tr key={train.id} className="hover:bg-teal-50/30">
                    <td className="py-2.5 px-4 font-bold text-slate-900">{train.rakeNumber}</td>
                    <td className="py-2.5 px-4 font-semibold text-slate-800">{train.currentMileageKm.toLocaleString()} km</td>
                    <td className="py-2.5 px-4 font-bold text-teal-700">{train.targetDailyMileageKm} km</td>
                    <td className="py-2.5 px-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-200 rounded-full h-1.5">
                          <div
                            className={`h-full rounded-full ${train.componentWear.bogieWearPct > 70 ? 'bg-rose-500' : 'bg-teal-500'}`}
                            style={{ width: `${train.componentWear.bogieWearPct}%` }}
                          ></div>
                        </div>
                        <span>{train.componentWear.bogieWearPct}%</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-200 rounded-full h-1.5">
                          <div
                            className={`h-full rounded-full ${train.componentWear.brakePadWearPct > 70 ? 'bg-rose-500' : 'bg-teal-500'}`}
                            style={{ width: `${train.componentWear.brakePadWearPct}%` }}
                          ></div>
                        </div>
                        <span>{train.componentWear.brakePadWearPct}%</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-4 font-semibold text-emerald-700">{train.componentWear.hvacHealthScore}/100</td>
                    <td className="py-2.5 px-4">
                      {train.componentWear.bogieWearPct > 70 || train.componentWear.brakePadWearPct > 70 ? (
                        <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-bold text-[10px]">
                          Wear Limit Exceeded
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold text-[10px]">
                          Balanced
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sub-Tab 5: Cleaning & Detailing Slots */}
      {activeSubTab === 5 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-heading font-bold text-slate-900 text-base flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-teal-600" />
                <span>Cleaning & Detailing Slots (Automatic Wash Plant & Bay Sanitation)</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Manpower allocation (Housekeeping shift teams) and track occupancy for deep bio-chemical interior disinfection.
              </p>
            </div>
            <span className="px-3 py-1 rounded-full bg-teal-100 text-teal-800 font-bold text-xs">
              Muttom Wash Plant Active
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {trainsets.map((train) => (
              <div
                key={train.id}
                className={`p-4 rounded-xl border text-xs space-y-2 ${
                  train.assignedRole === 'CLEANING_BAY'
                    ? 'bg-teal-50 border-teal-300 ring-2 ring-teal-500/20'
                    : 'bg-white border-slate-200'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-heading font-extrabold text-slate-900 text-sm">{train.rakeNumber}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      train.cleaning.deepCleaningRequired ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                    }`}
                  >
                    {train.cleaning.deepCleaningRequired ? 'Deep Sanitization Required' : 'Sanitized & Clean'}
                  </span>
                </div>
                <div className="space-y-1 text-slate-600">
                  <div className="flex justify-between">
                    <span>Last Cleaned:</span>
                    <strong className="text-slate-800">{train.cleaning.lastCleanedDate}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Assigned Bay:</span>
                    <strong className="text-slate-800">{train.cleaning.assignedBay}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Manpower Team:</span>
                    <strong className="text-slate-800">{train.cleaning.manpowerAllocated} Crew Members</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sub-Tab 6: Stabling Geometry & Shunting Minimization */}
      {activeSubTab === 6 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-heading font-bold text-slate-900 text-base flex items-center space-x-2">
                <Layers className="w-5 h-5 text-teal-600" />
                <span>Stabling Geometry & Turn-Out Sequencing (Muttom Depot 12 Lines)</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Physical track bay positions that minimize night-time shunting movements and morning turn-out latency to Aluva/SN Junction.
              </p>
            </div>
            <span className="px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 font-bold text-xs">
              -34% Shunting Energy Saved
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {trainsets.map((train) => (
              <div key={train.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-heading font-extrabold text-slate-900 text-sm">{train.rakeNumber}</span>
                  <span className="px-2 py-0.5 rounded bg-slate-200 font-mono font-bold text-teal-800 text-xs">
                    {train.stabling.trackLine}
                  </span>
                </div>
                <div className="space-y-1 text-slate-600">
                  <div className="flex justify-between">
                    <span>Lane Depth:</span>
                    <strong className="text-slate-800">Position {train.stabling.positionDepth}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Shunting Moves:</span>
                    <strong className={train.stabling.shuntingTurnsNeeded === 0 ? 'text-emerald-700' : 'text-amber-700'}>
                      {train.stabling.shuntingTurnsNeeded} Shunting Turn(s)
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span>Morning Turnout Time:</span>
                    <strong className="text-teal-700">{train.stabling.turnoutTimeMins} mins</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
