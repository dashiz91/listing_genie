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
}) => {
  // Unified viewport mode
  const [unifiedViewportMode, setUnifiedViewportMode] = useState<'desktop' | 'mobile'>('desktop');
  const [showPushNudge, setShowPushNudge] = useState(true);

  const handleViewportModeChange = useCallback((mode: 'desktop' | 'mobile') => {
    setUnifiedViewportMode(mode);
    onAplusViewportChange(mode);
  }, [onAplusViewportChange]);

  const completeCount = images.filter(i => i.status === 'complete').length;
  const allListingImagesReady = images.length > 0 && completeCount === images.length;
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
    <div className="flex-1 overflow-auto">
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
            {sessionId && images.some(i => i.status === 'complete') && !showPushBanner && (
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

      {/* Persistent (non-modal) nudge when all listing slots are ready */}
      {showPushBanner && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-4">
          <div className="rounded-xl border border-[#FF9900]/30 bg-gradient-to-r from-[#FF9900]/12 to-slate-800/80 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-[#FFB84D]">
                Listing images are ready to publish
              </p>
              <p className="text-xs text-slate-300 mt-1">
                You can keep tweaking images anytime, but you can also push this version to Amazon now.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <PushToAmazonButton
                sessionId={sessionId!}
                label="Push This Version"
                className="bg-[#FF9900]/20 border-[#FF9900]/40 hover:bg-[#FF9900]/30"
              />
              <button
                onClick={() => setShowPushNudge(false)}
                className="px-2 py-1 text-xs text-slate-400 hover:text-slate-200"
              >
                Dismiss
              </button>
            </div>
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
    </div>
  );
};
