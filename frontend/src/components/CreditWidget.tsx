import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useCredits } from '@/contexts/CreditContext';

interface CreditWidgetProps {
  className?: string;
  compact?: boolean;
}

export const CreditWidget: React.FC<CreditWidgetProps> = ({ className, compact = false }) => {
  const { credits, isLoading, balance, isAdmin, planName, refetch } = useCredits();
  const [isExpanded, setIsExpanded] = useState(false);
  const [animatedBalance, setAnimatedBalance] = useState(balance);

  // Animate balance changes
  useEffect(() => {
    if (balance !== animatedBalance) {
      // Animate from current to new balance
      const diff = balance - animatedBalance;
      const steps = 10;
      const stepSize = diff / steps;
      let current = animatedBalance;
      let step = 0;

      const interval = setInterval(() => {
        step++;
        current += stepSize;
        if (step >= steps) {
          setAnimatedBalance(balance);
          clearInterval(interval);
        } else {
          setAnimatedBalance(Math.round(current));
        }
      }, 30);

      return () => clearInterval(interval);
    }
  }, [balance, animatedBalance]);

  // Calculate balance status for coloring
  const getBalanceStatus = () => {
    if (isAdmin) return 'admin';
    const creditsPerPeriod = credits?.credits_per_period || 30;
    const percentage = (balance / creditsPerPeriod) * 100;
    if (percentage <= 10) return 'critical';
    if (percentage <= 25) return 'warning';
    return 'normal';
  };

  const balanceStatus = getBalanceStatus();

  if (isLoading && !credits) {
    return (
      <div className={cn('p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 animate-pulse', className)}>
        <div className="h-6 w-20 bg-slate-700 rounded mb-1" />
        <div className="h-3 w-16 bg-slate-700 rounded" />
      </div>
    );
  }

  if (!credits) {
    return null;
  }

  // Compact mode for mobile
  if (compact) {
    return (
      <Link
        to="/app/settings"
        className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors',
          isAdmin
            ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30'
            : 'bg-slate-800/50 border border-slate-700/50 hover:bg-slate-700/50',
          className
        )}
      >
        {isAdmin ? (
          <>
            <span className="text-amber-400">👑</span>
            <span className="text-xs font-medium text-amber-400">Admin</span>
          </>
        ) : (
          <>
            <svg className="w-4 h-4 text-redd-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className={cn(
              'text-xs font-bold',
              balanceStatus === 'critical' && 'text-red-400',
              balanceStatus === 'warning' && 'text-orange-400',
              balanceStatus === 'normal' && 'text-white',
            )}>
              {animatedBalance}
            </span>
          </>
        )}
      </Link>
    );
  }

  return (
    <div className={cn(
      'rounded-lg border transition-all',
      isAdmin
        ? 'bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/30'
        : 'bg-slate-800/50 border-slate-700/50',
      className
    )}>
      {/* Main display */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-3 text-left flex items-center justify-between group"
      >
        <div className="flex items-center gap-3">
          {/* Icon */}
          {isAdmin ? (
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <span className="text-sm">👑</span>
            </div>
          ) : (
            <div className={cn(
              'w-8 h-8 rounded-full flex items-center justify-center',
              balanceStatus === 'critical' && 'bg-red-500/20',
              balanceStatus === 'warning' && 'bg-orange-500/20',
              balanceStatus === 'normal' && 'bg-redd-500/20',
            )}>
              <svg className={cn(
                'w-4 h-4',
                balanceStatus === 'critical' && 'text-red-400',
                balanceStatus === 'warning' && 'text-orange-400',
                balanceStatus === 'normal' && 'text-redd-400',
              )} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          )}

          {/* Balance */}
          <div>
            {isAdmin ? (
              <>
                <div className="flex items-center gap-1">
                  <span className="text-lg font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
                    ∞
                  </span>
                  <span className="text-xs text-amber-400/80 font-medium">UNLIMITED</span>
                </div>
                <p className="text-[10px] text-amber-400/60">Admin Access</p>
              </>
            ) : (
              <>
                <div className="flex items-baseline gap-1">
                  <span className={cn(
                    'text-lg font-bold tabular-nums transition-colors',
                    balanceStatus === 'critical' && 'text-red-400',
                    balanceStatus === 'warning' && 'text-orange-400',
                    balanceStatus === 'normal' && 'text-white',
                  )}>
                    {animatedBalance}
                  </span>
                  <span className="text-xs text-slate-400">credits</span>
                </div>
                <p className="text-[10px] text-slate-500 capitalize">{planName} Plan</p>
              </>
            )}
          </div>
        </div>

        {/* Expand chevron */}
        <svg
          className={cn(
            'w-4 h-4 text-slate-500 transition-transform',
            isExpanded && 'rotate-180'
          )}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded details */}
      {isExpanded && (
        <div className="px-3 pb-3 border-t border-slate-700/50 pt-2 space-y-2">
          {!isAdmin && (
            <>
              {/* Progress bar */}
              <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className={cn(
                    'h-full rounded-full transition-all duration-500',
                    balanceStatus === 'critical' && 'bg-red-500',
                    balanceStatus === 'warning' && 'bg-orange-500',
                    balanceStatus === 'normal' && 'bg-redd-500',
                  )}
                  style={{ width: `${Math.min((balance / (credits?.credits_per_period || 30)) * 100, 100)}%` }}
                />
              </div>

              {/* Reset info */}
              <p className="text-[10px] text-slate-500">
                {credits?.period === 'day' ? 'Resets daily' : 'Resets monthly'}
              </p>
            </>
          )}

          {/* Quick actions */}
          <div className="flex gap-2">
            <Link
              to="/app/settings"
              className="flex-1 text-center text-[10px] py-1.5 bg-slate-700/50 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors"
            >
              {isAdmin ? 'Settings' : 'View Plans'}
            </Link>
            <button
              onClick={(e) => { e.stopPropagation(); refetch(); }}
              className="px-2 py-1.5 bg-slate-700/50 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors"
              title="Refresh"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreditWidget;
