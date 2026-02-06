import React from 'react';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';

type DeviceMode = 'desktop' | 'mobile';

interface PreviewToolbarProps {
  deviceMode: DeviceMode;
  onDeviceModeChange: (mode: DeviceMode) => void;
  onDownloadAll: () => void;
  onStartOver: () => void;
  onFullscreen?: () => void;
  isDownloading?: boolean;
  isFullscreen?: boolean;
  hasCompleteImages?: boolean;
  className?: string;
}

export const PreviewToolbar: React.FC<PreviewToolbarProps> = ({
  deviceMode,
  onDeviceModeChange,
  onDownloadAll,
  onStartOver,
  onFullscreen,
  isDownloading = false,
  isFullscreen = false,
  hasCompleteImages = true,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex flex-wrap items-center justify-between gap-4 p-4 bg-slate-800/50 border border-slate-700 rounded-xl',
        className
      )}
    >
      {/* Left side - Device Toggle */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-slate-400 mr-2">Preview:</span>
        <div className="flex bg-slate-900 rounded-lg p-1">
          <button
            onClick={() => onDeviceModeChange('desktop')}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              deviceMode === 'desktop'
                ? 'bg-slate-700 text-white'
                : 'text-slate-400 hover:text-white'
            )}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            <span className="hidden sm:inline">Desktop</span>
          </button>
          <button
            onClick={() => onDeviceModeChange('mobile')}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              deviceMode === 'mobile'
                ? 'bg-slate-700 text-white'
                : 'text-slate-400 hover:text-white'
            )}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
              />
            </svg>
            <span className="hidden sm:inline">Mobile</span>
          </button>
        </div>

        {/* Fullscreen Button */}
        {onFullscreen && (
          <button
            onClick={onFullscreen}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              'text-slate-400 hover:text-white hover:bg-slate-700'
            )}
            title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            )}
            <span className="hidden sm:inline">{isFullscreen ? 'Exit' : 'Fullscreen'}</span>
          </button>
        )}

      </div>

      {/* Right side - Actions */}
      <div className="flex items-center gap-2">
        {/* Download All Button */}
        <button
          onClick={onDownloadAll}
          disabled={isDownloading || !hasCompleteImages}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            'bg-redd-500 text-white hover:bg-redd-600',
            'disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed'
          )}
        >
          {isDownloading ? (
            <>
              <Spinner size="sm" className="text-white" />
              <span>Downloading...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              <span>Download All</span>
            </>
          )}
        </button>

        {/* New Project Button */}
        <button
          onClick={onStartOver}
          className="flex items-center gap-2 px-4 py-2 bg-slate-700 text-white text-sm font-medium rounded-lg hover:bg-slate-600 transition-colors border border-slate-600"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span className="hidden sm:inline">New Project</span>
        </button>
      </div>
    </div>
  );
};
