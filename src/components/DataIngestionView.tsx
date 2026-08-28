import React, { useState } from 'react';
import { UploadCloud, FileSpreadsheet, Radio, CheckCircle2, AlertCircle, RefreshCw, Layers } from 'lucide-react';

export const DataIngestionView: React.FC = () => {
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const handleSimulateUpload = (fileName: string) => {
    setIsUploading(true);
    setUploadSuccess(null);
    setTimeout(() => {
      setIsUploading(false);
      setUploadSuccess(`Successfully parsed and validated: ${fileName} (25 Rake Records Updated)`);
    }, 800);
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md bg-teal-50 text-teal-700 font-bold text-xs border border-teal-200">
              <Layers className="w-3.5 h-3.5" />
              <span>Unified Data Ingestion Hub</span>
            </div>
            <h2 className="text-xl font-heading font-extrabold text-slate-900 mt-1">
              Heterogeneous Data Ingestion & Stream Connectors
            </h2>
            <p className="text-xs text-slate-600 mt-0.5 max-w-2xl">
              Integrate IBM Maximo work orders, IoT telemetry streams (MQTT / UNS), and tri-department spreadsheets into an automated real-time schema.
            </p>
          </div>

          <span className="text-xs font-mono px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-800 font-bold flex items-center space-x-1.5 border border-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span>UNS Ingestion Active</span>
          </span>
        </div>
      </div>

      {/* Stream Connectors Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Maximo Stream */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-heading font-bold text-slate-900 text-sm">IBM Maximo REST API</span>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">CONNECTED</span>
          </div>
          <p className="text-xs text-slate-500">Live work order polling every 30s. Automatically imports open/closed defect cards.</p>
          <div className="text-[11px] text-slate-400 pt-1 border-t border-slate-100 flex justify-between">
            <span>Last Sync: 2 mins ago</span>
            <span className="text-teal-700 font-semibold">12 Open Cards Tracked</span>
          </div>
        </div>

        {/* IoT Telemetry Stream */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-heading font-bold text-slate-900 text-sm">IoT UNS Fleet Telemetry</span>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">STREAMING</span>
          </div>
          <p className="text-xs text-slate-500">MQTT stream for brake pressure, HVAC compressor PSI, and door cycle telemetry.</p>
          <div className="text-[11px] text-slate-400 pt-1 border-t border-slate-100 flex justify-between">
            <span>25 / 25 Rakes Live</span>
            <span className="text-teal-700 font-semibold">100 Hz Sample Rate</span>
          </div>
        </div>

        {/* Fitness Cert Ingestion */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-heading font-bold text-slate-900 text-sm">Tri-Dept Digital Portal</span>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">SYNCHRONIZED</span>
          </div>
          <p className="text-xs text-slate-500">Rolling-Stock, Signalling, and Telecom certificate sign-off workflow.</p>
          <div className="text-[11px] text-slate-400 pt-1 border-t border-slate-100 flex justify-between">
            <span>Signatures Verified</span>
            <span className="text-teal-700 font-semibold">3 Clearance Authorities</span>
          </div>
        </div>
      </div>

      {/* Manual File Dropzone & Template Upload */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <h3 className="font-heading font-bold text-slate-900 text-base flex items-center space-x-2">
          <FileSpreadsheet className="w-5 h-5 text-teal-600" />
          <span>Manual File Ingestion & Historical Import (Excel / CSV)</span>
        </h3>

        <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer">
          <UploadCloud className="w-10 h-10 text-teal-600 mx-auto" />
          <div className="font-heading font-bold text-slate-800 text-sm mt-2">
            Drag & Drop Department Spreadsheets or Maximo Export Files
          </div>
          <p className="text-xs text-slate-500 mt-1">Supports `.xlsx`, `.csv` (Fitness Certificates, Maximo Work Orders, Advertiser Contracts, Mileage Logs)</p>

          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {[
              'fitness_certificates_aug29.xlsx',
              'maximo_jobcards_export.csv',
              'branding_contracts_q3.xlsx',
              'muttom_stabling_geometry.csv',
            ].map((file) => (
              <button
                key={file}
                onClick={() => handleSimulateUpload(file)}
                disabled={isUploading}
                className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 hover:border-teal-500 text-slate-700 text-xs font-semibold shadow-sm transition-all flex items-center space-x-1.5"
              >
                <FileSpreadsheet className="w-3.5 h-3.5 text-teal-600" />
                <span>Simulate: {file}</span>
              </button>
            ))}
          </div>
        </div>

        {isUploading && (
          <div className="p-3 rounded-lg bg-teal-50 border border-teal-200 text-teal-800 text-xs flex items-center space-x-2 animate-pulse font-medium">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>Parsing file structure, checking schema validity, and refreshing constraint variables...</span>
          </div>
        )}

        {uploadSuccess && (
          <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center space-x-2 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{uploadSuccess}</span>
          </div>
        )}
      </div>
    </div>
  );
};
