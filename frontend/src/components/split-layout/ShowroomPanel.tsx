import React, { useState, useCallback } from 'react';
import { cn, normalizeColors } from '@/lib/utils';
import { apiClient } from '@/api/client';
import type { SessionImage, DesignFramework } from '@/api/types';
import type { UploadWithPreview } from '../ImageUploader';
import { LivePreview, PreviewState } from '../live-preview/LivePreview';
import { AmazonListingPreview } from '../amazon-preview';
import { AplusSection, type AplusModule, type AplusViewportMode } from '../preview-slots/AplusSection';
import type { ListingVersionState } from '@/pages/HomePage';

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
  isAnalyzing?: boolean;

  // Generation
  sessionId?: string;
  images: SessionImage[];

  // A+ Content modules
  aplusModules?: AplusModule[];
  aplusVisualScript?: import('@/api/types').AplusVisualScript | null;
  isGeneratingScript?: boolean;
  onGenerateAplusModule?: (moduleIndex: number) => void;
  onRegenerateAplusModule?: (moduleIndex: number, note?: string, referenceImagePaths?: string[]) => void;
  onGenerateAllAplus?: () => void;
  onRegenerateScript?: () => void;
  onReplanAll?: () => void;
  isReplanning?: boolean;
  onAplusVersionChange?: (moduleIndex: number, versionIndex: number) => void;
  onEditAplusModule?: (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => void;
  aplusViewportMode?: AplusViewportMode;
  onAplusViewportChange?: (mode: AplusViewportMode) => void;
  onGenerateMobileModule?: (moduleIndex: number) => void;
  onGenerateAllMobile?: () => void;
  onRegenerateMobileModule?: (moduleIndex: number, note?: string, referenceImagePaths?: string[]) => void;
  onEditMobileModule?: (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => void;
  onCancelAplusModule?: (moduleIndex: number, viewport: AplusViewportMode) => void;

  // Listing version tracking
  listingVersions?: ListingVersionState;
  onListingVersionChange?: (imageType: string, index: number) => void;

  // Callbacks
  onGenerateSingle?: (imageType: string) => void;
  onGenerateAll?: () => void;
  onRegenerateSingle?: (imageType: string, note?: string, referenceImagePaths?: string[]) => void;
  onEditSingle?: (imageType: string, instructions: string, referenceImagePaths?: string[]) => void;
  onCancelGeneration?: (imageType: string) => void;
  availableReferenceImages?: import('@/api/types').ReferenceImage[];
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
  isAnalyzing = false,
  sessionId,
  images,
  aplusModules = [],
  aplusVisualScript,
  isGeneratingScript = false,
  onGenerateAplusModule,
  onRegenerateAplusModule,
  onGenerateAllAplus,
  onRegenerateScript,
  onReplanAll,
  isReplanning = false,
  onAplusVersionChange,
  onEditAplusModule,
  aplusViewportMode: _aplusViewportMode, // Now controlled via unified viewport
  onAplusViewportChange,
  onGenerateMobileModule,
  onGenerateAllMobile,
  onRegenerateMobileModule,
  onEditMobileModule,
  onCancelAplusModule,
  listingVersions,
  onListingVersionChange,
  onGenerateSingle,
  onGenerateAll,
  onRegenerateSingle,
  onEditSingle,
  onCancelGeneration,
  availableReferenceImages = [],
  onRetry,
  onStartOver,
  className,
}) => {
  // Unified viewport mode - controls BOTH listing images AND A+ content
  const [unifiedViewportMode, setUnifiedViewportMode] = useState<'desktop' | 'mobile'>('desktop');

  // Handler that syncs both listing and A+ viewport modes
  const handleViewportModeChange = useCallback((mode: 'desktop' | 'mobile') => {
    setUnifiedViewportMode(mode);
    // Also update A+ viewport if callback provided
    if (onAplusViewportChange) {
      onAplusViewportChange(mode);
    }
  }, [onAplusViewportChange]);

  // Legacy deviceMode for LivePreview (non-Amazon preview states)
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
  const totalImages = images.length || 6;
  const generationProgress = totalImages > 0 ? (completeCount / totalImages) * 100 : 0;

  // Get accent color from framework
  const frameworkColors = selectedFramework ? normalizeColors(selectedFramework.colors) : [];
  const accentColor = frameworkColors.find((c) => c.role === 'primary')?.hex || '#C85A35';

  // Toggle fullscreen
  const handleFullscreenToggle = useCallback(() => {
    setIsFullscreen((prev) => !prev);
  }, []);

  // Check if we should show the Amazon-style interactive preview
  // Show it when framework is selected OR when generating/complete
  const showAmazonPreview = previewState === 'framework_selected' || previewState === 'generating' || previewState === 'complete';

  // For framework_selected, generating, or complete states - show the full AmazonListingPreview
  if (showAmazonPreview) {
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
                onGenerateSingle={onGenerateSingle}
                onGenerateAll={onGenerateAll}
                onRetry={onRetry}
                onRegenerateSingle={onRegenerateSingle}
                onEditSingle={onEditSingle}
                onCancelGeneration={onCancelGeneration}
                availableReferenceImages={availableReferenceImages}
                onStartOver={onStartOver}
                listingVersions={listingVersions}
                onVersionChange={onListingVersionChange}
                deviceMode={unifiedViewportMode}
                onDeviceModeChange={handleViewportModeChange}
              />
            </div>
          </div>
        )}

        {/* Normal view - single continuous Amazon page mockup */}
        <div className="flex-1 overflow-auto">
          <AmazonListingPreview
            productTitle={productTitle}
            brandName={brandName}
            features={features.filter(Boolean).map(f => f || '')}
            targetAudience={targetAudience}
            sessionId={sessionId}
            images={images}
            framework={selectedFramework}
            onGenerateSingle={onGenerateSingle}
            onGenerateAll={onGenerateAll}
            onRetry={onRetry}
            onRegenerateSingle={onRegenerateSingle}
            onEditSingle={onEditSingle}
            availableReferenceImages={availableReferenceImages}
            onStartOver={onStartOver}
            listingVersions={listingVersions}
            onVersionChange={onListingVersionChange}
            deviceMode={unifiedViewportMode}
            onDeviceModeChange={handleViewportModeChange}
            onReplanAll={onReplanAll}
            isReplanning={isReplanning}
            aplusContent={aplusModules.length > 0 ? (
              <AplusSection
                modules={aplusModules}
                sessionId={sessionId}
                productTitle={productTitle}
                accentColor={accentColor}
                isEnabled={true}
                visualScript={aplusVisualScript}
                isGeneratingScript={isGeneratingScript}
                onGenerateModule={onGenerateAplusModule}
                onRegenerateModule={onRegenerateAplusModule}
                onGenerateAll={onGenerateAllAplus}
                onRegenerateScript={onRegenerateScript}
                onVersionChange={onAplusVersionChange}
                onEditModule={onEditAplusModule}
                viewportMode={unifiedViewportMode}
                onViewportChange={handleViewportModeChange}
                onGenerateMobileModule={onGenerateMobileModule}
                onGenerateAllMobile={onGenerateAllMobile}
                onRegenerateMobileModule={onRegenerateMobileModule}
                onEditMobileModule={onEditMobileModule}
                availableReferenceImages={availableReferenceImages}
                onCancelModule={onCancelAplusModule}
              />
            ) : undefined}
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
      <div className="flex-1 overflow-auto relative">
        {/* Style Analysis Overlay */}
        {isAnalyzing && (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm rounded-lg">
            <div className="text-center space-y-6 p-8 max-w-sm">
              {/* Animated rings */}
              <div className="relative w-24 h-24 mx-auto">
                <div className="absolute inset-0 rounded-full border-2 border-redd-500/30 animate-ping" />
                <div className="absolute inset-2 rounded-full border-2 border-redd-500/50 animate-pulse" />
                <div className="absolute inset-4 rounded-full border-2 border-redd-500 border-t-transparent animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <svg className="w-8 h-8 text-redd-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
                  </svg>
                </div>
              </div>

              {/* Text */}
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-white">Crafting Your Styles</h3>
                <p className="text-sm text-slate-400">
                  AI is analyzing your product and designing unique visual frameworks...
                </p>
              </div>

              {/* Shimmer bars */}
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-2 rounded-full bg-slate-700 overflow-hidden"
                    style={{ width: `${100 - i * 15}%`, margin: '0 auto' }}
                  >
                    <div
                      className="h-full animate-shimmer rounded-full"
                      style={{
                        background: 'linear-gradient(90deg, transparent 0%, rgba(200,90,53,0.5) 50%, transparent 100%)',
                        backgroundSize: '200% 100%',
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

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
      </div>
    </div>
  );
};

export default ShowroomPanel;
