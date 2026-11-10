import React from 'react';
import { HeartPulse } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left">
          <div className="flex items-center space-x-2 text-slate-700">
            <HeartPulse className="h-5 w-5 text-teal-600 flex-shrink-0" />
            <span className="text-sm font-semibold text-slate-900">
              The Cost of Waiting
            </span>
            <span className="text-slate-400">|</span>
            <span className="text-sm text-slate-600">
              Smart Queuing for Public Hospitals
            </span>
          </div>
          <div className="text-xs text-slate-500">
            Designed for high-throughput public hospital outpatient clinics. Checkpoint 1 (Foundation Stage).
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

