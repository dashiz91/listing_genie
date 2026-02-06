import React from 'react';
import { cn } from '@/lib/utils';
import type { SessionImage } from '@/api/types';

/** Friendly display names for image types */
const IMAGE_TYPE_LABELS: Record<string, string> = {
  main: 'Hero',
  infographic_1: 'Infographic 1',
  infographic_2: 'Infographic 2',
  lifestyle: 'Lifestyle',
  transformation: 'Transformation',
  comparison: 'Comparison',
};

interface GenerationProgressBarProps {
  images: SessionImage[];
  isGenerating: boolean;
}

export const GenerationProgressBar: React.FC<GenerationProgressBarProps> = ({
  images,
  isGenerating,
}) => {
  if (!isGenerating) return null;

  const total = images.length;
  const completed = images.filter(img => img.status === 'complete' || img.status === 'failed').length;
  const percent = total > 0 ? (completed / total) * 100 : 0;

  return (
    <div className="bg-slate-800/80 backdrop-blur-sm border-b border-slate-700/50 px-4 py-3">
      <div className="max-w-7xl mx-auto space-y-2">
        {/* Top row: label + count */}
        <div className="flex items-center gap-3">
          {/* Pulsing dot */}
          <span className="relative flex h-2.5 w-2.5 shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-redd-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-redd-500" />
          </span>

          <span className="text-xs text-slate-300 whitespace-nowrap font-medium">
            Generating listing images — {completed} of {total} complete
          </span>

          {/* Progress bar */}
          <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700 ease-out"
              style={{
                width: `${percent}%`,
                background: 'linear-gradient(90deg, #C85A35, #D4795A)',
              }}
            />
          </div>
        </div>

        {/* Per-image status row */}
        <div className="flex items-center gap-1 overflow-x-auto pb-0.5">
          {images.map((img) => {
            const label = IMAGE_TYPE_LABELS[img.type] || img.type;
            const isComplete = img.status === 'complete';
            const isProcessing = img.status === 'processing';
            const isFailed = img.status === 'failed';

            return (
              <div
                key={img.type}
                className="flex items-center gap-1 shrink-0 px-1.5 py-0.5"
              >
                {/* Status dot */}
                <div
                  className={cn(
                    'w-2.5 h-2.5 rounded-full flex items-center justify-center transition-all',
                    isComplete && 'bg-redd-500',
                    isProcessing && 'bg-redd-500 animate-pulse-soft',
                    isFailed && 'bg-red-500',
                    !isComplete && !isProcessing && !isFailed && 'border border-slate-600 bg-transparent',
                  )}
                >
                  {isComplete && (
                    <svg className="w-1.5 h-1.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>

                {/* Label */}
                <span
                  className={cn(
                    'text-[10px] whitespace-nowrap',
                    isComplete && 'text-slate-400',
                    isProcessing && 'text-redd-400 font-medium',
                    isFailed && 'text-red-400',
                    !isComplete && !isProcessing && !isFailed && 'text-slate-600',
                  )}
                >
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
