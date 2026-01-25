import React from 'react';
import { Link } from 'react-router-dom';

export const Hero: React.FC = () => {
  return (
    <section className="pt-32 pb-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-redd-500/10 border border-redd-500/20 mb-6">
            <span className="w-2 h-2 rounded-full bg-redd-500 animate-pulse"></span>
            <span className="text-redd-400 text-sm font-medium">AI-Powered</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white mb-6">
            Transform Product Photos into{' '}
            <span className="text-redd-500">Amazon-Ready Listings</span>
          </h1>

          {/* Subheadline */}
          <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-8">
            Upload your product photos. Our AI generates professional main images,
            infographics, and lifestyle shots — all optimized for Amazon in minutes.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link
              to="/app"
              className="w-full sm:w-auto px-8 py-4 bg-redd-500 hover:bg-redd-600 text-white font-semibold rounded-lg transition-colors text-lg"
            >
              Start Free
            </Link>
            <a
              href="#features"
              className="w-full sm:w-auto px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-medium rounded-lg transition-colors text-lg border border-slate-700"
            >
              See Examples
            </a>
          </div>

          {/* Hero Image */}
          <div className="relative mx-auto max-w-4xl">
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent z-10 pointer-events-none"></div>
            <div className="rounded-xl overflow-hidden border border-slate-700 shadow-2xl shadow-redd-500/10">
              <img
                src="/images/hero-mockup.png"
                alt="REDDAI.CO Dashboard - AI-powered Amazon listing image generator"
                className="w-full h-auto"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
