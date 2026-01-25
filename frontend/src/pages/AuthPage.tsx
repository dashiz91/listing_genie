import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Auth } from '@supabase/auth-ui-react';
import { ThemeSupa } from '@supabase/auth-ui-shared';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

export const AuthPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate('/app');
    }
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <img
            src="/logo/fox-icon.png"
            alt="REDDAI Logo"
            className="w-16 h-16 mx-auto mb-4"
          />
          <h1 className="text-2xl font-bold text-white">
            Welcome to <span className="text-redd-500">Listing Genie</span>
          </h1>
          <p className="text-slate-400 mt-2">
            Sign in to create AI-powered Amazon listing images
          </p>
        </div>

        {/* Auth Form */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <Auth
            supabaseClient={supabase}
            appearance={{
              theme: ThemeSupa,
              variables: {
                default: {
                  colors: {
                    brand: '#C85A35',
                    brandAccent: '#A04830',
                    brandButtonText: 'white',
                    defaultButtonBackground: '#374151',
                    defaultButtonBackgroundHover: '#4B5563',
                    inputBackground: '#1F2937',
                    inputBorder: '#374151',
                    inputBorderHover: '#C85A35',
                    inputBorderFocus: '#C85A35',
                    inputText: 'white',
                    inputPlaceholder: '#9CA3AF',
                  },
                  borderWidths: {
                    buttonBorderWidth: '1px',
                    inputBorderWidth: '1px',
                  },
                  radii: {
                    borderRadiusButton: '8px',
                    buttonBorderRadius: '8px',
                    inputBorderRadius: '8px',
                  },
                },
              },
              className: {
                container: 'auth-container',
                button: 'auth-button',
                input: 'auth-input',
              },
            }}
            providers={[]}
            redirectTo={window.location.origin + '/app'}
          />
        </div>

        {/* Footer */}
        <p className="text-center text-slate-500 text-sm mt-6">
          Powered by <span className="text-redd-400">REDDAI.CO</span>
        </p>
      </div>
    </div>
  );
};
