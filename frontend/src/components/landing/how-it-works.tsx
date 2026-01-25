import React from 'react';

const steps = [
  {
    number: '1',
    title: 'Upload',
    description: 'Drop in your product photos. Raw shots work great.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
      </svg>
    ),
  },
  {
    number: '2',
    title: 'AI Magic',
    description: 'Our AI analyzes your product and creates 4 unique design frameworks.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  {
    number: '3',
    title: 'Download',
    description: 'Get 5 professional images. Main, infographics, lifestyle, and comparison.',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
    ),
  },
];

export const HowItWorks: React.FC = () => {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 bg-slate-800/30">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-semibold text-white mb-4">
            How It Works
          </h2>
          <p className="text-slate-400 max-w-xl mx-auto">
            From photo to professional listing images in three simple steps.
          </p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connection Line - Desktop */}
          <div className="hidden md:block absolute top-12 left-1/2 -translate-x-1/2 w-2/3 h-0.5 bg-gradient-to-r from-slate-700 via-redd-500/50 to-slate-700"></div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
            {steps.map((step, index) => (
              <div key={index} className="relative text-center">
                {/* Step Number Circle */}
                <div className="relative z-10 w-24 h-24 mx-auto mb-6 rounded-full bg-slate-800 border-2 border-slate-700 flex items-center justify-center">
                  <div className="w-16 h-16 rounded-full bg-redd-500/10 flex items-center justify-center text-redd-500">
                    {step.icon}
                  </div>
                  {/* Number Badge */}
                  <div className="absolute -top-1 -right-1 w-7 h-7 rounded-full bg-redd-500 flex items-center justify-center">
                    <span className="text-white text-sm font-bold">{step.number}</span>
                  </div>
                </div>

                <h3 className="text-xl font-medium text-white mb-2">{step.title}</h3>
                <p className="text-slate-400 text-sm max-w-xs mx-auto">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
