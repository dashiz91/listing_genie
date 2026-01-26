import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface SplitScreenLayoutProps {
  /** Left panel content (Workshop) */
  leftPanel: React.ReactNode;
  /** Right panel content (Showroom/Preview) */
  rightPanel: React.ReactNode;
  /** Optional class for the container */
  className?: string;
}

/**
 * SplitScreenLayout - Two-panel responsive container
 *
 * Desktop (>1024px): Side-by-side 40/60 split
 * Tablet (768-1024px): 50/50 split
 * Mobile (<768px): Stacked with collapsible mini-preview at bottom
 */
export const SplitScreenLayout: React.FC<SplitScreenLayoutProps> = ({
  leftPanel,
  rightPanel,
  className,
}) => {
  const [mobilePreviewExpanded, setMobilePreviewExpanded] = useState(false);

  const toggleMobilePreview = useCallback(() => {
    setMobilePreviewExpanded((prev) => !prev);
  }, []);

  return (
    <div className={cn('h-full w-full', className)}>
      {/* Desktop/Tablet Layout */}
      <div className="hidden md:flex h-full">
        {/* Left Panel (Workshop) - 40% on desktop, 50% on tablet */}
        <div className="w-1/2 lg:w-[40%] h-full overflow-y-auto border-r border-slate-700 bg-slate-900">
          <div className="p-6">
            {leftPanel}
          </div>
        </div>

        {/* Right Panel (Showroom/Preview) - 60% on desktop, 50% on tablet */}
        <div className="w-1/2 lg:w-[60%] h-full overflow-y-auto bg-slate-800/50">
          <div className="p-6 h-full">
            {rightPanel}
          </div>
        </div>
      </div>

      {/* Mobile Layout - Stacked with sticky mini-preview */}
      <div className="md:hidden flex flex-col h-full">
        {/* Scrollable form area */}
        <div
          className={cn(
            'flex-1 overflow-y-auto transition-all duration-300',
            mobilePreviewExpanded ? 'max-h-0 overflow-hidden' : ''
          )}
        >
          <div className="p-4">
            {leftPanel}
          </div>
        </div>

        {/* Mobile mini-preview / Expanded preview */}
        <div
          className={cn(
            'border-t border-slate-700 bg-slate-800 transition-all duration-300',
            mobilePreviewExpanded
              ? 'h-full'
              : 'h-[30%] min-h-[200px]'
          )}
        >
          {/* Expand/Collapse handle */}
          <button
            onClick={toggleMobilePreview}
            className="w-full flex items-center justify-center py-2 border-b border-slate-700 hover:bg-slate-700/50 transition-colors"
            aria-label={mobilePreviewExpanded ? 'Collapse preview' : 'Expand preview'}
          >
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <svg
                className={cn(
                  'w-4 h-4 transition-transform duration-300',
                  mobilePreviewExpanded ? 'rotate-180' : ''
                )}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              <span>{mobilePreviewExpanded ? 'Collapse Preview' : 'Expand Preview'}</span>
            </div>
          </button>

          {/* Preview content */}
          <div className={cn(
            'overflow-y-auto p-4',
            mobilePreviewExpanded ? 'h-[calc(100%-44px)]' : 'h-[calc(100%-44px)]'
          )}>
            {rightPanel}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SplitScreenLayout;
