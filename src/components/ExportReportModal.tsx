import React from 'react';
import { Trainset } from '../types';
import { X, Printer, Download, CheckCircle2, ShieldCheck, Building2 } from 'lucide-react';

interface ExportReportModalProps {
  trainsets: Trainset[];
  onClose: () => void;
}

export const ExportReportModal: React.FC<ExportReportModalProps> = ({ trainsets, onClose }) => {
  const handlePrint = () => {
    window.print();
  };

  const revenueTrains = trainsets.filter((t) => t.assignedRole === 'REVENUE_SERVICE');
  const standbyTrains = trainsets.filter((t) => t.assignedRole === 'HOT_STANDBY');
  const iblTrains = trainsets.filter((t) => t.assignedRole === 'IBL_MAINTENANCE');
  const washTrains = trainsets.filter((t) => t.assignedRole === 'CLEANING_BAY');

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-fade-in">
        {/* Modal Actions Bar (Not printed) */}
        <div className="bg-slate-900 text-white p-4 flex items-center justify-between print:hidden">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-teal-400" />
            <span className="font-heading font-extrabold text-base">
              KMRL Official Daily Induction Master Sheet
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="px-3.5 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs flex items-center space-x-1.5 shadow-md"
            >
              <Printer className="w-4 h-4" />
              <span>Print / Save PDF</span>
            </button>
            <button onClick={onClose} className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Document Body */}
        <div className="p-8 overflow-y-auto space-y-6 text-xs text-slate-800 font-sans" id="printable-sheet">
          {/* Official Letterhead */}
          <div className="border-b-2 border-teal-800 pb-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-xl bg-slate-900 flex items-center justify-center p-1">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="-258 191.7 441.7 178.3" className="w-full h-full">
                  <path fill="#009999" d="M-170.9,315.8c-15.5,15.3-31,30.7-46.5,46c-6.5,6.5-14.1,9.2-23.2,6.8c-9.6-2.6-16.4-11.3-16.4-21.4c-0.1-44.1-0.1-88.2,0-132.4c0-12.6,10-22.2,22.8-22.2c12.5,0,22.3,9.4,22.4,22c0.1,23.5,0.1,47,0.1,70.5c0,1.8,0,3.5,0,6.5c2.1-1.9,3.4-2.9,4.5-4c28.7-28.9,57.6-57.7,86.5-86.6c11.4-11.3,24.2-11.4,35.5-0.2c15,14.9,29.9,29.9,44.9,44.8c1.2,1.2,2.5,2.1,3.8,3.1c10.6,10.6,21.1,21.2,31.7,31.8c9.7,9.8,19.3,19.7,29,29.5c6.6,6.6,13.2,13.1,19.8,19.7c9.5,9.5,10,23.4,1,32.6c-9.3,9.5-23.2,9.5-33-0.2c-14.8-14.7-29.5-29.4-44.2-44.1c-1.7-1.7-3.8-3.2-5.6-4.8c-2.6-2.9-5.1-6-7.9-8.7c-7.9-7.7-15.9-15.3-23.8-23c-6.1-6.3-12.1-12.6-18.2-19c-4.9-5.1-9.6-10.4-13.8-14.8c-10.5,10-20,19-29.5,28.1c-0.7,0.6-1.3,1.3-2,1.9c-2,2-4,4-6.1,6.1c-8.8,8.8-17.6,17.6-26.4,26.4c-1.1,1.1-2.2,2.2-3.3,3.2C-169.3,314.2-170.1,315-170.9,315.8z" />
                  <path fill="#16DDDD" d="M-4.8,280.6c-10.6-10.6-21.1-21.2-31.7-31.8c16.9-17,33.7-34.1,50.9-50.8c7.9-7.7,21.7-7.1,30,1c21.1,20.8,42,41.8,63,62.7c22.7,22.7,45.5,45.4,68.2,68.1c6.9,6.8,9.3,15,6.4,24.2c-2.9,8.8-9.4,14.1-18.6,15.3c-8,1.1-14.5-2-20.2-7.7c-21-21.1-42.1-42.2-63.2-63.2c-15.8-15.8-31.6-31.5-47.4-47.2c-1.1-1.1-2.5-2.1-4-3.3C17.2,258.9,6.2,269.7-4.8,280.6z" />
                  <path fill="#16DDDD" d="M-69.5,281.6c7.9,7.7,15.9,15.2,23.8,23c2.8,2.7,5.3,5.8,7.9,8.7C-49.2,324.9-60.6,336.5-72,348c-4.5,4.6-9.1,9.2-13.7,13.8c-10.1,10.2-23.7,10.3-34.1,0.3c-2.3-2.2-4.5-4.4-6.8-6.6c-1.1-1-2.2-2-3.3-3l-0.1,0.2l0.1-0.2c-1.7-1.7-3.3-3.3-5-5l-0.2,0.1l0.2-0.1c-1.4-1.5-2.9-3.1-4.3-4.6l-0.1-0.1c-2.9-2.8-5.8-5.5-8.6-8.3c-3.1-3.1-6.2-6.3-9.3-9.4c-1-1.1-2.1-2.2-3.1-3.3c-0.7-0.7-1.3-1.3-2-2c-0.1-0.7-0.3-1.4-0.4-2.1c8.9-9,17.9-17.9,26.8-26.9c0.6-0.6,1.3-1.2,1.9-1.8c0.4-0.4,0.8-0.8,1.2-1.3c0.3-0.1,0.5-0.2,0.7-0.5c0.7,0,1.3,0,2,0.1c8.9,9.1,17.8,18.2,27.6,28.2C-90.9,303.7-80.2,292.6-69.5,281.6z" />
                </svg>
              </div>
              <div>
                <h1 className="font-heading font-extrabold text-lg text-slate-900 tracking-wide">
                  KOCHI METRO RAIL LIMITED
                </h1>
                <p className="text-[11px] text-teal-800 font-semibold tracking-wider">
                  OPERATIONS & DEPOT MANAGEMENT DIVISION • MUTTOM DEPOT
                </p>
              </div>
            </div>

            <div className="text-right">
              <div className="font-mono font-bold text-xs text-slate-900">DOC REF: KMRL/OPS/IND-2026/08/29</div>
              <div className="text-[10px] text-slate-500">Generated: 2026-08-29 22:50 IST</div>
              <div className="text-[10px] text-teal-700 font-bold">Dawn Deployment: 05:30 IST</div>
            </div>
          </div>

          {/* Executive Summary */}
          <div className="grid grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200">
            <div>
              <div className="text-[10px] text-slate-500">Revenue Rollout:</div>
              <div className="text-sm font-bold text-emerald-800">{revenueTrains.length} Trainsets</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500">Hot Standby Buffer:</div>
              <div className="text-sm font-bold text-amber-800">{standbyTrains.length} Trainsets</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500">IBL Maintenance:</div>
              <div className="text-sm font-bold text-rose-800">{iblTrains.length} Trainsets</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500">Automatic Wash Plant:</div>
              <div className="text-sm font-bold text-teal-800">{washTrains.length} Trainsets</div>
            </div>
          </div>

          {/* Section 1: Dawn Revenue Service Table */}
          <div className="space-y-2">
            <h3 className="font-heading font-bold text-slate-900 text-xs uppercase tracking-wider text-teal-900 flex items-center space-x-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-teal-700" />
              <span>1. Dawn Revenue Service Induction List (18 Rakes - 05:30 IST)</span>
            </h3>
            <table className="w-full text-left border-collapse border border-slate-300">
              <thead>
                <tr className="bg-slate-100 font-semibold text-[10px] text-slate-700">
                  <th className="border border-slate-300 p-1.5 text-center">Slot</th>
                  <th className="border border-slate-300 p-1.5">Rake ID</th>
                  <th className="border border-slate-300 p-1.5">Stabling Line</th>
                  <th className="border border-slate-300 p-1.5">Branding Wrap Partner</th>
                  <th className="border border-slate-300 p-1.5">Target Daily km</th>
                  <th className="border border-slate-300 p-1.5">Turnout Latency</th>
                  <th className="border border-slate-300 p-1.5">Tri-Dept Clearance</th>
                </tr>
              </thead>
              <tbody>
                {revenueTrains.map((train, idx) => (
                  <tr key={train.id} className="text-[10px]">
                    <td className="border border-slate-300 p-1 text-center font-bold">{idx + 1}</td>
                    <td className="border border-slate-300 p-1 font-bold text-slate-900">{train.rakeNumber}</td>
                    <td className="border border-slate-300 p-1 font-mono">{train.stabling.trackLine} (Pos {train.stabling.positionDepth})</td>
                    <td className="border border-slate-300 p-1 font-semibold">{train.branding?.advertiser || 'Standard Clean'}</td>
                    <td className="border border-slate-300 p-1">{train.targetDailyMileageKm} km</td>
                    <td className="border border-slate-300 p-1">{train.stabling.turnoutTimeMins} mins</td>
                    <td className="border border-slate-300 p-1 text-emerald-700 font-bold">100% Certified</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Section 2: Hot Standby & Maintenance */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <h4 className="font-heading font-bold text-xs text-amber-900">2. Hot Standby Reserves (4 Rakes)</h4>
              <table className="w-full text-left border-collapse border border-slate-300 text-[10px]">
                <thead>
                  <tr className="bg-slate-100 font-semibold">
                    <th className="border border-slate-300 p-1">Rake ID</th>
                    <th className="border border-slate-300 p-1">Siding Track</th>
                    <th className="border border-slate-300 p-1">Response Time</th>
                  </tr>
                </thead>
                <tbody>
                  {standbyTrains.map((t) => (
                    <tr key={t.id}>
                      <td className="border border-slate-300 p-1 font-bold">{t.rakeNumber}</td>
                      <td className="border border-slate-300 p-1 font-mono">{t.stabling.trackLine}</td>
                      <td className="border border-slate-300 p-1 text-amber-700 font-semibold">&lt; 4.0 mins rapid turn-out</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="space-y-1.5">
              <h4 className="font-heading font-bold text-xs text-rose-900">3. IBL Bay Maintenance Holdback (2 Rakes)</h4>
              <table className="w-full text-left border-collapse border border-slate-300 text-[10px]">
                <thead>
                  <tr className="bg-slate-100 font-semibold">
                    <th className="border border-slate-300 p-1">Rake ID</th>
                    <th className="border border-slate-300 p-1">Bay</th>
                    <th className="border border-slate-300 p-1">Work Order Defect</th>
                  </tr>
                </thead>
                <tbody>
                  {iblTrains.map((t) => (
                    <tr key={t.id}>
                      <td className="border border-slate-300 p-1 font-bold">{t.rakeNumber}</td>
                      <td className="border border-slate-300 p-1 font-mono">{t.stabling.trackLine}</td>
                      <td className="border border-slate-300 p-1 text-rose-700 font-semibold">
                        {t.jobCards[0]?.title || 'Scheduled Overhaul'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Departmental Authority Signatures */}
          <div className="pt-6 border-t-2 border-slate-300 grid grid-cols-4 gap-4 text-center">
            <div className="space-y-10">
              <div className="font-bold text-slate-800 text-[11px]">Chief Engineer (Rolling-Stock)</div>
              <div className="border-t border-slate-400 pt-1 text-[10px] text-slate-500">Sign & Stamp</div>
            </div>
            <div className="space-y-10">
              <div className="font-bold text-slate-800 text-[11px]">Chief Engineer (Signalling)</div>
              <div className="border-t border-slate-400 pt-1 text-[10px] text-slate-500">Sign & Stamp</div>
            </div>
            <div className="space-y-10">
              <div className="font-bold text-slate-800 text-[11px]">Chief Engineer (Telecom)</div>
              <div className="border-t border-slate-400 pt-1 text-[10px] text-slate-500">Sign & Stamp</div>
            </div>
            <div className="space-y-10">
              <div className="font-bold text-slate-800 text-[11px]">Operations Director (KMRL)</div>
              <div className="border-t border-slate-400 pt-1 text-[10px] text-slate-500">Approved & Ratified</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
