import React from 'react';
import { cn } from '@/lib/utils';

interface VersionNavigatorProps {
  currentVersion: number;
  totalVersions: number;
  onPrevious: () => void;
  onNext: () => void;
  onEdit: () => void;
  onRegenerate: () => void;
  isProcessing?: boolean;
  className?: string;
}

export const VersionNavigator: React.FC<VersionNavigatorProps> = ({
  currentVersion,
  totalVersions,
  onPrevious,
  onNext,
  onEdit,
  onRegenerate,
  isProcessing = false,
  className,
}) => {
  const hasPrevious = currentVersion > 1;
  const hasNext = currentVersion < totalVersions;

  return (
    <div
      className={cn(
        'flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4 px-4 py-3 bg-slate-800/80 backdrop-blur-sm rounded-lg border border-slate-700',
        className
      )}
      role="region"
      aria-label="Image version navigation"
    >
      {/* Version Navigation */}
      <nav className="flex items-center gap-2" aria-label="Version controls">
        {/* Previous Button */}
        <button
          onClick={onPrevious}
          disabled={!hasPrevious || isProcessing}
          aria-label="Go to previous version"
          aria-keyshortcuts="ArrowLeft"
          className={cn(
            'p-1.5 rounded-md transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-redd-500 focus:ring-offset-2 focus:ring-offset-slate-800',
            hasPrevious && !isProcessing
              ? 'text-slate-300 hover:text-white hover:bg-slate-700'
              : 'text-slate-600 cursor-not-allowed'
          )}
          title="Previous version (←)"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        {/* Version Indicator */}
        <div
          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900/50 rounded text-sm"
          aria-live="polite"
          aria-atomic="true"
        >
          <span className="text-slate-400">Version</span>
          <span className="text-white font-medium">{currentVersion}</span>
          <span className="text-slate-500">of</span>
          <span className="text-slate-300">{totalVersions}</span>
        </div>

        {/* Next Button */}
        <button
          onClick={onNext}
          disabled={!hasNext || isProcessing}
          aria-label="Go to next version"
          aria-keyshortcuts="ArrowRight"
          className={cn(
            'p-1.5 rounded-md transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-redd-500 focus:ring-offset-2 focus:ring-offset-slate-800',
            hasNext && !isProcessing
              ? 'text-slate-300 hover:text-white hover:bg-slate-700'
              : 'text-slate-600 cursor-not-allowed'
          )}
          title="Next version (→)"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </nav>

      {/* Action Buttons */}
      <div className="flex items-center gap-2" role="group" aria-label="Image actions">
        {/* Edit Button */}
        <button
          onClick={onEdit}
          disabled={isProcessing}
          aria-label="Edit current image"
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200',
            'border border-slate-600 text-slate-300 hover:text-white hover:bg-slate-700 hover:border-slate-500',
            'focus:outline-none focus:ring-2 focus:ring-redd-500 focus:ring-offset-2 focus:ring-offset-slate-800',
            isProcessing && 'opacity-50 cursor-not-allowed'
          )}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
          <span>Edit</span>
        </button>

        {/* Regenerate Button */}
        <button
          onClick={onRegenerate}
          disabled={isProcessing}
          aria-label={isProcessing ? 'Generating new version' : 'Regenerate image'}
          aria-busy={isProcessing}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200',
            'bg-redd-500 text-white hover:bg-redd-600',
            'focus:outline-none focus:ring-2 focus:ring-redd-500 focus:ring-offset-2 focus:ring-offset-slate-800',
            isProcessing && 'opacity-50 cursor-not-allowed'
          )}
        >
          {isProcessing ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" aria-hidden="true" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              <span>Regenerate</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
