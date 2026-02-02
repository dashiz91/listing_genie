import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import type { AplusModuleType, ImageVersion } from '@/api/types';
import { APLUS_DIMENSIONS, APLUS_MOBILE_DIMENSIONS } from '@/api/types';
import { PromptModal } from '@/components/PromptModal';
import { ImageActionOverlay } from '@/components/shared/ImageActionOverlay';
import FocusImagePicker, { useFocusImages } from '@/components/FocusImagePicker';
import type { SlotStatus } from './ImageSlot';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/** @deprecated Use ImageVersion from api/types instead */
export type AplusModuleVersion = ImageVersion;

export type AplusViewportMode = 'desktop' | 'mobile';

export interface AplusModule {
  id: string;
  type: AplusModuleType;
  index: number;
  status: SlotStatus;
  errorMessage?: string;
  // Desktop versions
  versions: ImageVersion[];
  activeVersionIndex: number;
  // Mobile versions (independent track)
  mobileVersions: ImageVersion[];
  mobileActiveVersionIndex: number;
  mobileStatus?: SlotStatus;
}

// Helper to get the active version's URL/path
export function getActiveVersion(module: AplusModule, viewport: AplusViewportMode = 'desktop'): AplusModuleVersion | undefined {
  if (viewport === 'mobile') {
    return module.mobileVersions[module.mobileActiveVersionIndex];
  }
  return module.versions[module.activeVersionIndex];
}

export function getActiveImageUrl(module: AplusModule, viewport: AplusViewportMode = 'desktop'): string | undefined {
  if (viewport === 'mobile') {
    return module.mobileVersions[module.mobileActiveVersionIndex]?.imageUrl;
  }
  return module.versions[module.activeVersionIndex]?.imageUrl;
}

export function getActiveImagePath(module: AplusModule, viewport: AplusViewportMode = 'desktop'): string | undefined {
  if (viewport === 'mobile') {
    return module.mobileVersions[module.mobileActiveVersionIndex]?.imagePath;
  }
  return module.versions[module.activeVersionIndex]?.imagePath;
}

