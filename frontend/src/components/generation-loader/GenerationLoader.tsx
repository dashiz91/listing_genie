import React, { useMemo } from 'react';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';

interface GenerationLoaderProps {
  /** Type of image being generated — used for narrative label */
  imageType: string;
  /** Aspect ratio for sizing */
  aspectRatio?: '1:1' | '21:9' | '16:9' | '4:3';
  /** Additional class names */
  className?: string;
  /** Compact mode for thumbnail slots */
  compact?: boolean;
}

/** Map image types to human-readable narrative labels */
const NARRATIVE_LABELS: Record<string, string> = {
  main: 'Creating Hero Image',
  infographic_1: 'Composing Infographic',
  infographic_2: 'Building Feature Grid',
  lifestyle: 'Composing Lifestyle Scene',
  transformation: 'Rendering Transformation',
  comparison: 'Designing Comparison',
  style_preview: 'Generating Style Preview',
};

const getNarrativeLabel = (imageType: string): string => {
  // Handle A+ module types like "aplus_0", "aplus_3"
  if (imageType.startsWith('aplus_')) {
    const idx = parseInt(imageType.split('_')[1], 10);
    if (idx <= 1) return 'Creating A+ Hero Module';
    return `Rendering A+ Module ${idx + 1}`;
  }
  // Handle mobile types
  if (imageType.startsWith('aplus_mobile_')) {
    return 'Transforming to Mobile';
  }
  return NARRATIVE_LABELS[imageType] || formatImageType(imageType);
};

const formatImageType = (type: string): string => {
  return type
    .replace(/_/g, ' ')
    .replace(/aplus/i, 'A+')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export const GenerationLoader: React.FC<GenerationLoaderProps> = ({
  imageType,
  aspectRatio = '1:1',
  className,
  compact = false,
}) => {
  const aspectPadding = useMemo(() => {
    switch (aspectRatio) {
      case '21:9': return '42.86%';
      case '16:9': return '56.25%';
      case '4:3': return '75%';
      default: return '100%';
    }
  }, [aspectRatio]);

  const narrativeLabel = getNarrativeLabel(imageType);

  if (compact) {
    return (
      <div className={cn(
        'w-full h-full flex flex-col items-center justify-center rounded-lg relative overflow-hidden',
        'bg-slate-800',
        className
      )}>
        {/* Shimmer background */}
        <div
          className="absolute inset-0 animate-shimmer pointer-events-none"
          style={{
            background: 'linear-gradient(90deg, transparent 0%, rgba(200,90,53,0.08) 50%, transparent 100%)',
            backgroundSize: '200% 100%',
          }}
        />

        <div className="relative z-10 flex flex-col items-center">
          <Spinner size="md" className="text-redd-500 mb-2" />
          <p className="text-[11px] text-slate-400 font-medium">{narrativeLabel}</p>
          {/* Thin shimmer bar */}
          <div className="w-16 h-0.5 bg-slate-700 rounded-full overflow-hidden mt-2">
            <div
              className="h-full rounded-full animate-shimmer"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, #C85A35 50%, transparent 100%)',
                backgroundSize: '200% 100%',
              }}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('w-full', className)}>
      {/* Main container with aspect ratio */}
      <div
        className="relative w-full overflow-hidden rounded-xl bg-gradient-to-br from-slate-800 to-slate-900"
        style={{ paddingBottom: aspectPadding }}
      >
        {/* Slow ambient gradient background */}
        <div className="absolute inset-0">
          <div
            className="absolute inset-0 opacity-30 animate-gradient-flow"
            style={{
              background: 'linear-gradient(45deg, rgba(200,90,53,0.15), transparent 40%, rgba(200,90,53,0.1) 60%, transparent)',
              backgroundSize: '400% 400%',
            }}
          />
          {/* Shimmer sweep */}
          <div
            className="absolute inset-0 animate-shimmer"
            style={{
              background: 'linear-gradient(90deg, transparent 0%, rgba(200,90,53,0.1) 25%, rgba(200,90,53,0.18) 50%, rgba(200,90,53,0.1) 75%, transparent 100%)',
              backgroundSize: '200% 100%',
            }}
          />
        </div>

        {/* Content overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6">
          <Spinner size="xl" className="text-redd-500 mb-5" />

          <p className="text-white font-semibold text-lg mb-1">
            {narrativeLabel}
          </p>

          {/* Thin indeterminate shimmer bar */}
          <div className="w-full max-w-[200px] h-1 bg-slate-700/60 rounded-full overflow-hidden mt-3">
            <div
              className="h-full rounded-full animate-shimmer"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, #C85A35 50%, transparent 100%)',
                backgroundSize: '200% 100%',
              }}
            />
          </div>

          <p className="text-slate-500 text-xs mt-3">
            This may take a minute
          </p>
        </div>
      </div>
    </div>
  );
};

export default GenerationLoader;
