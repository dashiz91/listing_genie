import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface MainImageViewerProps {
  imageUrl: string;
  imageLabel: string;
  imageType: string;
  isProcessing?: boolean;
  className?: string;
}

export const MainImageViewer: React.FC<MainImageViewerProps> = ({
  imageUrl,
  imageLabel,
  imageType: _imageType,
  isProcessing = false,
  className,
}) => {
  void _imageType; // Reserved for future use

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

  if (isProcessing) {
    return (
      <div
        className={cn(
          'relative aspect-square bg-slate-100 rounded-lg flex items-center justify-center',
          className
        )}
      >
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 border-4 border-redd-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-500 text-sm">Generating {imageLabel}...</p>
        </div>
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
