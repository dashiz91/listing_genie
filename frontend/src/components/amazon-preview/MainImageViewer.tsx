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
  className,
}) => {

  const [isHovering, setIsHovering] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 50, y: 50 });
  const [isImageLoaded, setIsImageLoaded] = useState(false);
  const [previousUrl, setPreviousUrl] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Track image URL changes for crossfade effect
  useEffect(() => {
    if (imageUrl !== previousUrl) {
      setIsImageLoaded(false);
      setPreviousUrl(imageUrl);
    }
  }, [imageUrl, previousUrl]);

  const handleImageLoad = () => {
    setIsImageLoaded(true);
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
        {!isImageLoaded && (
          <div className="absolute inset-0 bg-slate-100 animate-pulse flex items-center justify-center">
            <div className="w-12 h-12 border-4 border-slate-300 border-t-redd-500 rounded-full animate-spin" />
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
        />

        {/* Zoom lens overlay (Amazon-style square) */}
        {isHovering && (
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

        {/* Image type badge */}
        <div className="absolute bottom-3 left-3 px-2 py-1 bg-slate-900/80 backdrop-blur-sm rounded text-xs text-white font-medium">
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
      {isHovering && (
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
