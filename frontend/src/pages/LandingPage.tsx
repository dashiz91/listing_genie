import React from 'react';
import {
  Navbar,
  Hero,
  SocialProof,
  Features,
  HowItWorks,
  Pricing,
  CTAFooter,
} from '../components/landing';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-white font-sans">
      <Navbar />
      <main>
        <Hero />
        <SocialProof />
        <Features />
        <HowItWorks />
        <Pricing />
        <CTAFooter />
      </main>
    </div>
  );
};
