import React from 'react';
import { Trainset } from '../types';
import {
  TrendingUp,
  Award,
  Gauge,
  History,
  CheckCircle2,
  Brain,
  ShieldCheck
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  Legend
} from 'recharts';

interface AnalyticsViewProps {
  trainsets: Trainset[];
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ trainsets }) => {
  // Mileage Data for Bar Chart
  const mileageData = trainsets.map((t) => ({
    rake: t.rakeNumber,
    mileage: t.currentMileageKm,
    bogieWear: t.componentWear.bogieWearPct,
    brakeWear: t.componentWear.brakePadWearPct,
  }));

  // Branding exposure data
  const brandingData = trainsets
    .filter((t) => t.branding !== null)
    .map((t) => ({
      name: t.branding!.advertiser.split(' ')[0],
      current: t.branding!.currentExposureHours,
      target: t.branding!.targetExposureHours,
      penaltyRisk: t.branding!.penaltyRatePerHour,
    }));

  // Historical ML Accuracy Data (learning loop over 30 days)
  const accuracyHistory = [
    { day: 'Day 1', manualAccuracy: 78, mlAccuracy: 84 },
    { day: 'Day 5', manualAccuracy: 80, mlAccuracy: 88 },
    { day: 'Day 10', manualAccuracy: 81, mlAccuracy: 92 },
    { day: 'Day 15', manualAccuracy: 82, mlAccuracy: 95 },
    { day: 'Day 20', manualAccuracy: 83, mlAccuracy: 97.4 },
    { day: 'Day 25', manualAccuracy: 82, mlAccuracy: 98.6 },
    { day: 'Day 30 (Today)', manualAccuracy: 84, mlAccuracy: 99.2 },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-teal-50 text-teal-700 font-bold text-xs border border-teal-200">
              <Brain className="w-3.5 h-3.5" />
              <span>Machine Learning Continuous Learning Pipeline</span>
            </div>
            <h2 className="text-xl font-heading font-extrabold text-slate-900 mt-1">
              ML Analytics, Closed-Loop Feedback & Audit Trails
            </h2>
            <p className="text-xs text-slate-600 mt-0.5 max-w-2xl">
              Tracks continuous model calibration, supervisor override adjustments, and fleet lifecycle wear equalization.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="px-3 py-1.5 rounded-lg bg-teal-100 text-teal-800 font-bold text-xs">
              Model Calibration Score: 99.2%
            </span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: ML Forecast vs Manual Accuracy Progression */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <div className="font-heading font-bold text-slate-900 text-sm flex items-center space-x-1.5">
              <TrendingUp className="w-4 h-4 text-teal-600" />
              <span>ML Induction Accuracy vs. Manual Baseline (%)</span>
            </div>
            <span className="text-xs text-emerald-700 font-bold">+15.2% Improvement</span>
          </div>
          <div className="h-64 w-full text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={accuracyHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="day" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis domain={[70, 100]} stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Line type="monotone" dataKey="mlAccuracy" stroke="#009999" strokeWidth={3} name="AI Induction Engine" dot={{ r: 4 }} />
                <Line type="monotone" dataKey="manualAccuracy" stroke="#94a3b8" strokeWidth={2} strokeDasharray="4 4" name="Manual Spreadsheet Baseline" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Branding Contract Exposure Compliance */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <div className="font-heading font-bold text-slate-900 text-sm flex items-center space-x-1.5">
              <Award className="w-4 h-4 text-purple-600" />
              <span>Advertiser Wrap Exposure: Current vs Target (Hours)</span>
            </div>
            <span className="text-xs text-purple-700 font-bold">₹3.72L Penalties Saved</span>
          </div>
          <div className="h-64 w-full text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={brandingData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="current" fill="#009999" name="Accumulated Hours" radius={[4, 4, 0, 0]} />
                <Bar dataKey="target" fill="#cbd5e1" name="Contract Target (Hrs)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Chart 3: Fleet Mileage Distribution */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2">
          <div className="font-heading font-bold text-slate-900 text-sm flex items-center space-x-1.5">
            <Gauge className="w-4 h-4 text-teal-600" />
            <span>Fleet Mileage Distribution Across 25 Rakes (km)</span>
          </div>
          <span className="text-xs text-slate-500">Wear Equalization Goal: Target within ±15k km of Mean</span>
        </div>
        <div className="h-64 w-full text-xs">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={mileageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="rake" stroke="#64748b" tick={{ fontSize: 10 }} interval={1} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }} />
              <Bar dataKey="mileage" fill="#14b8a6" name="Total Kilometers (km)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Supervisor Override Audit Trail */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2">
          <div className="font-heading font-bold text-slate-900 text-sm flex items-center space-x-1.5">
            <History className="w-4 h-4 text-teal-600" />
            <span>Supervisor Override Audit Log (Feedback Pipeline)</span>
          </div>
          <span className="text-xs text-slate-400 font-mono">Immutable Compliance Log</span>
        </div>

        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Trainset</th>
                <th className="py-2.5 px-4">AI Recommendation</th>
                <th className="py-2.5 px-4">Supervisor Override</th>
                <th className="py-2.5 px-4">Justification</th>
                <th className="py-2.5 px-4">Officer Name</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr className="hover:bg-slate-50">
                <td className="py-2.5 px-4 text-slate-500">2026-08-28 22:45 IST</td>
                <td className="py-2.5 px-4 font-bold text-slate-900">KM-108</td>
                <td className="py-2.5 px-4 text-emerald-700">Revenue Service</td>
                <td className="py-2.5 px-4 text-amber-700 font-bold">Hot Standby</td>
                <td className="py-2.5 px-4 text-slate-600">Pending late beacon calibration verification</td>
                <td className="py-2.5 px-4 text-slate-800">Shift Lead P. Narayanan</td>
              </tr>
              <tr className="hover:bg-slate-50">
                <td className="py-2.5 px-4 text-slate-500">2026-08-27 22:30 IST</td>
                <td className="py-2.5 px-4 font-bold text-slate-900">KM-125</td>
                <td className="py-2.5 px-4 text-amber-700">Hot Standby</td>
                <td className="py-2.5 px-4 text-teal-700 font-bold">Deep Cleaning Bay</td>
                <td className="py-2.5 px-4 text-slate-600">Bio-sanitation scheduled for VIP inspection</td>
                <td className="py-2.5 px-4 text-slate-800">Depot In-Charge K. Varma</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
