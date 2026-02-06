import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { cn } from '@/lib/utils';
import type { AplusModuleType, ImageVersion } from '@/api/types';
import { APLUS_DIMENSIONS, APLUS_MOBILE_DIMENSIONS } from '@/api/types';
import { apiClient } from '@/api/client';
import { PromptModal } from '@/components/PromptModal';
import { GenerationLoader } from '@/components/generation-loader';
import { Spinner } from '@/components/ui/spinner';
import { ImageActionOverlay } from '@/components/shared/ImageActionOverlay';
import FocusImagePicker, { useFocusImages } from '@/components/FocusImagePicker';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';
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
  onRegenerateModule?: (moduleIndex: number, note?: string, referenceImagePaths?: string[]) => void;
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
  onRegenerateMobileModule?: (moduleIndex: number, note?: string, referenceImagePaths?: string[]) => void;
  onEditMobileModule?: (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => void;
  // Focus images for edit
  availableReferenceImages?: import('@/api/types').ReferenceImage[];
  // Cancel generation (viewport-aware — caller decides desktop vs mobile)
  onCancelModule?: (moduleIndex: number, viewport: AplusViewportMode) => void;
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
  onRegenerateScript: _onRegenerateScript,
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
  onCancelModule,
}) => {
  const [promptModalIndex, setPromptModalIndex] = useState<number | null>(null);
  void _onRegenerateScript; // Deprecated: now handled by unified Re-plan Art Direction button
  const [editingModuleIndex, setEditingModuleIndex] = useState<number | null>(null);
  const [editInstructions, setEditInstructions] = useState('');
  const focusImages = useFocusImages();
  const [regenModuleIndex, setRegenModuleIndex] = useState<number | null>(null);
  const [regenNote, setRegenNote] = useState('');
  const regenFocusImages = useFocusImages();
  // Augmented reference images: include previous module's image when editing/regenerating module 2+
  const regenFocusAvailableImages = useMemo(() => {
    if (regenModuleIndex === null || regenModuleIndex <= 1) return availableReferenceImages;
    const prevModule = modules[regenModuleIndex - 1];
    const prevVer = prevModule?.versions[prevModule.activeVersionIndex];
    if (!prevVer?.imagePath || !prevVer?.imageUrl) return availableReferenceImages;
    return [
      { path: prevVer.imagePath, url: prevVer.imageUrl, label: `Module ${regenModuleIndex}` },
      ...availableReferenceImages,
    ];
  }, [regenModuleIndex, modules, availableReferenceImages]);

  const editFocusAvailableImages = useMemo(() => {
    if (editingModuleIndex === null || editingModuleIndex <= 1) return availableReferenceImages;
    const prevModule = modules[editingModuleIndex - 1];
    const prevVer = prevModule?.versions[prevModule.activeVersionIndex];
    if (!prevVer?.imagePath || !prevVer?.imageUrl) return availableReferenceImages;
    return [
      { path: prevVer.imagePath, url: prevVer.imageUrl, label: `Module ${editingModuleIndex}` },
      ...availableReferenceImages,
    ];
  }, [editingModuleIndex, modules, availableReferenceImages]);

  // Track which modules have been generating for >5s (show cancel/retry hint)
  const [stuckModules, setStuckModules] = useState<Set<number>>(new Set());
  const genTimersRef = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  // Monitor generating modules and set stuck hints after 5s
  useEffect(() => {
    modules.forEach((m, idx) => {
      const isGen = m.status === 'generating' || m.mobileStatus === 'generating';
      if (isGen && !genTimersRef.current.has(idx)) {
        const timer = setTimeout(() => {
          setStuckModules(prev => new Set(prev).add(idx));
        }, 5000);
        genTimersRef.current.set(idx, timer);
      } else if (!isGen && genTimersRef.current.has(idx)) {
        clearTimeout(genTimersRef.current.get(idx)!);
        genTimersRef.current.delete(idx);
        setStuckModules(prev => { const n = new Set(prev); n.delete(idx); return n; });
      }
    });
  }, [modules]);

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
    <div className={cn('overflow-hidden', className)}>
      {/* Amazon-style header - "From the manufacturer" section */}
      <div className="bg-gray-100 border-t border-gray-200 px-4 py-2.5 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">From the manufacturer</span>
        {/* Secondary viewport toggle for convenience (uses parent's unified handler) */}
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
              className={cn(
                'px-3 py-1 text-xs font-medium rounded-full transition-all duration-200',
                viewportMode === 'mobile'
                  ? 'text-white shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              )}
              style={viewportMode === 'mobile' ? { backgroundColor: accentColor } : undefined}
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

      {/* Art Director planning state */}
      {isGeneratingScript && (
        <div className="px-4 pt-4">
          <div className="flex items-center gap-3 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
            <Spinner size="md" className="text-redd-500" />
            <div>
              <p className="text-sm font-medium text-slate-200">Art Director is planning...</p>
              <p className="text-xs text-slate-400">Designing your A+ section as one unified visual narrative</p>
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
              {/* Module headers hidden - show only on hover via ImageActionOverlay */}

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

                    {/* Hover overlay with action buttons and module label */}
                    <ImageActionOverlay
                      versionInfo={{ current: activeIndex + 1, total: totalVersions }}
                      onRegenerate={() => {
                        setRegenModuleIndex(idx); setRegenNote(''); regenFocusImages.reset();
                      }}
                      onEdit={onEditModule || onEditMobileModule ? () => { setEditingModuleIndex(idx); setEditInstructions(''); focusImages.reset(); } : undefined}
                      onDownload={() => handleDownload(module, idx, viewportMode)}
                      onViewPrompt={sessionId ? () => setPromptModalIndex(idx) : undefined}
                      onMobileTransform={!isMobile && onGenerateMobileModule ? () => onGenerateMobileModule(idx) : undefined}
                      label={moduleLabel}
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

              {/* Generating: compact loader */}
              {mStatus === 'generating' && (
                <div
                  className={cn("relative w-full overflow-hidden", imageRounding)}
                  style={{ paddingBottom: `${Math.min(aspectPercent, isMobile ? 75 : 60)}%` }}
                >
                  <div className="absolute inset-0">
                    <GenerationLoader
                      imageType={isMobile ? `aplus_mobile_${idx}` : `aplus_${idx}`}
                      compact
                      className="w-full h-full"
                    />
                    {/* Cancel button overlay (appears after 5s) */}
                    {stuckModules.has(idx) && onCancelModule && (
                      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onCancelModule(idx, isMobile ? 'mobile' : 'desktop');
                          }}
                          className="text-xs font-medium text-slate-300 bg-slate-700/80 border border-slate-600 px-3 py-1.5 rounded-md transition-colors shadow-sm hover:bg-slate-600/80"
                        >
                          Cancel
                        </button>
                      </div>
                    )}
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
          version={modules[promptModalIndex] ? getModuleActiveIndex(modules[promptModalIndex]) + 1 : undefined}
          title={`Module ${promptModalIndex + 1} Prompt${
            visualScript?.modules?.[promptModalIndex]?.role
              ? ` — ${visualScript.modules[promptModalIndex].role}`
              : ''
          }`}
          onClose={() => setPromptModalIndex(null)}
        />
      )}

      {/* Regenerate Panel (Sheet) */}
      <Sheet open={regenModuleIndex !== null} onOpenChange={(open) => !open && setRegenModuleIndex(null)}>
        <SheetContent className="bg-slate-900 border-slate-700">
          <SheetHeader>
            <SheetTitle className="text-white">
              Regenerate {regenModuleIndex !== null && regenModuleIndex <= 1 ? 'Hero Pair' : `Module ${(regenModuleIndex ?? 0) + 1}`}
            </SheetTitle>
            <SheetDescription className="text-slate-400">
              Optionally describe what you'd like different. Leave empty to regenerate freely.
            </SheetDescription>
          </SheetHeader>

          <div className="mt-6 space-y-4">
            {/* Preview of module being regenerated */}
            {regenModuleIndex !== null && modules[regenModuleIndex] && (
              <div className="rounded-lg overflow-hidden border border-slate-700">
                <img
                  src={getActiveImageUrl(modules[regenModuleIndex], viewportMode)}
                  alt="Module to regenerate"
                  className="w-full h-48 object-contain bg-white"
                />
              </div>
            )}

            {/* Regen note */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Regeneration Notes (Optional)
              </label>
              <textarea
                value={regenNote}
                onChange={(e) => setRegenNote(e.target.value)}
                placeholder="e.g., 'Try a more minimal style' or 'Make it more vibrant'"
                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-redd-500 focus:border-transparent resize-none"
                rows={4}
              />
            </div>

            {/* Focus Images for regen */}
            {regenFocusAvailableImages && regenFocusAvailableImages.length > 0 && (
              <FocusImagePicker
                availableImages={regenFocusAvailableImages}
                selectedPaths={regenFocusImages.selectedPaths}
                onToggle={regenFocusImages.toggle}
                extraFile={regenFocusImages.extraFile}
                onExtraFile={regenFocusImages.addExtra}
                onRemoveExtra={regenFocusImages.removeExtra}
                variant="dark"
              />
            )}

            {/* Action buttons */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={async () => {
                  if (regenModuleIndex !== null) {
                    const refPaths = regenFocusImages.getSelectedPaths();

                    // Upload extra file if present and get its path
                    if (regenFocusImages.extraFile) {
                      try {
                        const uploadResult = await apiClient.uploadImage(regenFocusImages.extraFile.file);
                        refPaths.push(uploadResult.file_path);
                      } catch (err) {
                        console.error('Failed to upload extra reference image:', err);
                      }
                    }

                    const refs = refPaths.length > 0 ? refPaths : undefined;
                    if (isMobile) {
                      onRegenerateMobileModule?.(regenModuleIndex, regenNote.trim() || undefined, refs);
                    } else {
                      onRegenerateModule?.(regenModuleIndex, regenNote.trim() || undefined, refs);
                    }
                    setRegenModuleIndex(null);
                    setRegenNote('');
                  }
                }}
                className="flex-1 px-4 py-2 bg-redd-500 text-white font-medium rounded-lg hover:bg-redd-600 transition-colors"
              >
                Regenerate
              </button>
              <button
                onClick={() => setRegenModuleIndex(null)}
                className="px-4 py-2 bg-slate-800 text-slate-300 font-medium rounded-lg hover:bg-slate-700 border border-slate-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      {/* Edit Panel (Sheet) */}
      <Sheet open={editingModuleIndex !== null} onOpenChange={(open) => !open && setEditingModuleIndex(null)}>
        <SheetContent className="bg-slate-900 border-slate-700">
          <SheetHeader>
            <SheetTitle className="text-white">
              Edit Module {(editingModuleIndex ?? 0) + 1}
            </SheetTitle>
            <SheetDescription className="text-slate-400">
              Describe what changes you'd like to make. This will create a new version.
            </SheetDescription>
          </SheetHeader>

          <div className="mt-6 space-y-4">
            {/* Preview of module being edited */}
            {editingModuleIndex !== null && modules[editingModuleIndex] && (
              <div className="rounded-lg overflow-hidden border border-slate-700">
                <img
                  src={getActiveImageUrl(modules[editingModuleIndex], viewportMode)}
                  alt="Module to edit"
                  className="w-full h-48 object-contain bg-white"
                />
              </div>
            )}

            {/* Edit instructions */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Edit Instructions
              </label>
              <textarea
                value={editInstructions}
                onChange={(e) => setEditInstructions(e.target.value)}
                placeholder="e.g., 'Make the background darker' or 'Add more product detail on the left side'"
                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-redd-500 focus:border-transparent resize-none"
                rows={4}
              />
              <p className="mt-1 text-xs text-slate-500">
                Minimum 5 characters required
              </p>
            </div>

            {/* Focus images — select which references to send with edit */}
            {editFocusAvailableImages.length > 0 && (
              <FocusImagePicker
                availableImages={editFocusAvailableImages}
                selectedPaths={focusImages.selectedPaths}
                onToggle={focusImages.toggle}
                extraFile={focusImages.extraFile}
                onExtraFile={focusImages.addExtra}
                onRemoveExtra={focusImages.removeExtra}
                variant="dark"
              />
            )}

            {/* Action buttons */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={async () => {
                  if (editInstructions.trim().length >= 5 && editingModuleIndex !== null) {
                    const refPaths = focusImages.getSelectedPaths();

                    // Upload extra file if present and get its path
                    if (focusImages.extraFile) {
                      try {
                        const uploadResult = await apiClient.uploadImage(focusImages.extraFile.file);
                        refPaths.push(uploadResult.file_path);
                      } catch (err) {
                        console.error('Failed to upload extra reference image:', err);
                      }
                    }

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
                disabled={editInstructions.trim().length < 5}
                className="flex-1 px-4 py-2 bg-redd-500 text-white font-medium rounded-lg hover:bg-redd-600 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed transition-colors"
              >
                Apply Edit
              </button>
              <button
                onClick={() => setEditingModuleIndex(null)}
                className="px-4 py-2 bg-slate-800 text-slate-300 font-medium rounded-lg hover:bg-slate-700 border border-slate-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
};

export default AplusSection;
