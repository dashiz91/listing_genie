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
  /** Compact mode for smaller slots */
  compact?: boolean;
}

const GENERATION_STEPS = [
  { label: 'Analyzing product', icon: '🔍', description: 'Understanding your product' },
  { label: 'Composing layout', icon: '📐', description: 'Planning the perfect composition' },
  { label: 'Rendering image', icon: '🎨', description: 'Bringing your vision to life' },
  { label: 'Applying style', icon: '✨', description: 'Adding the finishing touches' },
  { label: 'Finalizing', icon: '🖼️', description: 'Almost ready!' },
];

// Rotating tips/messages for engagement
const LOADING_MESSAGES = [
  "AI is crafting your perfect listing image...",
  "Analyzing product features and colors...",
  "Composing a conversion-optimized layout...",
  "Applying professional e-commerce styling...",
  "Making your product stand out...",
  "Creating visual impact for shoppers...",
];

/**
 * GenerationLoader - Engaging loading state for image generation
 * Features: progress steps, shimmer animation, time estimate, rotating messages
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
  compact = false,
}) => {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [internalStep, setInternalStep] = useState(0);
  const [messageIndex, setMessageIndex] = useState(0);

  // Use external step if provided, otherwise auto-advance
  const currentStep = externalStep ?? internalStep;

  // Timer for elapsed time
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Rotate loading messages
  useEffect(() => {
    const messageTimer = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
    }, 3000);
    return () => clearInterval(messageTimer);
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

  // Progress percentage (with slight overshoot to feel responsive)
  const progress = Math.min(95, (elapsedSeconds / estimatedSeconds) * 100);

  // Aspect ratio to padding-bottom for responsive sizing
  const aspectPadding = useMemo(() => {
    switch (aspectRatio) {
      case '21:9': return '42.86%';
      case '16:9': return '56.25%';
      case '4:3': return '75%';
      default: return '100%';
    }
  }, [aspectRatio]);

  // Format image type for display
  const formatImageType = (type: string) => {
    return type
      .replace(/_/g, ' ')
      .replace(/aplus/i, 'A+')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (compact) {
    // Compact version for small slots
    return (
      <div className={cn('w-full h-full flex flex-col items-center justify-center bg-slate-800/80 rounded-lg p-4', className)}>
        {/* Animated spinner */}
        <div className="relative mb-3">
          <div
            className="w-12 h-12 rounded-full border-3 border-slate-600 border-t-transparent animate-spin"
            style={{ borderTopColor: accentColor }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-lg">{GENERATION_STEPS[currentStep]?.icon || '✨'}</span>
          </div>
        </div>

        {/* Simple progress bar */}
        <div className="w-full max-w-[120px] h-1.5 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${progress}%`,
              background: `linear-gradient(90deg, ${accentColor}, ${accentColor}cc)`,
            }}
          />
        </div>

        <p className="text-xs text-slate-400 mt-2">{GENERATION_STEPS[currentStep]?.label}</p>
      </div>
    );
  }

  return (
    <div className={cn('w-full', className)}>
      {/* Shimmer container with aspect ratio */}
      <div
        className="relative w-full overflow-hidden rounded-xl bg-gradient-to-br from-slate-800 to-slate-900"
        style={{ paddingBottom: aspectPadding }}
      >
        {/* Animated background layers */}
        <div className="absolute inset-0">
          {/* Gradient mesh background */}
          <div
            className="absolute inset-0 opacity-20 animate-gradient-flow"
            style={{
              background: `linear-gradient(45deg, ${accentColor}33, transparent 40%, ${accentColor}22 60%, transparent)`,
              backgroundSize: '400% 400%',
            }}
          />

          {/* Moving shimmer effect */}
          <div
            className="absolute inset-0 animate-shimmer"
            style={{
              background: `linear-gradient(90deg, transparent 0%, ${accentColor}22 25%, ${accentColor}44 50%, ${accentColor}22 75%, transparent 100%)`,
              backgroundSize: '200% 100%',
            }}
          />

          {/* Pulsing center glow */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div
              className="w-40 h-40 rounded-full animate-pulse-soft"
              style={{
                background: `radial-gradient(circle, ${accentColor}55 0%, ${accentColor}22 40%, transparent 70%)`,
              }}
            />
          </div>

          {/* Floating particles effect */}
          <div className="absolute inset-0 overflow-hidden">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="absolute w-2 h-2 rounded-full animate-float opacity-30"
                style={{
                  background: accentColor,
                  left: `${15 + i * 20}%`,
                  top: `${20 + (i % 3) * 25}%`,
                  animationDelay: `${i * 0.5}s`,
                }}
              />
            ))}
          </div>
        </div>

        {/* Content overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6">
          {/* Current step indicator with icon */}
          <div className="text-center mb-6">
            <div className="relative inline-block">
              <span className="text-5xl block animate-float">
                {GENERATION_STEPS[currentStep]?.icon || '✨'}
              </span>
              {/* Glow ring around icon */}
              <div
                className="absolute inset-0 rounded-full animate-pulse-soft -z-10 scale-150 blur-xl"
                style={{ background: `${accentColor}44` }}
              />
            </div>
            <p className="text-white font-semibold text-xl mt-4">
              {GENERATION_STEPS[currentStep]?.label || 'Processing...'}
            </p>
            <p className="text-slate-400 text-sm mt-1">
              {GENERATION_STEPS[currentStep]?.description}
            </p>
          </div>

          {/* Enhanced progress bar */}
          <div className="w-full max-w-sm">
            <div className="h-3 bg-slate-700/60 rounded-full overflow-hidden backdrop-blur-sm border border-slate-600/30">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out relative overflow-hidden"
                style={{
                  width: `${progress}%`,
                  background: `linear-gradient(90deg, ${accentColor}, ${accentColor}dd, ${accentColor})`,
                }}
              >
                {/* Shine effect on progress bar */}
                <div
                  className="absolute inset-0 animate-shimmer"
                  style={{
                    background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%)',
                    backgroundSize: '200% 100%',
                  }}
                />
              </div>
            </div>

            {/* Time display */}
            <div className="flex justify-between mt-3 text-sm">
              <span className="text-slate-400 flex items-center gap-1">
                <span className="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                {elapsedSeconds}s
              </span>
              <span className="text-slate-500">
                ~{remainingSeconds > 0 ? `${remainingSeconds}s remaining` : 'Finishing up...'}
              </span>
            </div>
          </div>

          {/* Step indicators */}
          <div className="flex items-center gap-3 mt-6">
            {GENERATION_STEPS.map((step, index) => (
              <div
                key={step.label}
                className={cn(
                  'transition-all duration-500 rounded-full',
                  index < currentStep
                    ? 'w-3 h-3 bg-green-500'
                    : index === currentStep
                    ? 'w-4 h-4 animate-pulse'
                    : 'w-2 h-2 bg-slate-600'
                )}
                style={{
                  backgroundColor: index === currentStep ? accentColor : undefined,
                  boxShadow: index === currentStep ? `0 0 10px ${accentColor}` : undefined,
                }}
                title={step.label}
              />
            ))}
          </div>

          {/* Rotating message */}
          <p className="text-slate-400 text-sm mt-4 animate-pulse">
            {LOADING_MESSAGES[messageIndex]}
          </p>
        </div>
      </div>

      {/* Optional: Show prompt preview */}
      {showPrompt && promptText && (
        <div className="mt-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50 backdrop-blur-sm">
          <p className="text-xs text-slate-500 mb-1 flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-redd-500"></span>
            AI Designer prompt:
          </p>
          <p className="text-sm text-slate-400 line-clamp-2 italic">
            "{promptText.slice(0, 200)}..."
          </p>
        </div>
      )}

      {/* Image type label */}
      <div className="mt-4 text-center">
        <span className="inline-flex items-center gap-2 text-sm text-slate-500 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700/30">
          <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: accentColor }}></span>
          Creating {formatImageType(imageType)}
        </span>
      </div>
    </div>
  );
};

export default GenerationLoader;
