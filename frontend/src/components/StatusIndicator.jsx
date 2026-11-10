import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  RefreshCw, 
  Server, 
  Database, 
  Cpu, 
  Clock,
  Cloud
} from 'lucide-react';

const StatusIndicator = ({ healthData, loading, onRefresh }) => {
  const { overallStatus, backendOnline, databaseConnected, message, data } = healthData;

  const renderStatusBanner = () => {
    switch (overallStatus) {
      case 'connected':
        return (
          <div className="flex items-start space-x-3 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900">
            <CheckCircle2 className="h-6 w-6 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-base">Connected (Cloud Ready)</h3>
              <p className="text-sm text-emerald-700 mt-0.5">
                FastAPI backend and Supabase managed PostgreSQL are fully connected and responsive to health probes.
              </p>
            </div>
          </div>
        );

      case 'database_unavailable':
        return (
          <div className="flex items-start space-x-3 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900">
            <AlertTriangle className="h-6 w-6 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-base">Database Unavailable / Pending Setup</h3>
              <p className="text-sm text-amber-700 mt-0.5">
                The FastAPI backend is online, but Supabase PostgreSQL is unreachable or credentials are not yet configured in <code className="font-mono bg-amber-100 px-1 rounded">backend/.env</code>.
              </p>
              <p className="text-xs text-amber-800 mt-2 font-medium">
                Tip: Copy your Supabase Session Pooler URI into <span className="font-mono">backend/.env</span> under <span className="font-mono">DATABASE_URL</span> with <span className="font-mono">?sslmode=require</span>.
              </p>
            </div>
          </div>
        );

      case 'backend_unavailable':
      default:
        return (
          <div className="flex items-start space-x-3 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-900">
            <XCircle className="h-6 w-6 text-rose-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-base">Backend Unavailable</h3>
              <p className="text-sm text-rose-700 mt-0.5">
                Cannot reach the FastAPI server. If running locally, ensure Uvicorn is active. If running in cloud, check Render deployment status.
              </p>
              <p className="text-xs text-rose-800 mt-2 font-medium">
                Local: Run <span className="font-mono">uvicorn app.main:app --reload</span> inside <span className="font-mono">backend/</span>.
              </p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Cpu className="h-5 w-5 text-teal-600" />
          <h2 className="text-lg font-bold text-slate-900">System Integration Health</h2>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-50 transition-colors"
          title="Query /api/health now"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Checking...' : 'Refresh Status'}</span>
        </button>
      </div>

      <div className="p-6 space-y-6">
        {/* Main Status Banner */}
        {renderStatusBanner()}

        {/* Detailed Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Backend Card */}
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 flex items-center space-x-4">
            <div className={`p-3 rounded-lg ${backendOnline ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
              <Server className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Backend (FastAPI on Render)</p>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`inline-block h-2.5 w-2.5 rounded-full ${backendOnline ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                <span className="text-sm font-bold text-slate-900">
                  {backendOnline ? 'Online (Liveness OK)' : 'Offline / Unreachable'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">Endpoints: /api/health & /api/ready</p>
            </div>
          </div>

          {/* Database Card */}
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 flex items-center space-x-4">
            <div className={`p-3 rounded-lg ${databaseConnected ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
              <Database className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Database (Supabase PostgreSQL)</p>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`inline-block h-2.5 w-2.5 rounded-full ${databaseConnected ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                <span className="text-sm font-bold text-slate-900">
                  {databaseConnected ? 'Connected (Pooler active)' : 'Pending / Disconnected'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">Driver: Psycopg 3 + Alembic</p>
            </div>
          </div>
        </div>

        {/* Diagnostic Metadata Footer */}
        {data && (
          <div className="pt-4 border-t border-slate-100 text-xs text-slate-500 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center space-x-1.5">
              <Clock className="h-3.5 w-3.5 text-slate-400" />
              <span>Server UTC: <span className="font-mono">{data.timestamp}</span></span>
            </div>
            <div className="flex items-center space-x-1.5">
              <Cloud className="h-3.5 w-3.5 text-teal-600" />
              <span>Target: <span className="font-semibold text-slate-700">Vercel &bull; Render &bull; Supabase</span></span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatusIndicator;
