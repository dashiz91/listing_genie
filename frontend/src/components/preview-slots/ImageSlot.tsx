import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { GenerationLoader } from '../generation-loader';

export type SlotStatus = 'empty' | 'ready' | 'generating' | 'complete' | 'error' | 'locked';

interface ImageSlotProps {
  /** Unique identifier for this slot */
  slotId: string;
  /** Display label */
  label: string;
  /** Current status of this slot */
  status: SlotStatus;
  /** Image URL when complete */
  imageUrl?: string;
  /** Error message if failed */
  errorMessage?: string;
  /** Aspect ratio for sizing */
  aspectRatio?: '1:1' | '21:9' | '16:9' | '4:3';
  /** Accent color for theming */
  accentColor?: string;
  /** Whether this slot can be clicked to generate */
  canGenerate?: boolean;
  /** Called when user clicks to generate */
  onGenerate?: () => void;
  /** Called when user clicks to regenerate */
  onRegenerate?: () => void;
  /** Called when user clicks to edit */
  onEdit?: () => void;
  /** Locked reason (when status is 'locked') */
  lockedReason?: string;
  /** Show slot number/index */
  slotNumber?: number;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * ImageSlot - A clickable slot that shows different states during generation
 */
export const ImageSlot: React.FC<ImageSlotProps> = ({
  slotId: _slotId,
  label,
  status,
  imageUrl,
  errorMessage,
  aspectRatio = '1:1',
  accentColor = '#C85A35',
  canGenerate = true,
  onGenerate,
  onRegenerate,
  onEdit,
  lockedReason,
  slotNumber,
  size = 'md',
  className,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  // Aspect ratio to padding-bottom
  const aspectPadding = {
    '1:1': '100%',
    '21:9': '42.86%',
    '16:9': '56.25%',
    '4:3': '75%',
  }[aspectRatio];

  // Size classes
  const sizeClasses = {
    sm: 'min-w-[100px]',
    md: 'min-w-[150px]',
    lg: 'min-w-[200px]',
  }[size];

  const handleClick = () => {
    if (status === 'ready' && canGenerate && onGenerate) {
      onGenerate();
    }
  };

  return (
    <div
      className={cn(
        'relative rounded-xl overflow-hidden transition-all duration-300',
        sizeClasses,
        status === 'ready' && canGenerate && 'cursor-pointer',
        status === 'ready' && canGenerate && isHovered && 'ring-2 ring-offset-2 ring-offset-slate-900',
        status === 'locked' && 'opacity-50',
        className
      )}
      style={{
        ['--accent-color' as string]: accentColor,
        ['--tw-ring-color' as string]: status === 'ready' && canGenerate ? accentColor : undefined,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleClick}
    >
      {/* Aspect ratio container */}
      <div className="relative w-full" style={{ paddingBottom: aspectPadding }}>
        <div className="absolute inset-0">
          {/* Empty state */}
          {status === 'empty' && (
            <div className="w-full h-full bg-slate-800 border-2 border-dashed border-slate-600 rounded-xl flex flex-col items-center justify-center text-slate-500">
              <span className="text-2xl mb-1">📷</span>
              <span className="text-xs">No image</span>
            </div>
          )}

          {/* Ready state - clickable to generate */}
          {status === 'ready' && (
            <div
              className={cn(
                'w-full h-full bg-slate-800 border-2 rounded-xl flex flex-col items-center justify-center transition-all duration-300',
                isHovered ? 'border-solid bg-slate-700' : 'border-dashed border-slate-600'
              )}
              style={{ borderColor: isHovered ? accentColor : undefined }}
            >
              <div
                className={cn(
                  'w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300',
                  isHovered ? 'bg-opacity-100 scale-110' : 'bg-opacity-50'
                )}
                style={{ backgroundColor: isHovered ? accentColor : 'rgb(71 85 105)' }}
              >
                <svg
                  className={cn('w-6 h-6 transition-colors', isHovered ? 'text-white' : 'text-slate-300')}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className={cn('text-xs mt-2 transition-colors', isHovered ? 'text-white' : 'text-slate-400')}>
                Click to generate
              </span>
            </div>
          )}

          {/* Generating state */}
          {status === 'generating' && (
            <GenerationLoader
              imageType={label}
              aspectRatio={aspectRatio}
              accentColor={accentColor}
              estimatedSeconds={8}
              className="w-full h-full"
            />
          )}

          {/* Complete state - show image */}
          {status === 'complete' && imageUrl && (
            <div className="relative w-full h-full group">
              {/* Loading shimmer while image loads */}
              {!imageLoaded && (
                <div className="absolute inset-0 bg-slate-800 animate-pulse" />
              )}
              <img
                src={imageUrl}
                alt={label}
                className={cn(
                  'w-full h-full object-cover rounded-xl transition-opacity duration-500',
                  imageLoaded ? 'opacity-100 animate-image-reveal' : 'opacity-0'
                )}
                onLoad={() => setImageLoaded(true)}
              />
              {/* Hover overlay with actions */}
              <div className={cn(
                'absolute inset-0 bg-black/60 flex items-center justify-center gap-2 transition-opacity duration-200 rounded-xl',
                isHovered ? 'opacity-100' : 'opacity-0'
              )}>
                {onEdit && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onEdit(); }}
                    className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                )}
                {onRegenerate && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onRegenerate(); }}
                    className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                    title="Regenerate"
                  >
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Error state */}
          {status === 'error' && (
            <div className="w-full h-full bg-red-900/20 border-2 border-red-500/50 rounded-xl flex flex-col items-center justify-center p-4">
              <span className="text-2xl mb-2">❌</span>
              <span className="text-xs text-red-400 text-center">
                {errorMessage || 'Generation failed'}
              </span>
              {onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="mt-2 px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-300 text-xs rounded-lg transition-colors"
                >
                  Retry
                </button>
              )}
            </div>
          )}

          {/* Locked state */}
          {status === 'locked' && (
            <div className="w-full h-full bg-slate-800 border-2 border-slate-700 rounded-xl flex flex-col items-center justify-center text-slate-500">
              <span className="text-2xl mb-1">🔒</span>
              <span className="text-xs text-center px-2">
                {lockedReason || 'Waiting...'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Label */}
      <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-white truncate">
            {slotNumber !== undefined && (
              <span className="text-slate-400 mr-1">{slotNumber}.</span>
            )}
            {label}
          </span>
          {status === 'complete' && (
            <span className="text-green-400 text-xs">✓</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageSlot;
