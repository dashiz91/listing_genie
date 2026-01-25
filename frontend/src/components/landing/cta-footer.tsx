import React from 'react';
import { Link } from 'react-router-dom';

export const CTAFooter: React.FC = () => {
  return (
    <>
      {/* CTA Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-slate-800/30 to-slate-900">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-semibold text-white mb-4">
            Ready to transform your listings?
          </h2>
          <p className="text-slate-400 mb-8 text-lg">
            Join thousands of Amazon sellers using AI to create professional listing images.
          </p>
          <Link
            to="/app"
            className="inline-block px-8 py-4 bg-redd-500 hover:bg-redd-600 text-white font-semibold rounded-lg transition-colors text-lg"
          >
            Get Started Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
            {/* Logo Column */}
            <div className="col-span-2 md:col-span-1">
              <Link to="/" className="flex items-center gap-2 mb-4">
                <img src="/logo/fox-icon.png" alt="REDDAI.CO" className="w-8 h-8" />
                <span className="font-semibold text-lg text-white">REDDAI.CO</span>
              </Link>
              <p className="text-slate-400 text-sm">
                AI-powered Amazon listing images for modern sellers.
              </p>
            </div>

            {/* Product */}
            <div>
              <h4 className="text-white font-medium mb-4">Product</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#features" className="text-slate-400 hover:text-white text-sm transition-colors">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#pricing" className="text-slate-400 hover:text-white text-sm transition-colors">
                    Pricing
                  </a>
                </li>
                <li>
                  <Link to="/app" className="text-slate-400 hover:text-white text-sm transition-colors">
                    Dashboard
                  </Link>
                </li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-white font-medium mb-4">Company</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-slate-400 hover:text-white text-sm transition-colors">
                    About
                  </a>
                </li>
                <li>
                  <a href="#" className="text-slate-400 hover:text-white text-sm transition-colors">
                    Blog
                  </a>
                </li>
                <li>
                  <a href="#" className="text-slate-400 hover:text-white text-sm transition-colors">
                    Contact
                  </a>
                </li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="text-white font-medium mb-4">Legal</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-slate-400 hover:text-white text-sm transition-colors">
                    Privacy
                  </a>
                </li>
                <li>
                  <a href="#" className="text-slate-400 hover:text-white text-sm transition-colors">
                    Terms
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-slate-500 text-sm">
              &copy; {new Date().getFullYear()} REDDAI.CO. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              {/* Social Links - Placeholder */}
              <a href="#" className="text-slate-400 hover:text-white transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
};
