import React from 'react';
import { Link } from 'react-router-dom';

const plans = [
  {
    name: 'Starter',
    credits: 25,
    price: '$9.99',
    description: 'Perfect for trying it out',
    features: [
      '25 image credits',
      '5 images per listing',
      'All image types',
      'Style matching',
    ],
    popular: false,
  },
  {
    name: 'Pro',
    credits: 100,
    price: '$29.99',
    description: 'Most popular for sellers',
    features: [
      '100 image credits',
      '5 images per listing',
      'All image types',
      'Style matching',
      'Priority generation',
    ],
    popular: true,
  },
  {
    name: 'Agency',
    credits: 500,
    price: '$99.99',
    description: 'For high-volume sellers',
    features: [
      '500 image credits',
      '5 images per listing',
      'All image types',
      'Style matching',
      'Priority generation',
      'Bulk processing',
    ],
    popular: false,
  },
];

export const Pricing: React.FC = () => {
  return (
    <section id="pricing" className="py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl font-semibold text-white mb-4">
            Simple, Credit-Based Pricing
          </h2>
          <p className="text-slate-400 max-w-xl mx-auto">
            Buy credits, generate images. No subscriptions. Credits never expire.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`
                relative p-8 rounded-xl border transition-all
                ${plan.popular
                  ? 'bg-slate-800 border-redd-500 shadow-lg shadow-redd-500/10'
                  : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
                }
              `}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="px-3 py-1 bg-redd-500 text-white text-xs font-medium rounded-full">
                    POPULAR
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-xl font-medium text-white mb-1">{plan.name}</h3>
                <p className="text-slate-400 text-sm mb-4">{plan.description}</p>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-4xl font-bold text-white">{plan.price}</span>
                </div>
                <p className="text-slate-500 text-sm mt-1">{plan.credits} credits</p>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center gap-2 text-slate-300 text-sm">
                    <svg className="w-4 h-4 text-redd-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <Link
                to="/app"
                className={`
                  block w-full py-3 rounded-lg font-medium text-center transition-colors
                  ${plan.popular
                    ? 'bg-redd-500 hover:bg-redd-600 text-white'
                    : 'bg-slate-700 hover:bg-slate-600 text-white'
                  }
                `}
              >
                Get Started
              </Link>
            </div>
          ))}
        </div>

        {/* Fine Print */}
        <p className="text-center text-slate-500 text-sm mt-8">
          1 credit = 1 generated image. Each listing uses 5 credits.
        </p>
      </div>
    </section>
  );
};
