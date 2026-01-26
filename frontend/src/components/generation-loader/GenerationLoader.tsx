import React, { useState, useEffect, useMemo } from 'react';
import { cn } from '@/lib/utils';

interface GenerationLoaderProps {
  /** Type of image being generated */
  imageType: string;
  /** Estimated time in seconds */
  estimatedSeconds?: number;
  /** Current step (0-4) */
  currentStep?: number;
  /** Framework primary color for theming */
  accentColor?: string;
  /** Show the prompt being used */
  showPrompt?: boolean;
  /** The prompt text (truncated) */
  promptText?: string;
  /** Aspect ratio for sizing */
  aspectRatio?: '1:1' | '21:9' | '16:9' | '4:3';
  /** Additional class names */
  className?: string;
}

const GENERATION_STEPS = [
  { label: 'Analyzing product', icon: '🔍' },
  { label: 'Composing layout', icon: '📐' },
  { label: 'Rendering image', icon: '🎨' },
  { label: 'Applying style', icon: '✨' },
  { label: 'Finalizing', icon: '🖼️' },
];

/**
 * GenerationLoader - Engaging loading state for image generation
 * Shows progress steps, shimmer animation, and time estimate
 */
export const GenerationLoader: React.FC<GenerationLoaderProps> = ({
  imageType,
  estimatedSeconds = 8,
  currentStep: externalStep,
  accentColor = '#C85A35',
  showPrompt = false,
  promptText,
  aspectRatio = '1:1',
  className,
}) => {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [internalStep, setInternalStep] = useState(0);

  // Use external step if provided, otherwise auto-advance
  const currentStep = externalStep ?? internalStep;

  // Timer for elapsed time
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Auto-advance steps if not externally controlled
  useEffect(() => {
    if (externalStep !== undefined) return;

    const stepDuration = (estimatedSeconds * 1000) / GENERATION_STEPS.length;
    const stepTimer = setInterval(() => {
      setInternalStep((prev) => Math.min(prev + 1, GENERATION_STEPS.length - 1));
    }, stepDuration);

    return () => clearInterval(stepTimer);
  }, [estimatedSeconds, externalStep]);

  // Calculate remaining time
  const remainingSeconds = Math.max(0, estimatedSeconds - elapsedSeconds);

  // Progress percentage
  const progress = Math.min(100, (elapsedSeconds / estimatedSeconds) * 100);

  // Aspect ratio to padding-bottom for responsive sizing
  const aspectPadding = useMemo(() => {
    switch (aspectRatio) {
      case '21:9': return '42.86%'; // 9/21 * 100
      case '16:9': return '56.25%'; // 9/16 * 100
      case '4:3': return '75%';     // 3/4 * 100
      default: return '100%';       // 1:1
    }
  }, [aspectRatio]);

  return (
    <div className={cn('w-full', className)}>
      {/* Shimmer container with aspect ratio */}
      <div
        className="relative w-full overflow-hidden rounded-xl bg-slate-800"
        style={{ paddingBottom: aspectPadding }}
      >
        {/* Shimmer animation */}
        <div className="absolute inset-0">
          {/* Base gradient */}
          <div
            className="absolute inset-0 opacity-30"
            style={{
              background: `linear-gradient(135deg, ${accentColor}22 0%, transparent 50%, ${accentColor}22 100%)`,
            }}
          />

          {/* Moving shimmer */}
          <div
            className="absolute inset-0 animate-shimmer"
            style={{
              background: `linear-gradient(90deg, transparent 0%, ${accentColor}33 50%, transparent 100%)`,
              backgroundSize: '200% 100%',
            }}
          />

          {/* Pulsing center glow */}
          <div
            className="absolute inset-0 flex items-center justify-center"
          >
            <div
              className="w-32 h-32 rounded-full animate-pulse-soft opacity-40"
              style={{
                background: `radial-gradient(circle, ${accentColor}66 0%, transparent 70%)`,
              }}
            />
          </div>
        </div>

        {/* Content overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6">
          {/* Current step indicator */}
          <div className="text-center mb-4">
            <span className="text-3xl mb-2 block animate-bounce">
              {GENERATION_STEPS[currentStep]?.icon || '✨'}
            </span>
            <p className="text-white font-medium text-lg">
              {GENERATION_STEPS[currentStep]?.label || 'Processing...'}
            </p>
          </div>

          {/* Progress bar */}
          <div className="w-full max-w-xs">
            <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500 ease-out"
                style={{
                  width: `${progress}%`,
                  background: `linear-gradient(90deg, ${accentColor}, ${accentColor}cc)`,
                }}
              />
            </div>

            {/* Time estimate */}
            <div className="flex justify-between mt-2 text-sm">
              <span className="text-slate-400">
                {elapsedSeconds}s elapsed
              </span>
              <span className="text-slate-400">
                ~{remainingSeconds}s remaining
              </span>
            </div>
          </div>

          {/* Step indicators */}
          <div className="flex items-center gap-2 mt-4">
            {GENERATION_STEPS.map((step, index) => (
              <div
                key={step.label}
                className={cn(
                  'w-2 h-2 rounded-full transition-all duration-300',
                  index < currentStep
                    ? 'bg-green-500'
                    : index === currentStep
                    ? 'bg-white animate-pulse'
                    : 'bg-slate-600'
                )}
                title={step.label}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Optional: Show prompt preview */}
      {showPrompt && promptText && (
        <div className="mt-3 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
          <p className="text-xs text-slate-500 mb-1">AI Designer prompt:</p>
          <p className="text-sm text-slate-400 line-clamp-2 italic">
            "{promptText.slice(0, 150)}..."
          </p>
        </div>
      )}

      {/* Image type label */}
      <div className="mt-3 text-center">
        <span className="text-sm text-slate-500">
          Creating {imageType}
        </span>
      </div>
    </div>
  );
};

export default GenerationLoader;
