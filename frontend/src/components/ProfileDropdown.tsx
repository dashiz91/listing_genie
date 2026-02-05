import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/contexts/AuthContext';
import { useCredits } from '@/contexts/CreditContext';
import { cn } from '@/lib/utils';

interface ProfileDropdownProps {
  className?: string;
}

export const ProfileDropdown: React.FC<ProfileDropdownProps> = ({ className }) => {
  const { user, signOut } = useAuth();
  const { balance, isAdmin, planName, credits } = useCredits();
  const navigate = useNavigate();

  // Get user initials from email
  const getInitials = (email: string | undefined) => {
    if (!email) return '?';
    const parts = email.split('@')[0];
    if (parts.length >= 2) {
      return parts.slice(0, 2).toUpperCase();
    }
    return parts[0]?.toUpperCase() || '?';
  };

  // Truncate email for display
  const truncateEmail = (email: string | undefined, maxLength: number = 20) => {
    if (!email) return '';
    if (email.length <= maxLength) return email;
    const [localPart, domain] = email.split('@');
    const truncatedLocal = localPart.slice(0, Math.max(3, maxLength - domain.length - 4)) + '...';
    return `${truncatedLocal}@${domain}`;
  };

  // Calculate usage percentage
  const getUsagePercentage = () => {
    if (isAdmin) return 100;
    const creditsPerPeriod = credits?.credits_per_period || 30;
    return Math.round((balance / creditsPerPeriod) * 100);
  };

  const handleSignOut = async () => {
    await signOut();
    navigate('/auth');
  };

  const initials = getInitials(user?.email);
  const usagePercent = getUsagePercentage();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={cn(
            'w-full flex items-center gap-3 p-2 rounded-lg transition-colors',
            'hover:bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-redd-500/50',
            isAdmin
              ? 'bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20'
              : 'bg-slate-800/30 border border-slate-700/50',
            className
          )}
        >
          {/* Avatar */}
          <div
            className={cn(
              'w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold shrink-0',
              isAdmin
                ? 'bg-gradient-to-br from-amber-400 to-orange-500 text-white'
                : 'bg-redd-500/20 text-redd-400'
            )}
          >
            {isAdmin ? '👑' : initials}
          </div>

          {/* Info */}
          <div className="flex-1 text-left min-w-0">
            <div className="flex items-center gap-2">
              {isAdmin ? (
                <span className="text-sm font-semibold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
                  Admin
                </span>
              ) : (
                <span className="text-sm font-medium text-white truncate">
                  {balance} credits
                </span>
              )}
            </div>
            <p className="text-[10px] text-slate-500 capitalize truncate">
              {planName} Plan
            </p>
          </div>

          {/* Chevron */}
          <svg
            className="w-4 h-4 text-slate-500 shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="start"
        side="right"
        sideOffset={8}
        className="w-56 bg-slate-900 border-slate-700"
      >
        {/* User email */}
        <DropdownMenuLabel className="font-normal">
          <p className="text-xs text-slate-400 truncate">{truncateEmail(user?.email, 28)}</p>
        </DropdownMenuLabel>

        {/* Usage indicator */}
        <div className="px-2 py-2">
          <div className="flex items-center justify-between text-[10px] mb-1">
            <span className="text-slate-500">
              {isAdmin ? 'Unlimited usage' : `${usagePercent}% credits used`}
            </span>
          </div>
          {!isAdmin && (
            <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all',
                  usagePercent >= 90 ? 'bg-red-500' :
                  usagePercent >= 75 ? 'bg-orange-500' : 'bg-redd-500'
                )}
                style={{ width: `${Math.min(usagePercent, 100)}%` }}
              />
            </div>
          )}
        </div>

        <DropdownMenuSeparator className="bg-slate-700" />

        {/* Menu items */}
        <DropdownMenuItem asChild>
          <Link
            to="/app/settings?tab=billing"
            className="flex items-center gap-2 cursor-pointer"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            Plans & Pricing
          </Link>
        </DropdownMenuItem>

        <DropdownMenuItem asChild>
          <Link
            to="/app/settings"
            className="flex items-center gap-2 cursor-pointer"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Settings
          </Link>
        </DropdownMenuItem>

        <DropdownMenuItem asChild>
          <a
            href="https://discord.gg/reddstudio"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 cursor-pointer"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
            </svg>
            Join Community
          </a>
        </DropdownMenuItem>

        <DropdownMenuSeparator className="bg-slate-700" />

        <DropdownMenuItem
          onClick={handleSignOut}
          className="flex items-center gap-2 cursor-pointer text-red-400 focus:text-red-400 focus:bg-red-500/10"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default ProfileDropdown;
