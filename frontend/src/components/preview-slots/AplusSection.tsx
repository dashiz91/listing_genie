import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import type { AplusModuleType } from '@/api/types';
import { APLUS_DIMENSIONS } from '@/api/types';
import { PromptModal } from '@/components/PromptModal';
import type { SlotStatus } from './ImageSlot';

export interface AplusModule {
  id: string;
  type: AplusModuleType;
  index: number;
  status: SlotStatus;
  imageUrl?: string;
  imagePath?: string;
  errorMessage?: string;
  promptText?: string;
}

interface AplusSectionProps {
  modules: AplusModule[];
  sessionId?: string;
  productTitle?: string;
  accentColor?: string;
  visualScript?: import('@/api/types').AplusVisualScript | null;
  isGeneratingScript?: boolean;
  onGenerateModule?: (moduleIndex: number) => void;
  onRegenerateModule?: (moduleIndex: number) => void;
  onGenerateAll?: () => void;
  isEnabled?: boolean;
  className?: string;
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
  isEnabled = true,
  className,
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [promptModalIndex, setPromptModalIndex] = useState<number | null>(null);

  const handleDownload = async (module: AplusModule, idx: number) => {
    if (!module.imageUrl) return;
    try {
      const response = await fetch(module.imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const slug = productTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      a.download = `${slug}-aplus-module-${idx + 1}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Download failed:', e);
    }
  };

  const allPending = modules.every((m) => m.status === 'ready' || m.status === 'locked');
  const anyGenerating = modules.some((m) => m.status === 'generating');

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
      {/* Amazon-style header */}
      <div className="bg-gray-100 border-b border-gray-200 px-4 py-2.5">
        <span className="text-sm font-medium text-gray-700">From the manufacturer</span>
      </div>

      {/* Generate All button + Art Director planning state */}
      {allPending && !anyGenerating && !isGeneratingScript && sessionId && (
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

      {/* Modules */}
      <div className="p-4 space-y-3">
        {modules.map((module, idx) => {
          const dims = APLUS_DIMENSIONS[module.type];
          const canGenerate = canGenerateModule(idx);
          const isLocked = !canGenerate && module.status !== 'generating' && module.status !== 'complete';
          const isHovered = hoveredIndex === idx;
          const moduleLabel = getModuleLabel(idx, module.type);

          // Aspect ratio for sizing
          const aspectPercent = (dims.height / dims.width) * 100;

          return (
            <div key={module.id}>
              {/* Module role label */}
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {moduleLabel}
                </span>
                <span className="text-xs text-gray-400">
                  {idx + 1}/{modules.length}
                </span>
              </div>

              {/* Complete: show image with hover overlay */}
              {module.status === 'complete' && module.imageUrl && (
                <div
                  className="relative w-full rounded-lg overflow-hidden cursor-pointer"
                  style={{ paddingBottom: `${Math.min(aspectPercent, 60)}%` }}
                  onMouseEnter={() => setHoveredIndex(idx)}
                  onMouseLeave={() => setHoveredIndex(null)}
                >
                  <img
                    src={module.imageUrl}
                    alt={`A+ Module ${idx + 1}`}
                    className="absolute inset-0 w-full h-full object-cover"
                  />
                  {isHovered && (
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center gap-3 transition-opacity">
                      <button
                        onClick={() => onRegenerateModule?.(idx)}
                        className="px-4 py-2 bg-white rounded-lg text-sm font-medium text-gray-800 hover:bg-gray-100 transition-colors shadow-lg flex items-center gap-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Regenerate
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDownload(module, idx); }}
                        className="px-4 py-2 bg-white/90 rounded-lg text-sm font-medium text-gray-800 hover:bg-white transition-colors shadow-lg flex items-center gap-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download
                      </button>
                      {sessionId && (
                        <button
                          onClick={(e) => { e.stopPropagation(); setPromptModalIndex(idx); }}
                          className="px-4 py-2 bg-white/90 rounded-lg text-sm font-medium text-gray-800 hover:bg-white transition-colors shadow-lg flex items-center gap-2"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          View Prompt
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Generating: spinner */}
              {module.status === 'generating' && (
                <div
                  className="relative w-full rounded-lg border-2 border-gray-200 bg-gray-50 overflow-hidden"
                  style={{ paddingBottom: `${Math.min(aspectPercent, 60)}%` }}
                >
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
                    <div className="w-8 h-8 border-2 border-gray-300 rounded-full animate-spin" style={{ borderTopColor: accentColor }} />
                    <p className="text-sm text-gray-500">Generating {moduleLabel}...</p>
                  </div>
                </div>
              )}

              {/* Error */}
              {module.status === 'error' && (
                <div
                  className="relative w-full rounded-lg border-2 border-dashed border-red-300 bg-red-50 overflow-hidden cursor-pointer"
                  style={{ paddingBottom: `${Math.min(aspectPercent, 60)}%` }}
                  onClick={() => onGenerateModule?.(idx)}
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

              {/* Pending: can generate */}
              {(module.status === 'ready' || module.status === 'locked') && canGenerate && (
                <div
                  className="relative w-full rounded-lg border-2 border-dashed border-gray-300 bg-white hover:border-gray-400 hover:bg-gray-50 transition-colors cursor-pointer"
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

              {/* Pending: locked (waiting for previous) */}
              {(module.status === 'ready' || module.status === 'locked') && isLocked && (
                <div
                  className="relative w-full rounded-lg border-2 border-dashed border-gray-200 bg-gray-50 overflow-hidden"
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
    </div>
  );
};

export default AplusSection;
