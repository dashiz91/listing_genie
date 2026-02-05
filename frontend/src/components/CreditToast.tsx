import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { useCredits } from '@/contexts/CreditContext';

export const CreditToast: React.FC = () => {
  const { lastUsage, clearUsage, refetch } = useCredits();
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (lastUsage) {
      setIsVisible(true);
      setIsExiting(false);

      // Auto-dismiss after 4 seconds
      const dismissTimer = setTimeout(() => {
        setIsExiting(true);
        setTimeout(() => {
          setIsVisible(false);
          clearUsage();
          // Refetch credits to ensure sync
          refetch();
        }, 300);
      }, 4000);

      return () => clearTimeout(dismissTimer);
    }
  }, [lastUsage, clearUsage, refetch]);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      clearUsage();
    }, 300);
  };

  if (!isVisible || !lastUsage) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div
        className={cn(
          'flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl transition-all duration-300',
          lastUsage.isAdmin
            ? 'bg-gradient-to-r from-amber-500/90 to-orange-500/90 text-white'
            : 'bg-slate-800 border border-slate-700 text-white',
          isExiting
            ? 'opacity-0 translate-y-2'
            : 'opacity-100 translate-y-0'
        )}
        style={{
          animation: isExiting ? undefined : 'slideInUp 0.3s ease-out',
        }}
      >
        {/* Icon */}
        {lastUsage.isAdmin ? (
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
            <span className="text-lg">👑</span>
          </div>
        ) : (
          <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )}

        {/* Content */}
        <div className="flex-1">
          <p className="font-medium text-sm">{lastUsage.operation}</p>
          {lastUsage.isAdmin ? (
            <p className="text-xs text-white/80">No credits used (Admin)</p>
          ) : (
            <p className="text-xs text-slate-400">
              <span className="text-redd-400 font-medium">{lastUsage.creditsUsed}</span> credits used
              <span className="mx-1">•</span>
              <span className="text-white">{lastUsage.newBalance}</span> remaining
            </p>
          )}
        </div>

        {/* Dismiss button */}
        <button
          onClick={handleDismiss}
          className={cn(
            'p-1 rounded-full transition-colors',
            lastUsage.isAdmin
              ? 'hover:bg-white/20'
              : 'hover:bg-slate-700'
          )}
        >
          <svg className="w-4 h-4 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <style>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(1rem);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default CreditToast;
