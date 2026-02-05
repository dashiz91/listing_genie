import React, { useState, useCallback } from 'react';
import { normalizeColors } from '@/lib/utils';
import type { SessionImage, DesignFramework, ReferenceImage, AplusVisualScript } from '@/api/types';
import { AmazonListingPreview } from '../amazon-preview';
import { AplusSection, type AplusModule, type AplusViewportMode } from '../preview-slots/AplusSection';
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

  // Navigation
  onBackToEditor: () => void;
  onOpenAdvancedSettings: () => void;
  onStartOver: () => void;
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
  onBackToEditor,
  onOpenAdvancedSettings,
  onStartOver,
}) => {
  // Unified viewport mode
  const [unifiedViewportMode, setUnifiedViewportMode] = useState<'desktop' | 'mobile'>('desktop');

  const handleViewportModeChange = useCallback((mode: 'desktop' | 'mobile') => {
    setUnifiedViewportMode(mode);
    onAplusViewportChange(mode);
  }, [onAplusViewportChange]);

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
