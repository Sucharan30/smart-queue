import React from 'react';
import { Activity, ShieldCheck } from 'lucide-react';

const Navbar = ({ overallStatus }) => {
  const getBadgeStyle = () => {
    switch (overallStatus) {
      case 'connected':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'database_unavailable':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'backend_unavailable':
      default:
        return 'bg-rose-100 text-rose-800 border-rose-300';
    }
  };

  const getBadgeText = () => {
    switch (overallStatus) {
      case 'connected':
        return 'System Connected';
      case 'database_unavailable':
        return 'DB Unavailable';
      case 'backend_unavailable':
      default:
        return 'Backend Offline';
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-teal-600 flex items-center justify-center text-white shadow-sm shadow-teal-500/20">
              <Activity className="h-6 w-6" />
            </div>
            <div>
              <span className="text-lg font-bold text-slate-900 tracking-tight block leading-tight">
                The Cost of Waiting
              </span>
              <span className="text-xs text-teal-700 font-medium">
                Public Hospital Smart Queuing
              </span>
            </div>
          </div>

          {/* Status Badge & Milestone indicator */}
          <div className="flex items-center space-x-4">
            <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
              Checkpoint 1: Foundation
            </span>
            <div className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${getBadgeStyle()}`}>
              <span className={`h-2 w-2 rounded-full ${overallStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : overallStatus === 'database_unavailable' ? 'bg-amber-500 animate-pulse' : 'bg-rose-500'}`} />
              <span>{getBadgeText()}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;

