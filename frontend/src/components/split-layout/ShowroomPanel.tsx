import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { apiClient } from '@/api/client';
import type { SessionImage, DesignFramework } from '@/api/types';
import type { UploadWithPreview } from '../ImageUploader';
import { LivePreview, PreviewState } from '../live-preview/LivePreview';
import { AmazonListingPreview } from '../amazon-preview';

interface ShowroomPanelProps {
  // Preview state
  previewState: PreviewState;

  // Product info
  productTitle: string;
  brandName?: string;
  features: string[];
  targetAudience?: string;

  // Uploads
  productImages: UploadWithPreview[];

  // Framework
  selectedFramework?: DesignFramework;

  // Generation
  sessionId?: string;
  images: SessionImage[];

  // Callbacks
  onRegenerateSingle?: (imageType: string, note?: string) => void;
  onEditSingle?: (imageType: string, instructions: string) => void;
  onRetry?: () => void;
  onStartOver?: () => void;

  className?: string;
}

/**
 * ShowroomPanel - Right side panel containing the live preview
 * Shows simple LivePreview during form filling, switches to full AmazonListingPreview after generation
 */
export const ShowroomPanel: React.FC<ShowroomPanelProps> = ({
  previewState,
  productTitle,
  brandName,
  features,
  targetAudience,
  productImages,
  selectedFramework,
  sessionId,
  images,
  onRegenerateSingle,
  onEditSingle,
  onRetry,
  onStartOver,
  className,
}) => {
  const [deviceMode, setDeviceMode] = useState<'desktop' | 'mobile'>('desktop');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedImageType, setSelectedImageType] = useState('main');

  // Get image URL with optional cache busting
  const getImageUrl = useCallback(
    (imageType: string) => {
      if (!sessionId) return '';
      return apiClient.getImageUrl(sessionId, imageType);
    },
    [sessionId]
  );

  // Calculate generation progress
  const completeCount = images.filter((img) => img.status === 'complete').length;
  const totalImages = images.length || 5;
  const generationProgress = totalImages > 0 ? (completeCount / totalImages) * 100 : 0;

  // Toggle fullscreen
  const handleFullscreenToggle = useCallback(() => {
    setIsFullscreen((prev) => !prev);
  }, []);

  // For completed generation, use the full AmazonListingPreview with all features
  if (previewState === 'complete' && sessionId) {
    return (
      <div className={cn('h-full flex flex-col', className)}>
        {/* Fullscreen overlay */}
        {isFullscreen && (
          <div className="fixed inset-0 z-50 bg-slate-900 flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
              <h2 className="text-white font-medium">Amazon Listing Preview</h2>
              <button
                onClick={handleFullscreenToggle}
                className="p-2 text-slate-400 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="flex-1 overflow-auto p-8">
              <AmazonListingPreview
                productTitle={productTitle}
                brandName={brandName}
                features={features.filter(Boolean).map(f => f || '')}
                targetAudience={targetAudience}
                sessionId={sessionId}
                images={images}
                framework={selectedFramework}
                onRetry={onRetry}
                onRegenerateSingle={onRegenerateSingle}
                onEditSingle={onEditSingle}
                onStartOver={onStartOver}
              />
            </div>
          </div>
        )}

        {/* Normal view */}
        <div className="flex-1 overflow-auto">
          <AmazonListingPreview
            productTitle={productTitle}
            brandName={brandName}
            features={features.filter(Boolean).map(f => f || '')}
            targetAudience={targetAudience}
            sessionId={sessionId}
            images={images}
            framework={selectedFramework}
            onRetry={onRetry}
            onRegenerateSingle={onRegenerateSingle}
            onEditSingle={onEditSingle}
            onStartOver={onStartOver}
          />
        </div>
      </div>
    );
  }

  // For all other states, use the simplified LivePreview
  return (
    <div className={cn('h-full flex flex-col', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">Preview</h2>
        <div className="flex items-center gap-2">
          {/* Device mode toggle - only show when we have content */}
          {(previewState !== 'empty') && (
            <div className="flex items-center rounded-lg bg-slate-700 p-0.5">
              <button
                onClick={() => setDeviceMode('desktop')}
                className={cn(
                  'px-3 py-1 text-xs font-medium rounded transition-colors',
                  deviceMode === 'desktop' ? 'bg-slate-600 text-white' : 'text-slate-400 hover:text-white'
                )}
              >
                Desktop
              </button>
              <button
                onClick={() => setDeviceMode('mobile')}
                className={cn(
                  'px-3 py-1 text-xs font-medium rounded transition-colors',
                  deviceMode === 'mobile' ? 'bg-slate-600 text-white' : 'text-slate-400 hover:text-white'
                )}
              >
                Mobile
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Live Preview */}
      <div className="flex-1 overflow-auto">
        <LivePreview
          state={previewState}
          productTitle={productTitle}
          brandName={brandName}
          features={features}
          productImages={productImages}
          selectedFramework={selectedFramework}
          sessionId={sessionId}
          images={images}
          generationProgress={generationProgress}
          deviceMode={deviceMode}
          onDeviceModeChange={setDeviceMode}
          isFullscreen={isFullscreen}
          onFullscreenToggle={handleFullscreenToggle}
          selectedImageType={selectedImageType}
          onSelectImage={setSelectedImageType}
          getImageUrl={getImageUrl}
        />
      </div>

      {/* Footer info based on state */}
      <div className="mt-4 pt-4 border-t border-slate-700">
        {previewState === 'empty' && (
          <p className="text-center text-sm text-slate-500">
            Upload product photos to see your listing preview
          </p>
        )}
        {previewState === 'photos_only' && (
          <p className="text-center text-sm text-slate-500">
            Add product details to see the full preview
          </p>
        )}
        {previewState === 'filling' && (
          <p className="text-center text-sm text-slate-500">
            Preview updates in real-time as you type
          </p>
        )}
        {previewState === 'framework_selected' && (
          <p className="text-center text-sm text-slate-500">
            Ready to generate your listing images
          </p>
        )}
        {previewState === 'generating' && (
          <p className="text-center text-sm text-slate-500">
            {completeCount} of {totalImages} images generated
          </p>
        )}
      </div>
    </div>
  );
};

export default ShowroomPanel;
