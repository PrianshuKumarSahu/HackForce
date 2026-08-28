import React, { useState } from 'react';
import { Trainset, InductionRole } from '../types';
import { X, CheckCircle2, AlertTriangle, ArrowRightLeft, UserCheck, ShieldAlert } from 'lucide-react';

interface SupervisorOverrideModalProps {
  train: Trainset | null;
  onClose: () => void;
  onSaveOverride: (trainId: string, newRole: InductionRole, justification: string, supervisorName: string) => void;
}

export const SupervisorOverrideModal: React.FC<SupervisorOverrideModalProps> = ({
  train,
  onClose,
  onSaveOverride,
}) => {
  if (!train) return null;

  const [selectedRole, setSelectedRole] = useState<InductionRole>(train.assignedRole);
  const [justification, setJustification] = useState<string>('');
  const [supervisorName, setSupervisorName] = useState<string>('Shift Lead Rajesh Nair');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!justification.trim()) {
      setErrorMsg('Please provide an operational justification for the ML feedback loop audit.');
      return;
    }
    onSaveOverride(train.id, selectedRole, justification, supervisorName);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-lg w-full overflow-hidden animate-fade-in">
        {/* Modal Header */}
        <div className="bg-slate-900 text-white p-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ArrowRightLeft className="w-5 h-5 text-teal-400" />
            <span className="font-heading font-extrabold text-base">
              Supervisor Manual Override: {train.rakeNumber}
            </span>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          {/* Current State vs Proposed State */}
          <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Current AI Recommendation:</span>
              <strong className="text-teal-700 font-bold">{train.assignedRole} (Score: {train.overallReadinessScore}%)</strong>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Stabling Track:</span>
              <strong className="text-slate-800">{train.stabling.trackLine} - Pos {train.stabling.positionDepth}</strong>
            </div>
            {train.branding && (
              <div className="flex justify-between items-center text-purple-700">
                <span>Active Commercial Wrap:</span>
                <strong>{train.branding.advertiser} ({train.branding.tier})</strong>
              </div>
            )}
          </div>

          {/* Role Selection */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-800">Select Override Role:</label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 'REVENUE_SERVICE', label: 'Dawn Revenue Service (05:30)', color: 'border-emerald-300 hover:bg-emerald-50 text-emerald-900' },
                { id: 'HOT_STANDBY', label: 'Hot Standby Reserve Siding', color: 'border-amber-300 hover:bg-amber-50 text-amber-900' },
                { id: 'IBL_MAINTENANCE', label: 'IBL Bay Overhaul Holdback', color: 'border-rose-300 hover:bg-rose-50 text-rose-900' },
                { id: 'CLEANING_BAY', label: 'Deep Sanitization Wash Plant', color: 'border-teal-300 hover:bg-teal-50 text-teal-900' },
              ].map((roleOption) => (
                <button
                  type="button"
                  key={roleOption.id}
                  onClick={() => setSelectedRole(roleOption.id as InductionRole)}
                  className={`p-2.5 rounded-xl border text-left font-semibold transition-all ${roleOption.color} ${
                    selectedRole === roleOption.id
                      ? 'ring-2 ring-teal-500 bg-teal-50/80 border-teal-500 shadow-sm'
                      : 'bg-white'
                  }`}
                >
                  <div className="text-xs">{roleOption.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Justification Field */}
          <div className="space-y-1.5">
            <label className="font-bold text-slate-800 flex items-center justify-between">
              <span>Operational Justification (Mandatory for ML Retraining):</span>
              <span className="text-[10px] text-slate-400">Captured in immutable audit log</span>
            </label>
            <textarea
              rows={3}
              required
              placeholder="E.g., Held on hot standby due to unconfirmed brake transducer sensor glitch; re-inspection booked at 05:00 AM."
              value={justification}
              onChange={(e) => {
                setJustification(e.target.value);
                setErrorMsg(null);
              }}
              className="w-full p-2.5 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500/40"
            ></textarea>
            {errorMsg && <p className="text-rose-600 font-semibold text-[11px]">{errorMsg}</p>}
          </div>

          {/* Supervisor Identity */}
          <div className="space-y-1">
            <label className="font-bold text-slate-800">Authorizing Supervisor Name:</label>
            <div className="relative">
              <UserCheck className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                required
                value={supervisorName}
                onChange={(e) => setSupervisorName(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500/40"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white font-bold shadow-md transition-all"
            >
              Confirm Override & Update Roster
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
