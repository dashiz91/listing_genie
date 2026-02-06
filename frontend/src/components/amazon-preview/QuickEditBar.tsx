import React from 'react';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';
import type { SessionImage } from '@/api/types';

interface QuickEditBarProps {
  images: SessionImage[];
  selectedType: string;
  onEdit: (imageType: string) => void;
  onRegenerate: (imageType: string) => void;
  onViewPrompt?: (imageType: string) => void;
  className?: string;
}

// Image type order for display
const IMAGE_ORDER = ['main', 'infographic_1', 'infographic_2', 'lifestyle', 'transformation', 'comparison'];

// Short labels for the edit bar
const SHORT_LABELS: Record<string, string> = {
  main: 'Main',
  infographic_1: 'Info 1',
  infographic_2: 'Info 2',
  lifestyle: 'Lifestyle',
  transformation: 'Transform',
  comparison: 'Compare',
};

export const QuickEditBar: React.FC<QuickEditBarProps> = ({
  images,
  selectedType,
  onEdit,
  onRegenerate,
  onViewPrompt,
  className,
}) => {
  // Sort images by order
  const sortedImages = [...images].sort(
    (a, b) => IMAGE_ORDER.indexOf(a.type) - IMAGE_ORDER.indexOf(b.type)
  );

  return (
    <div
      className={cn(
        'flex flex-wrap items-center gap-2 p-3 bg-slate-800/50 border border-slate-700 rounded-xl',
        className
      )}
      role="toolbar"
      aria-label="Quick edit toolbar for all images"
    >
      <span className="text-sm text-slate-400 mr-2" id="quick-edit-label">Quick Edit:</span>
      {sortedImages.map((image) => {
        const isSelected = image.type === selectedType;
        const isComplete = image.status === 'complete';
        const isProcessing = image.status === 'processing';
        const label = SHORT_LABELS[image.type] || image.label;

        return (
          <div
            key={image.type}
            className={cn(
              'flex items-center gap-1 px-2 py-1.5 rounded-lg border transition-all duration-200',
              isSelected
                ? 'border-redd-500/50 bg-redd-500/10 scale-105'
                : 'border-slate-700 bg-slate-800/50 hover:border-slate-600',
              !isComplete && 'opacity-50'
            )}
            role="group"
            aria-label={`${label} image actions`}
          >
            <span
              className={cn(
                'text-xs font-medium',
                isSelected ? 'text-redd-400' : 'text-slate-300'
              )}
            >
              {label}
            </span>

            {isComplete && (
              <div className="flex items-center gap-0.5 ml-1">
                {/* Edit button */}
                <button
                  onClick={() => onEdit(image.type)}
                  className="p-1 text-slate-400 hover:text-redd-400 transition-colors rounded focus:outline-none focus:ring-2 focus:ring-redd-500 focus:ring-offset-1 focus:ring-offset-slate-800"
                  title={`Edit ${label}`}
                  aria-label={`Edit ${label} image`}
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                </button>

                {/* Regenerate button */}
                <button
                  onClick={() => onRegenerate(image.type)}
                  className="p-1 text-slate-400 hover:text-redd-400 transition-colors rounded focus:outline-none focus:ring-2 focus:ring-redd-500 focus:ring-offset-1 focus:ring-offset-slate-800"
                  title={`Regenerate ${label}`}
                  aria-label={`Regenerate ${label} image`}
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                </button>

                {/* View Prompt button (dev mode) */}
                {onViewPrompt && (
                  <button
                    onClick={() => onViewPrompt(image.type)}
                    className="p-1 text-slate-400 hover:text-purple-400 transition-colors rounded focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-1 focus:ring-offset-slate-800"
                    title={`View Prompt for ${label}`}
                    aria-label={`View prompt used for ${label} image`}
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                      />
                    </svg>
                  </button>
                )}
              </div>
            )}

            {isProcessing && (
              <Spinner size="sm" className="text-redd-500 ml-1" />
            )}
          </div>
        );
      })}
    </div>
  );
};
