import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { GenerationLoader } from '../generation-loader';

interface MainImageViewerProps {
  imageUrl: string;
  imageLabel: string;
  imageType: string;
  isProcessing?: boolean;
  isPending?: boolean;
  accentColor?: string;
  onGenerate?: () => void;
  overlay?: React.ReactNode;
  // On-image action bar (coexists with zoom)
  versionInfo?: { current: number; total: number };
  onPreviousVersion?: () => void;
  onNextVersion?: () => void;
  onRegenerate?: () => void;
  onEdit?: () => void;
  onDownload?: () => void;
  onViewPrompt?: () => void;
  onCancel?: () => void;
  className?: string;
}

export const MainImageViewer: React.FC<MainImageViewerProps> = ({
  imageUrl,
  imageLabel,
  imageType,
  isProcessing = false,
  isPending = false,
  accentColor = '#C85A35',
  onGenerate,
  overlay,
  versionInfo,
  onPreviousVersion,
  onNextVersion,
  onRegenerate,
  onEdit,
  onDownload,
  onViewPrompt,
  onCancel,
  className,
}) => {

  const [isHovering, setIsHovering] = useState(false);
  const [isOverActionBar, setIsOverActionBar] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 50, y: 50 });
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [isImageError, setIsImageError] = useState(false);
  const [previousUrl, setPreviousUrl] = useState<string | null>(null);
  const [showStuckHint, setShowStuckHint] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const hasActions = !!(onRegenerate || onEdit || onDownload || onViewPrompt);
  const hasVersions = versionInfo && versionInfo.total > 1;
  const canGoLeft = versionInfo ? versionInfo.current > 1 : false;
  const canGoRight = versionInfo ? versionInfo.current < versionInfo.total : false;

  // Zoom only active when hovering image but NOT the action bar
  const zoomActive = isHovering && !isOverActionBar;

  // Show cancel/retry actions after 5 seconds of processing
  useEffect(() => {
    if (!isProcessing) {
      setShowStuckHint(false);
      return;
    }
    const timer = setTimeout(() => setShowStuckHint(true), 5000);
    return () => clearTimeout(timer);
  }, [isProcessing]);

  // Track image URL changes for crossfade effect
  useEffect(() => {
    if (imageUrl !== previousUrl) {
      setIsImageLoaded(false);
      setIsImageError(false);
      setPreviousUrl(imageUrl);
    }
  }, [imageUrl, previousUrl]);

  const handleImageLoad = () => {
    setIsImageLoaded(true);
    setIsImageError(false);
  };

  const handleImageError = () => {
    setIsImageError(true);
    setIsImageLoaded(false);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    // Clamp values to prevent edge issues
    setMousePosition({
      x: Math.max(0, Math.min(100, x)),
      y: Math.max(0, Math.min(100, y)),
    });
  };

  // Pending state - show generate button
  if (isPending && onGenerate) {
    return (
      <div className={cn('relative', className)}>
        <div className="aspect-square bg-slate-100 rounded-lg flex flex-col items-center justify-center border-2 border-dashed border-slate-300 hover:border-redd-500/50 transition-colors cursor-pointer group"
          onClick={onGenerate}
        >
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-all group-hover:scale-110"
            style={{ backgroundColor: `${accentColor}20` }}
          >
            <svg
              className="w-8 h-8 transition-colors"
              style={{ color: accentColor }}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-slate-600 font-medium text-sm mb-1">Click to Generate</p>
          <p className="text-slate-400 text-xs">{imageLabel}</p>
        </div>
      </div>
    );
  }

  // Processing state - show loader
  if (isProcessing) {
    return (
      <div className={cn('relative', className)}>
        <GenerationLoader
          imageType={imageType}
          aspectRatio="1:1"
          accentColor={accentColor}
          estimatedSeconds={12}
          className="rounded-lg overflow-hidden"
        />
        {showStuckHint && onCancel && (
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10">
            <button
              onClick={onCancel}
              className="text-xs font-medium text-slate-700 bg-white/90 hover:bg-white px-3 py-1.5 rounded-md transition-colors shadow-sm border border-slate-300"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={cn('relative', className)}>
      {/* Main image container */}
      <div
        ref={containerRef}
        className="relative aspect-square bg-white rounded-lg overflow-hidden cursor-crosshair"
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
        onMouseMove={handleMouseMove}
        role="img"
        aria-label={imageLabel}
      >
        {/* Loading skeleton */}
        {!isImageLoaded && !isImageError && (
          <div className="absolute inset-0 bg-slate-100 animate-pulse flex items-center justify-center">
            <div className="w-12 h-12 border-4 border-slate-300 border-t-redd-500 rounded-full animate-spin" />
          </div>
        )}

        {/* Error state — image failed to load */}
        {isImageError && (
          <div className="absolute inset-0 bg-slate-50 flex flex-col items-center justify-center">
            <svg className="w-12 h-12 text-slate-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-sm text-slate-400 font-medium">Image unavailable</p>
            <p className="text-xs text-slate-300 mt-1">Signed URL may have expired</p>
            {onRegenerate && (
              <button
                onClick={onRegenerate}
                className="mt-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
                style={{ backgroundColor: `${accentColor}15`, color: accentColor }}
              >
                Regenerate
              </button>
            )}
          </div>
        )}

        {/* Main Image with crossfade */}
        <img
          src={imageUrl}
          alt={imageLabel}
          className={cn(
            'w-full h-full object-contain transition-opacity duration-300',
            isImageLoaded ? 'opacity-100' : 'opacity-0'
          )}
          draggable={false}
          onLoad={handleImageLoad}
          onError={handleImageError}
        />

        {/* Zoom lens overlay (Amazon-style square) */}
        {zoomActive && (
          <div
            className="absolute pointer-events-none border-2 border-redd-500/60 bg-redd-500/10 transition-opacity duration-150"
            style={{
              width: '120px',
              height: '120px',
              left: `calc(${mousePosition.x}% - 60px)`,
              top: `calc(${mousePosition.y}% - 60px)`,
            }}
          />
        )}

        {/* Action overlay (legacy — used in fullscreen) */}
        {overlay}

        {/* Version arrows on sides — always visible when multiple versions */}
        {hasVersions && (
          <>
            <button
              onClick={(e) => { e.stopPropagation(); canGoLeft && onPreviousVersion?.(); }}
              onMouseEnter={() => setIsOverActionBar(true)}
              onMouseLeave={() => setIsOverActionBar(false)}
              className={cn(
                "absolute z-20 left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 flex items-center justify-center transition-opacity",
                canGoLeft ? "hover:bg-black/70 opacity-80" : "opacity-30 cursor-default"
              )}
            >
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); canGoRight && onNextVersion?.(); }}
              onMouseEnter={() => setIsOverActionBar(true)}
              onMouseLeave={() => setIsOverActionBar(false)}
              className={cn(
                "absolute z-20 right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 flex items-center justify-center transition-opacity",
                canGoRight ? "hover:bg-black/70 opacity-80" : "opacity-30 cursor-default"
              )}
            >
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
            {/* Version badge */}
            <div className="absolute z-20 bottom-10 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-black/50 rounded-full">
              <span className="text-xs text-white font-medium">
                v{versionInfo.current}/{versionInfo.total}
              </span>
            </div>
          </>
        )}

        {/* Bottom action bar — appears on hover, compact so zoom still works above */}
        {hasActions && isHovering && !isProcessing && (
          <div
            className="absolute z-20 bottom-0 inset-x-0 flex items-center justify-center gap-2 py-2 px-3 bg-gradient-to-t from-black/60 to-transparent"
            onMouseEnter={() => setIsOverActionBar(true)}
            onMouseLeave={() => setIsOverActionBar(false)}
          >
            {onRegenerate && (
              <button
                onClick={(e) => { e.stopPropagation(); onRegenerate(); }}
                className="px-3 py-1.5 bg-white/90 rounded-md text-xs font-medium text-gray-800 hover:bg-white transition-colors shadow flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Regenerate
              </button>
            )}
            {onEdit && (
              <button
                onClick={(e) => { e.stopPropagation(); onEdit(); }}
                className="px-3 py-1.5 bg-white/90 rounded-md text-xs font-medium text-gray-800 hover:bg-white transition-colors shadow flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
            )}
            {onDownload && (
              <button
                onClick={(e) => { e.stopPropagation(); onDownload(); }}
                className="px-3 py-1.5 bg-white/90 rounded-md text-xs font-medium text-gray-800 hover:bg-white transition-colors shadow flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download
              </button>
            )}
            {onViewPrompt && (
              <button
                onClick={(e) => { e.stopPropagation(); onViewPrompt(); }}
                className="px-3 py-1.5 bg-white/90 rounded-md text-xs font-medium text-gray-800 hover:bg-white transition-colors shadow flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Prompt
              </button>
            )}
          </div>
        )}

        {/* Image type badge */}
        <div className={cn(
          "absolute left-3 px-2 py-1 bg-slate-900/80 backdrop-blur-sm rounded text-xs text-white font-medium",
          hasVersions ? "bottom-10" : "bottom-3"
        )}>
          {imageLabel}
        </div>

        {/* Zoom hint */}
        {!isHovering && (
          <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2 py-1 bg-slate-900/80 backdrop-blur-sm rounded text-xs text-slate-300">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
              />
            </svg>
            <span>Hover to zoom</span>
          </div>
        )}
      </div>

      {/* Zoomed preview panel (appears on right when hovering) */}
      {zoomActive && (
        <div
          className="absolute left-full top-0 ml-4 w-80 h-80 bg-white rounded-lg border border-slate-200 shadow-xl overflow-hidden z-10 hidden lg:block"
        >
          <div
            className="w-full h-full"
            style={{
              backgroundImage: `url(${imageUrl})`,
              backgroundSize: '300%',
              backgroundPosition: `${mousePosition.x}% ${mousePosition.y}%`,
              backgroundRepeat: 'no-repeat',
            }}
          />
          <div className="absolute bottom-2 left-2 right-2 text-center">
            <span className="px-2 py-1 bg-slate-900/80 backdrop-blur-sm rounded text-xs text-white">
              3x Zoom
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
