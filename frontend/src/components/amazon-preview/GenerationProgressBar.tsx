import React from 'react';
import type { SessionImage } from '@/api/types';

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
    <div className="bg-slate-800/80 backdrop-blur-sm border-b border-slate-700/50 px-4 py-2">
      <div className="max-w-7xl mx-auto flex items-center gap-3">
        {/* Pulsing dot */}
        <span className="relative flex h-2.5 w-2.5 shrink-0">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-redd-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-redd-500" />
        </span>

        {/* Label */}
        <span className="text-xs text-slate-300 whitespace-nowrap">
          Generating images... {completed} of {total}
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
    </div>
  );
};
