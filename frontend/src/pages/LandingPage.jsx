import React from 'react';
import StatusIndicator from '../components/StatusIndicator';
import { 
  Clock, 
  MessageSquare, 
  Users, 
  ShieldAlert, 
  CheckCircle, 
  Layers, 
  ArrowRight,
  TrendingDown,
  Building2,
  Cloud
} from 'lucide-react';

const LandingPage = ({ healthData, loading, onRefresh }) => {
  return (
    <div className="space-y-12 py-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <section className="text-center max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-teal-50 border border-teal-200 text-teal-800 text-xs font-semibold uppercase tracking-wider">
          <Building2 className="h-3.5 w-3.5" />
          <span>Public Hospital Digital Healthcare Initiative</span>
        </div>
        
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
          The Cost of Waiting
        </h1>
        
        <p className="text-xl sm:text-2xl font-semibold text-teal-700">
          Smart Queuing for Public Hospitals
        </p>
        
        <p className="text-base sm:text-lg text-slate-600 leading-relaxed pt-2">
          A WhatsApp-integrated hospital queue management platform designed to eliminate multi-hour waiting room congestion, protect vulnerable patients from cross-infections, and safeguard daily-wage earnings through real-time queue visibility.
        </p>
      </section>

      {/* Real-Time Backend & Database Health Status Indicator */}
      <section className="max-w-3xl mx-auto">
        <StatusIndicator 
          healthData={healthData} 
          loading={loading} 
          onRefresh={onRefresh} 
        />
      </section>

      {/* Project Purpose & The Cost of Waiting Overview */}
      <section className="max-w-5xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-slate-900">Addressing the Waiting Crisis in Public Health</h2>
          <p className="text-sm text-slate-600 mt-1">Why modernizing outpatient queuing changes community healthcare outcomes</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="h-12 w-12 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center mb-4">
              <TrendingDown className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Economic Protection</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Long, unpredictable wait times cost daily-wage patients an entire day's income. Remote queue tracking allows patients to manage their work and time.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="h-12 w-12 rounded-xl bg-rose-100 text-rose-700 flex items-center justify-center mb-4">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Infection Control</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Crowded, enclosed waiting rooms act as vectors for respiratory transmission. Decoupling waiting from physical halls protects vulnerable patients.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="h-12 w-12 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center mb-4">
              <MessageSquare className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Zero-Barrier WhatsApp</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Patients do not need to install complex mobile applications. Queue tokens, status changes, and arrival alerts are delivered over WhatsApp.
            </p>
          </div>
        </div>
      </section>

      {/* Checkpoint 1 Cloud Architecture Foundation */}
      <section className="max-w-5xl mx-auto bg-slate-900 text-white rounded-2xl p-8 sm:p-10 shadow-lg">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pb-8 border-b border-slate-800">
          <div>
            <span className="text-teal-400 font-mono text-xs uppercase tracking-widest font-semibold block mb-1">
              Cloud Architecture
            </span>
            <h2 className="text-2xl font-bold">Vercel &bull; Render &bull; Supabase Foundation</h2>
          </div>
          <span className="px-3 py-1 rounded-full bg-teal-900/60 border border-teal-500/30 text-teal-300 text-xs font-medium">
            Piloting: 1 Clinic &bull; 1 Doctor Scalable Model
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
          <div className="space-y-2">
            <div className="text-teal-400 font-semibold text-sm flex items-center space-x-1.5">
              <CheckCircle className="h-4 w-4" />
              <span>Frontend (Vercel)</span>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">
              React 18, Vite, Tailwind CSS, SPA routing, and dynamic Axios client communicating with Render.
            </p>
          </div>

          <div className="space-y-2">
            <div className="text-teal-400 font-semibold text-sm flex items-center space-x-1.5">
              <CheckCircle className="h-4 w-4" />
              <span>Backend (Render)</span>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">
              FastAPI ASGI service with CORS security, Liveness (/api/health) and Readiness (/api/ready) probes.
            </p>
          </div>

          <div className="space-y-2">
            <div className="text-teal-400 font-semibold text-sm flex items-center space-x-1.5">
              <CheckCircle className="h-4 w-4" />
              <span>Database (Supabase)</span>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">
              Managed PostgreSQL with Session Pooling, SSL encryption, and Psycopg 3 driver connectivity.
            </p>
          </div>

          <div className="space-y-2">
            <div className="text-teal-400 font-semibold text-sm flex items-center space-x-1.5">
              <CheckCircle className="h-4 w-4" />
              <span>Schema Migrations</span>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">
              Alembic migration pipeline configured for reliable versioned schema deployments.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