interface AplusSectionProps {
  modules: AplusModule[];
  sessionId?: string;
  productTitle?: string;
  accentColor?: string;
  visualScript?: import('@/api/types').AplusVisualScript | null;
  isGeneratingScript?: boolean;
  onGenerateModule?: (moduleIndex: number) => void;
  onRegenerateModule?: (moduleIndex: number, note?: string) => void;
  onGenerateAll?: () => void;
  onRegenerateScript?: () => void;
  onVersionChange?: (moduleIndex: number, versionIndex: number) => void;
  onEditModule?: (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => void;
  isEnabled?: boolean;
  className?: string;
  // Mobile viewport support
  viewportMode?: AplusViewportMode;
  onViewportChange?: (mode: AplusViewportMode) => void;
  onGenerateMobileModule?: (moduleIndex: number) => void;
  onGenerateAllMobile?: () => void;
  onRegenerateMobileModule?: (moduleIndex: number, note?: string) => void;
  onEditMobileModule?: (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => void;
  // Focus images for edit
  availableReferenceImages?: import('@/api/types').ReferenceImage[];
}

const MODULE_LABELS: Record<AplusModuleType, string> = {
  full_image: 'Full Image Banner',
  dual_image: 'Dual Images',
  four_image: 'Four Images',
  comparison: 'Comparison Table',
};

export const AplusSection: React.FC<AplusSectionProps> = ({
  modules,
  sessionId,
  productTitle = 'product',
  accentColor = '#C85A35',
  visualScript,
  isGeneratingScript = false,
  onGenerateModule,
  onRegenerateModule,
  onGenerateAll,
  onRegenerateScript,
  onVersionChange,
  onEditModule,
  isEnabled = true,
  className,
  viewportMode = 'desktop',
  onViewportChange,
  onGenerateMobileModule,
  onGenerateAllMobile,
  onRegenerateMobileModule,
  onEditMobileModule,
  availableReferenceImages = [],
}) => {
  const [promptModalIndex, setPromptModalIndex] = useState<number | null>(null);
  const [editingModuleIndex, setEditingModuleIndex] = useState<number | null>(null);
  const [editInstructions, setEditInstructions] = useState('');
  const focusImages = useFocusImages();
  const [regenModuleIndex, setRegenModuleIndex] = useState<number | null>(null);
  const [regenNote, setRegenNote] = useState('');
  // Track refreshed URLs for modules whose signed URLs expired
  const [refreshedUrls, setRefreshedUrls] = useState<Record<string, string>>({});

  const handleImageError = useCallback((moduleId: string, imagePath: string | undefined) => {
    if (!imagePath) return;
    // Use the backend proxy to get a fresh signed URL
    const proxyUrl = `${API_BASE}/api/images/file?path=${encodeURIComponent(imagePath)}&t=${Date.now()}`;
    setRefreshedUrls((prev) => ({ ...prev, [moduleId]: proxyUrl }));
  }, []);

  const handleDownload = async (module: AplusModule, idx: number, viewport: AplusViewportMode = 'desktop') => {
    const imgUrl = getActiveImageUrl(module, viewport);
    if (!imgUrl) return;
    try {
      const response = await fetch(imgUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const slug = productTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      a.download = `${slug}-aplus-module-${idx + 1}${viewport === 'mobile' ? '-mobile' : ''}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Download failed:', e);
    }
  };

  const isMobile = viewportMode === 'mobile';

  // For mobile viewport, use mobile versions/status
  const getModuleVersions = (m: AplusModule) => isMobile ? m.mobileVersions : m.versions;
  const getModuleActiveIndex = (m: AplusModule) => isMobile ? m.mobileActiveVersionIndex : m.activeVersionIndex;
  const getModuleStatus = (m: AplusModule): SlotStatus => {
    if (isMobile) return m.mobileStatus || 'ready';
    return m.status;
  };

  // Check if at least one desktop module is complete (for enabling mobile toggle)
  const anyDesktopComplete = modules.some((m) => m.status === 'complete' && m.versions.length > 0);
  // Check if any mobile modules exist
  const anyMobileExists = modules.some((m) => m.mobileVersions.length > 0);
  const noMobileGenerated = !anyMobileExists;
  // Count modules needing mobile generation
  const mobileNeededCount = modules.filter((m) => m.status === 'complete' && m.versions.length > 0 && m.mobileVersions.length === 0).length;

  const allPending = modules.every((m) => m.status === 'ready' || m.status === 'locked');
  const anyGenerating = modules.some((m) => m.status === 'generating' || m.mobileStatus === 'generating');

  // Get module role label from visual script or fallback
  const getModuleLabel = (idx: number, type: AplusModuleType): string => {
    if (visualScript?.modules?.[idx]?.role) {
      return visualScript.modules[idx].role;
    }
    return MODULE_LABELS[type];
  };

  const canGenerateModule = (index: number): boolean => {
    if (!isEnabled || !sessionId) return false;
    if (index === 0) return true;
    const prevModule = modules[index - 1];
    return prevModule?.status === 'complete';
  };

  if (modules.length === 0) return null;

  return (
    <div className={cn('bg-white rounded-lg border border-gray-200 overflow-hidden', className)}>
      {/* Amazon-style header with viewport toggle */}
      <div className="bg-gray-100 border-b border-gray-200 px-4 py-2.5 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">From the manufacturer</span>
        {onViewportChange && (
          <div className="flex items-center rounded-full bg-gray-200 p-0.5">
            <button
              onClick={() => onViewportChange('desktop')}
              className={cn(
                'px-3 py-1 text-xs font-medium rounded-full transition-all duration-200',
                viewportMode === 'desktop'
                  ? 'text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              )}
              style={viewportMode === 'desktop' ? { backgroundColor: accentColor } : undefined}
            >
              Desktop
            </button>
            <button
              onClick={() => onViewportChange('mobile')}
              disabled={!anyDesktopComplete}
              className={cn(
                'px-3 py-1 text-xs font-medium rounded-full transition-all duration-200',
                viewportMode === 'mobile'
                  ? 'text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700',
                !anyDesktopComplete && 'opacity-40 cursor-not-allowed'
              )}
              style={viewportMode === 'mobile' ? { backgroundColor: accentColor } : undefined}
              title={!anyDesktopComplete ? 'Generate desktop modules first' : undefined}
            >
              Mobile
            </button>
          </div>
        )}
      </div>

      {/* Generate All button (desktop) */}
      {!isMobile && allPending && !anyGenerating && !isGeneratingScript && sessionId && (
        <div className="px-4 pt-4">
          <button
            onClick={() => onGenerateAll?.()}
            disabled={!isEnabled}
            className="w-full py-3 rounded-lg font-medium text-white transition-colors flex items-center justify-center gap-2"
            style={{ backgroundColor: accentColor }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Generate All A+ Content
          </button>
        </div>
      )}

      {/* Generate All Mobile button */}
      {isMobile && noMobileGenerated && mobileNeededCount > 0 && !anyGenerating && sessionId && (
        <div className="px-4 pt-4">
          <button
            onClick={() => onGenerateAllMobile?.()}
            disabled={!isEnabled}
            className="w-full py-3 rounded-lg font-medium text-white transition-colors flex items-center justify-center gap-2"
            style={{ backgroundColor: accentColor }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Generate All Mobile ({mobileNeededCount})
          </button>
        </div>
      )}

      {/* Re-plan Art Direction — always available when script exists */}
      {visualScript && onRegenerateScript && !anyGenerating && !isGeneratingScript && sessionId && (
        <div className="px-4 pt-2">
          <button
            onClick={() => onRegenerateScript()}
            className="w-full py-2 text-xs text-gray-500 hover:text-gray-700 transition-colors flex items-center justify-center gap-1"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Re-plan Art Direction
          </button>
        </div>
      )}

      {/* Art Director planning state */}
      {isGeneratingScript && (
        <div className="px-4 pt-4">
          <div className="flex items-center gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="w-6 h-6 border-2 border-amber-300 rounded-full animate-spin" style={{ borderTopColor: accentColor }} />
            <div>
              <p className="text-sm font-medium text-amber-800">Art Director is planning...</p>
              <p className="text-xs text-amber-600">Designing your A+ section as one unified visual narrative</p>
            </div>
          </div>
        </div>
      )}

      {/* Modules — no space-y so hero pair has zero gap */}
      <div className="p-4">
        {modules.map((module, idx) => {
          // Hide module 1 in mobile mode
          if (isMobile && idx === 1) return null;

          const dims = isMobile ? APLUS_MOBILE_DIMENSIONS[module.type] : APLUS_DIMENSIONS[module.type];
          const canGenerate = canGenerateModule(idx);
          const moduleLabel = getModuleLabel(idx, module.type);

          // Viewport-aware state
          const versions = getModuleVersions(module);
          const activeIndex = getModuleActiveIndex(module);
          const mStatus = getModuleStatus(module);
          const isLocked = !isMobile && !canGenerate && module.status !== 'generating' && module.status !== 'complete';

          // Aspect ratio for sizing
          const aspectPercent = (dims.height / dims.width) * 100;

          // Hero pair: modules 0+1 are seamless on desktop only — mobile stacks independently
          const isHeroTop = !isMobile && idx === 0;
          const isHeroBottom = !isMobile && idx === 1;
          const moduleStyle = isHeroBottom
            ? { marginTop: 0 }
            : idx > 0
              ? { marginTop: '12px' }
              : undefined;
          const imageRounding = isHeroTop ? 'rounded-t-lg' : isHeroBottom ? 'rounded-b-lg' : 'rounded-lg';

          // Mobile: show "Generate Mobile" overlay when desktop complete but no mobile version
          const showMobileGenPrompt = isMobile && module.status === 'complete' && module.versions.length > 0 && versions.length === 0 && mStatus !== 'generating';

          return (
            <div key={module.id} style={moduleStyle}>
              {/* Module role label — hide for hero bottom on desktop */}
              {!isHeroBottom && (
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {isMobile && idx === 0 ? `${moduleLabel} (Hero Banner)` : isHeroTop ? `${moduleLabel} (Hero Pair)` : moduleLabel}
                  </span>
                  <span className="text-xs text-gray-400">
                    {isMobile ? '📱 ' : ''}{isMobile ? (idx === 0 ? 1 : idx) : idx + 1}/{isMobile ? modules.length - 1 : modules.length}
                  </span>
                </div>
              )}

              {/* Mobile: "Generate Mobile" prompt overlay */}
              {showMobileGenPrompt && (
                <div
                  className={cn("relative w-full border-2 border-dashed border-blue-300 bg-blue-50 hover:border-blue-400 hover:bg-blue-100 transition-colors cursor-pointer", imageRounding)}
                  style={{ paddingBottom: `${Math.min(aspectPercent, 75)}%` }}
                  onClick={() => onGenerateMobileModule?.(idx)}
                >
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <p className="text-sm font-medium text-blue-700">
                      {idx === 0 ? 'Tap to generate mobile hero' : 'Tap to generate mobile'}
                    </p>
                    <p className="text-xs text-blue-500">
                      {idx === 0 ? 'Merges hero pair into one 4:3 image' : 'Recomposes for 4:3 mobile view'}
                    </p>
                  </div>
                </div>
              )}

              {/* Complete: show image with hover overlay + version arrows */}
              {!showMobileGenPrompt && mStatus === 'complete' && versions.length > 0 && (() => {
                const activeVer = versions[activeIndex];
                if (!activeVer) return null;
                const refreshKey = `${module.id}-${viewportMode}-${activeIndex}`;
                const displayUrl = refreshedUrls[refreshKey] || activeVer.imageUrl;
                const totalVersions = versions.length;
                const canGoLeft = activeIndex > 0;
                const canGoRight = activeIndex < totalVersions - 1;
                const hasMultipleVersions = totalVersions > 1;

                return (
                  <div
                    className={cn("relative w-full overflow-hidden cursor-pointer", imageRounding)}
                    style={{ paddingBottom: `${Math.min(aspectPercent, isMobile ? 75 : 60)}%` }}
                  >
                    <img
                      src={displayUrl}
                      alt={`A+ Module ${idx + 1}${isMobile ? ' (Mobile)' : ''}`}
                      className="absolute inset-0 w-full h-full object-cover"
                      onError={() => {
                        const key = `${module.id}-${viewportMode}-${activeIndex}`;
                        if (!refreshedUrls[key]) {
                          handleImageError(key, activeVer.imagePath);
                        }
                      }}
                    />

                    {/* Hover overlay with action buttons */}
                    <ImageActionOverlay
                      versionInfo={{ current: activeIndex + 1, total: totalVersions }}
                      onRegenerate={() => {
                        setRegenModuleIndex(idx); setRegenNote('');
                      }}
                      onEdit={onEditModule || onEditMobileModule ? () => { setEditingModuleIndex(idx); setEditInstructions(''); focusImages.reset(); } : undefined}
                      onDownload={() => handleDownload(module, idx, viewportMode)}
                      onViewPrompt={sessionId ? () => setPromptModalIndex(idx) : undefined}
                      onMobileTransform={!isMobile && onGenerateMobileModule ? () => onGenerateMobileModule(idx) : undefined}
                    />

                    {/* Version arrows */}
                    {hasMultipleVersions && (
                      <>
                        <button
                          onClick={(e) => { e.stopPropagation(); canGoLeft && onVersionChange?.(idx, activeIndex - 1); }}
                          className={cn(
                            "absolute z-30 left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/60 flex items-center justify-center transition-opacity",
                            canGoLeft ? "hover:bg-black/80 opacity-90" : "opacity-30 cursor-default"
                          )}
                        >
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                          </svg>
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); canGoRight && onVersionChange?.(idx, activeIndex + 1); }}
                          className={cn(
                            "absolute z-30 right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-black/60 flex items-center justify-center transition-opacity",
                            canGoRight ? "hover:bg-black/80 opacity-90" : "opacity-30 cursor-default"
                          )}
                        >
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                      </>
                    )}

                    {/* Version badge with viewport icon */}
                    <div className="absolute z-30 bottom-2 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-black/60 rounded-full">
                      <span className="text-xs text-white font-medium">
                        {isMobile ? '📱 ' : ''}v{activeIndex + 1}/{totalVersions}
                      </span>
                    </div>
                  </div>
                );
              })()}

              {/* Generating: spinner */}
              {mStatus === 'generating' && (
                <div
                  className={cn("relative w-full border-2 border-gray-200 bg-gray-50 overflow-hidden", imageRounding)}
                  style={{ paddingBottom: `${Math.min(aspectPercent, isMobile ? 75 : 60)}%` }}
                >
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
                    <div className="w-8 h-8 border-2 border-gray-300 rounded-full animate-spin" style={{ borderTopColor: accentColor }} />
                    <p className="text-sm text-gray-500">
                      {isMobile ? 'Generating mobile version...' : `Generating ${moduleLabel}...`}
                    </p>
                  </div>
                </div>
              )}

              {/* Error */}
              {!showMobileGenPrompt && mStatus === 'error' && (
                <div
                  className={cn("relative w-full border-2 border-dashed border-red-300 bg-red-50 overflow-hidden cursor-pointer", imageRounding)}
                  style={{ paddingBottom: `${Math.min(aspectPercent, isMobile ? 75 : 60)}%` }}
                  onClick={() => isMobile ? onGenerateMobileModule?.(idx) : onGenerateModule?.(idx)}
                >
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-2">
                    <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm text-red-500">{module.errorMessage || 'Generation failed'}</p>
                    <p className="text-xs text-red-400">Click to retry</p>
                  </div>
                </div>
              )}

              {/* Pending: can generate (desktop only) */}
              {!isMobile && (module.status === 'ready' || module.status === 'locked') && canGenerate && (
                <div
                  className={cn("relative w-full border-2 border-dashed border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50 transition-colors cursor-pointer", imageRounding)}
                  style={{ paddingBottom: `${Math.min(aspectPercent, 60)}%` }}
                  onClick={() => onGenerateModule?.(idx)}
                >
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                      <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <p className="text-sm font-medium text-gray-600">Click to Generate</p>
                    <p className="text-xs text-gray-400">{moduleLabel}</p>
                  </div>
                </div>
              )}

              {/* Pending: locked (waiting for previous, desktop only) */}
              {!isMobile && (module.status === 'ready' || module.status === 'locked') && isLocked && (
                <div
                  className={cn("relative w-full border-2 border-dashed border-gray-200 bg-gray-50 overflow-hidden", imageRounding)}
                  style={{ paddingBottom: `${Math.min(aspectPercent, 60)}%` }}
                >
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 opacity-50">
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    <p className="text-xs text-gray-400">Generate Module {idx} first</p>
                  </div>
                </div>
              )}

              {/* Mobile: no desktop image yet (show nothing meaningful) */}
              {isMobile && module.status !== 'complete' && versions.length === 0 && mStatus !== 'generating' && !showMobileGenPrompt && (
                <div
                  className={cn("relative w-full border-2 border-dashed border-gray-200 bg-gray-50 overflow-hidden", imageRounding)}
                  style={{ paddingBottom: `${Math.min(aspectPercent, 75)}%` }}
                >
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 opacity-50">
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    <p className="text-xs text-gray-400">Generate desktop first</p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Prompt Modal — shared component with listing images */}
      {promptModalIndex !== null && sessionId && (
        <PromptModal
          sessionId={sessionId}
          imageType={`aplus_${promptModalIndex}`}
          title={`Module ${promptModalIndex + 1} Prompt${
            visualScript?.modules?.[promptModalIndex]?.role
              ? ` — ${visualScript.modules[promptModalIndex].role}`
              : ''
          }`}
          onClose={() => setPromptModalIndex(null)}
        />
      )}

      {/* Regenerate Note Panel — slide-up overlay */}
      {regenModuleIndex !== null && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/30" onClick={() => setRegenModuleIndex(null)}>
          <div
            className="w-full max-w-lg bg-white rounded-t-xl shadow-xl p-6 space-y-4 animate-in slide-in-from-bottom"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                Regenerate {regenModuleIndex <= 1 ? 'Hero Pair' : `Module ${regenModuleIndex + 1}`}
              </h3>
              <button onClick={() => setRegenModuleIndex(null)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <textarea
              value={regenNote}
              onChange={(e) => setRegenNote(e.target.value)}
              placeholder="Optionally describe what you'd like different... e.g. 'Try a more minimal style' or 'Make it more vibrant'"
              className="w-full h-28 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-redd-500/50 resize-none"
              autoFocus
            />
            <div className="flex gap-3">
              <button
                onClick={() => setRegenModuleIndex(null)}
                className="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (regenModuleIndex !== null) {
                    if (isMobile) {
                      onRegenerateMobileModule?.(regenModuleIndex, regenNote.trim() || undefined);
                    } else {
                      onRegenerateModule?.(regenModuleIndex, regenNote.trim() || undefined);
                    }
                    setRegenModuleIndex(null);
                    setRegenNote('');
                  }
                }}
                className="flex-1 py-2.5 rounded-lg text-sm font-medium text-white transition-colors"
                style={{ backgroundColor: accentColor }}
              >
                Regenerate
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Panel — slide-up overlay */}
      {editingModuleIndex !== null && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/30" onClick={() => setEditingModuleIndex(null)}>
          <div
            className="w-full max-w-lg bg-white rounded-t-xl shadow-xl p-6 space-y-4 animate-in slide-in-from-bottom"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                Edit Module {editingModuleIndex + 1}
              </h3>
              <button onClick={() => setEditingModuleIndex(null)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <textarea
              value={editInstructions}
              onChange={(e) => setEditInstructions(e.target.value)}
              placeholder="Describe what you'd like to change... e.g. 'Make the background darker' or 'Add more product detail on the left side'"
              className="w-full h-28 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-redd-500/50 resize-none"
              autoFocus
            />

            {/* Focus images — select which references to send with edit */}
            {availableReferenceImages.length > 0 && (
              <FocusImagePicker
                availableImages={availableReferenceImages}
                selectedPaths={focusImages.selectedPaths}
                onToggle={focusImages.toggle}
                extraFile={focusImages.extraFile}
                onExtraFile={focusImages.addExtra}
                onRemoveExtra={focusImages.removeExtra}
                variant="light"
              />
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setEditingModuleIndex(null)}
                className="flex-1 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (editInstructions.trim() && editingModuleIndex !== null) {
                    const refPaths = focusImages.getSelectedPaths();
                    const refs = refPaths.length > 0 ? refPaths : undefined;
                    if (isMobile) {
                      onEditMobileModule?.(editingModuleIndex, editInstructions.trim(), refs);
                    } else {
                      onEditModule?.(editingModuleIndex, editInstructions.trim(), refs);
                    }
                    setEditingModuleIndex(null);
                    setEditInstructions('');
                    focusImages.reset();
                  }
                }}
                disabled={!editInstructions.trim()}
                className="flex-1 py-2.5 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50"
                style={{ backgroundColor: accentColor }}
              >
                Apply Edit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AplusSection;
