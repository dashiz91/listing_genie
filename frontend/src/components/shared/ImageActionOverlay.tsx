import React, { useState } from 'react';
import { cn } from '@/lib/utils';

export interface ImageActionOverlayProps {
  // Version navigation
  versionInfo: { current: number; total: number };
  onPreviousVersion?: () => void;
  onNextVersion?: () => void;
  // Actions
  onRegenerate?: () => void;
  onEdit?: () => void;
  onDownload?: () => void;
  onViewPrompt?: () => void;
  onMobileTransform?: () => void;
  // State
  isProcessing?: boolean;
  className?: string;
  // Optional label shown on hover (for A+ modules)
  label?: string;
}

export const ImageActionOverlay: React.FC<ImageActionOverlayProps> = ({
  versionInfo,
  onPreviousVersion,
  onNextVersion,
  onRegenerate,
  onEdit,
  onDownload,
  onViewPrompt,
  onMobileTransform,
  isProcessing = false,
  className,
  label,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const hasMultipleVersions = versionInfo.total > 1;
  const canGoLeft = versionInfo.current > 1;
  const canGoRight = versionInfo.current < versionInfo.total;

  return (
    <div
      className={cn('absolute inset-0 z-10', className)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Hover overlay with action buttons */}
      {isHovered && !isProcessing && (
        <div className="absolute inset-0 bg-black/40 flex flex-col items-center justify-center gap-3 transition-opacity">
          {/* Module label (if provided) */}
          {label && (
            <div className="absolute top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-black/60 rounded-full">
              <span className="text-xs font-medium text-white uppercase tracking-wider">{label}</span>
            </div>
          )}
          <div className="flex items-center gap-3">
          {onRegenerate && (
            <button
              onClick={(e) => { e.stopPropagation(); onRegenerate(); }}
              className="px-4 py-2 bg-white rounded-lg text-sm font-medium text-gray-800 hover:bg-gray-100 transition-colors shadow-lg flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Regenerate
            </button>
          )}
          {onEdit && (
            <button
              onClick={(e) => { e.stopPropagation(); onEdit(); }}
              className="px-4 py-2 bg-white rounded-lg text-sm font-medium text-gray-800 hover:bg-gray-100 transition-colors shadow-lg flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </button>
          )}
          {onDownload && (
            <button
              onClick={(e) => { e.stopPropagation(); onDownload(); }}
              className="px-4 py-2 bg-white/90 rounded-lg text-sm font-medium text-gray-800 hover:bg-white transition-colors shadow-lg flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
          )}
          {onViewPrompt && (
            <button
              onClick={(e) => { e.stopPropagation(); onViewPrompt(); }}
              className="px-4 py-2 bg-white/90 rounded-lg text-sm font-medium text-gray-800 hover:bg-white transition-colors shadow-lg flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Prompt
            </button>
          )}
          {onMobileTransform && (
            <button
              onClick={(e) => { e.stopPropagation(); onMobileTransform(); }}
              className="px-4 py-2 bg-blue-500 rounded-lg text-sm font-medium text-white hover:bg-blue-600 transition-colors shadow-lg flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              To Mobile
            </button>
          )}
          </div>
        </div>
      )}

      {/* Version arrows — always visible when multiple versions */}
      {hasMultipleVersions && (
        <>
          <button
            onClick={(e) => { e.stopPropagation(); canGoLeft && onPreviousVersion?.(); }}
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
            className={cn(
              "absolute z-20 right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/50 flex items-center justify-center transition-opacity",
              canGoRight ? "hover:bg-black/70 opacity-80" : "opacity-30 cursor-default"
            )}
          >
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <div className="absolute z-20 bottom-2 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-black/50 rounded-full">
            <span className="text-xs text-white font-medium">
              v{versionInfo.current}/{versionInfo.total}
            </span>
          </div>
        </>
      )}
    </div>
  );
};

export default ImageActionOverlay;
