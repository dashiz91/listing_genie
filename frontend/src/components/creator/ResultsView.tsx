import React, { useState, useCallback, useEffect } from 'react';
import { cn, normalizeColors } from '@/lib/utils';
import type { SessionImage, DesignFramework, ReferenceImage, AplusVisualScript } from '@/api/types';
import { AmazonListingPreview } from '../amazon-preview';
import { GenerationProgressBar } from '../amazon-preview/GenerationProgressBar';
import { CelebrationOverlay } from '../amazon-preview/CelebrationOverlay';
import { AplusSection, type AplusModule, type AplusViewportMode } from '../preview-slots/AplusSection';
import { WorkflowStepper, type WorkflowStep } from '../ui/workflow-stepper';
import PushToAmazonButton from '../PushToAmazonButton';
import type { ListingVersionState } from '@/pages/HomePage';

interface ResultsViewProps {
  // Product data
  productTitle: string;
  brandName?: string;
  features: string[];
  targetAudience?: string;

  // Images
  sessionId?: string;
  images: SessionImage[];

  // Framework
  selectedFramework?: DesignFramework;

  // A+ Content
  aplusModules: AplusModule[];
  aplusVisualScript: AplusVisualScript | null;
  isGeneratingScript: boolean;
  onGenerateAplusModule: (moduleIndex: number) => void;
  onRegenerateAplusModule: (moduleIndex: number, note?: string, referenceImagePaths?: string[]) => void;
  onGenerateAllAplus: () => void;
  onRegenerateScript: () => void;
  onReplanAll: () => void;
  isReplanning: boolean;
  onAplusVersionChange: (moduleIndex: number, versionIndex: number) => void;
  onEditAplusModule: (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => void;
  aplusViewportMode: AplusViewportMode;
  onAplusViewportChange: (mode: AplusViewportMode) => void;
  onGenerateMobileModule: (moduleIndex: number) => void;
  onGenerateAllMobile: () => void;
  onRegenerateMobileModule: (moduleIndex: number, note?: string, referenceImagePaths?: string[]) => void;
  onEditMobileModule: (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => void;
  onCancelAplusModule: (moduleIndex: number, viewport: AplusViewportMode) => void;

  // Listing versions
  listingVersions: ListingVersionState;
  onListingVersionChange: (imageType: string, index: number) => void;

  // Listing image callbacks
  onGenerateSingle: (imageType: string) => void;
  onGenerateAll: () => void;
  onRegenerateSingle: (imageType: string, note?: string, referenceImagePaths?: string[]) => void;
  onEditSingle: (imageType: string, instructions: string, referenceImagePaths?: string[]) => void;
  onCancelGeneration: (imageType: string) => void;
  availableReferenceImages: ReferenceImage[];
  onRetry: () => void;

  // Generation state
  isGenerating?: boolean;
  showGenerationCelebration?: boolean;
  onCelebrationComplete?: () => void;

  // Model
  imageModel: string;
  onModelChange: (model: string) => void;

  // Navigation
  onBackToEditor: () => void;
  onOpenAdvancedSettings: () => void;
  onStartOver: () => void;

  // Workflow stepper
  workflowSteps?: WorkflowStep[];

  // Error state
  error?: string | null;
  onDismissError?: () => void;
}

export const ResultsView: React.FC<ResultsViewProps> = ({
  productTitle,
  brandName,
  features,
  targetAudience,
  sessionId,
  images,
  selectedFramework,
  aplusModules,
  aplusVisualScript,
  isGeneratingScript,
  onGenerateAplusModule,
  onRegenerateAplusModule,
  onGenerateAllAplus,
  onRegenerateScript,
  onReplanAll,
  isReplanning,
  onAplusVersionChange,
  onEditAplusModule,
  aplusViewportMode: _aplusViewportMode,
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
  availableReferenceImages,
  onRetry,
  isGenerating = false,
  showGenerationCelebration = false,
  onCelebrationComplete,
  imageModel,
  onModelChange,
  onBackToEditor,
  onOpenAdvancedSettings,
  onStartOver,
  workflowSteps,
  error,
  onDismissError,
}) => {
  // Unified viewport mode
  const [unifiedViewportMode, setUnifiedViewportMode] = useState<'desktop' | 'mobile'>('desktop');
  const [showPushNudge, setShowPushNudge] = useState(true);
  const listingImageTypes = new Set([
    'main',
    'infographic_1',
    'infographic_2',
    'lifestyle',
    'transformation',
    'comparison',
  ]);

  const handleViewportModeChange = useCallback((mode: 'desktop' | 'mobile') => {
    setUnifiedViewportMode(mode);
    onAplusViewportChange(mode);
  }, [onAplusViewportChange]);

  const listingImages = images.filter((img) => listingImageTypes.has(img.type));
  const hasAnyListingComplete = listingImages.some((img) => img.status === 'complete');
  const allListingImagesReady =
    listingImages.length > 0 && listingImages.every((img) => img.status === 'complete');
  const showPushBanner = !!sessionId && allListingImagesReady && showPushNudge;

  useEffect(() => {
    if (allListingImagesReady) {
      setShowPushNudge(true);
    }
  }, [allListingImagesReady, sessionId]);

  // Get accent color from framework
  const frameworkColors = selectedFramework ? normalizeColors(selectedFramework.colors) : [];
  const accentColor = frameworkColors.find((c) => c.role === 'primary')?.hex || '#C85A35';

  return (
    <div className={cn('flex-1 overflow-auto', showPushBanner && 'pb-32')}>
      {/* Top bar */}
      <div className="sticky top-0 z-20 bg-slate-900/95 backdrop-blur-sm border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={onBackToEditor}
              className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors shrink-0"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Editor
            </button>
            <span className="text-slate-600">|</span>
            <h2 className="text-sm font-medium text-white truncate">{productTitle || 'Untitled'}</h2>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {/* Model toggle */}
            <div className="flex items-center bg-slate-800 border border-slate-600 rounded-lg p-0.5 gap-0.5">
              {([
                { value: 'gemini-2.5-flash-image', label: 'Flash', icon: '\u26A1', cost: '1' },
                { value: 'gemini-3-pro-image-preview', label: 'Pro', icon: '\u2728', cost: '3' },
              ] as const).map((opt) => {
                const isActive = imageModel === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => onModelChange(opt.value)}
                    className={cn(
                      'flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-all',
                      isActive
                        ? opt.value.includes('pro')
                          ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-sm'
                          : 'bg-slate-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-white hover:bg-slate-700'
                    )}
                    title={`${opt.label} — ${opt.cost} credit${opt.cost !== '1' ? 's' : ''}/image`}
                  >
                    <span className="text-[11px]">{opt.icon}</span>
                    {opt.label}
                    <span className={cn(
                      'text-[10px] tabular-nums',
                      isActive ? 'text-white/70' : 'text-slate-500'
                    )}>{opt.cost}cr</span>
                  </button>
                );
              })}
            </div>
            {/* Push to Amazon (visible when session has generated images) */}
            {sessionId && hasAnyListingComplete && !showPushBanner && (
              <PushToAmazonButton sessionId={sessionId} />
            )}
            <button
              onClick={onOpenAdvancedSettings}
              className="px-3 py-1.5 text-xs text-slate-400 hover:text-white bg-slate-800 border border-slate-600 rounded-lg transition-colors"
            >
              Settings
            </button>
            <button
              onClick={onStartOver}
              className="px-3 py-1.5 text-xs text-slate-400 hover:text-white bg-slate-800 border border-slate-600 rounded-lg transition-colors"
            >
              New Listing
            </button>
          </div>
        </div>
      </div>

      {/* Workflow stepper (visible during active generation) */}
      {workflowSteps && <WorkflowStepper steps={workflowSteps} />}

      {/* Generation progress bar */}
      <GenerationProgressBar images={images} isGenerating={isGenerating} />

      {/* Error banner */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 mt-4">
          <div className="bg-red-900/40 border border-red-500/50 rounded-lg p-4 flex items-start gap-3">
            <svg className="w-5 h-5 text-red-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div className="flex-1">
              <p className="text-red-200 text-sm">{error}</p>
            </div>
            {onDismissError && (
              <button onClick={onDismissError} className="text-red-400 hover:text-red-200 transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Celebration overlay */}
      <CelebrationOverlay
        isVisible={showGenerationCelebration}
        onComplete={onCelebrationComplete}
        message="Images Ready!"
        subMessage="Your listing images have been generated"
      />

      {/* Full-width Amazon preview */}
      <div className="max-w-7xl mx-auto">
        <AmazonListingPreview
          productTitle={productTitle}
          brandName={brandName}
          features={features.filter(Boolean).map(f => f || '')}
          targetAudience={targetAudience}
          sessionId={sessionId}
          images={images}
          framework={selectedFramework}
          aplusModules={aplusModules}
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

      {/* Sticky bottom nudge when all listing slots are ready */}
      {showPushBanner && (
        <div className="pointer-events-none fixed inset-x-0 bottom-4 z-40 px-3 sm:px-6">
          <div className="pointer-events-auto max-w-5xl mx-auto rounded-2xl border border-[#FF9900]/55 bg-gradient-to-r from-[#C85A35] via-[#FF9900] to-[#FFC266] p-[1px] shadow-[0_16px_40px_rgba(200,90,53,0.45)]">
            <div className="rounded-[15px] bg-slate-950/94 px-4 py-4 sm:px-6 sm:py-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <p className="text-base sm:text-lg font-semibold text-[#FFB84D]">
                  Your listing is ready to publish
                </p>
                <p className="text-xs sm:text-sm text-slate-300 mt-1">
                  Keep editing if you want, or push this version to Amazon now.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <PushToAmazonButton
                  sessionId={sessionId!}
                  label="Push This Version"
                  className="px-5 py-2.5 text-sm font-semibold !text-slate-950 !bg-[#FFD27A] !border-[#FFDFA6] hover:!bg-[#FFBF4D] shadow-[0_10px_24px_rgba(0,0,0,0.32)]"
                />
                <button
                  onClick={() => setShowPushNudge(false)}
                  className="px-2 py-1 text-xs text-slate-400 hover:text-slate-100"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
