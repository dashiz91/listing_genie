import React from 'react';

export const SocialProof: React.FC = () => {
  return (
    <section className="py-8 px-4 sm:px-6 lg:px-8 border-y border-slate-800 bg-slate-800/30">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-8 text-center sm:text-left">
          <p className="text-slate-400 text-sm">Trusted by 1,000+ Amazon sellers</p>
          <div className="flex items-center gap-6">
            {/* Placeholder brand logos - simple text for now */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-slate-700 flex items-center justify-center">
                <span className="text-xs text-slate-500">FBA</span>
              </div>
              <span className="text-slate-500 text-xs hidden sm:inline">FBA Sellers</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-slate-700 flex items-center justify-center">
                <span className="text-xs text-slate-500">DTC</span>
              </div>
              <span className="text-slate-500 text-xs hidden sm:inline">DTC Brands</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-slate-700 flex items-center justify-center">
                <span className="text-xs text-slate-500">AG</span>
              </div>
              <span className="text-slate-500 text-xs hidden sm:inline">Agencies</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
