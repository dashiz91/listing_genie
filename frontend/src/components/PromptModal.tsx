import React, { useState, useEffect } from 'react';
import type { PromptHistory } from '@/api/types';
import { apiClient } from '@/api/client';
import { normalizeColors } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';

interface PromptModalProps {
  /** Session ID for fetching prompt data */
  sessionId: string;
  /** Image type key: 'main', 'infographic_1', 'aplus_0', etc. */
  imageType: string;
  /** Optional prompt track for A+ prompt history */
  promptTrack?: 'desktop' | 'mobile';
  /** Human-readable title shown in the header, e.g. "Main Image" or "Module 1 — Hero" */
  title: string;
  /** Optional version number (1-based). If omitted, fetches the latest version. */
  version?: number;
  /** Called when the modal should close */
  onClose: () => void;
}

/**
 * Unified prompt viewer modal used by both listing images and A+ modules.
 * Fetches prompt data from the API and displays:
 *   - AI Designer context (product info, framework, copy, global note, analysis)
 *   - Reference images with click-to-zoom
 *   - User feedback / AI interpretation
 *   - Full prompt text
 */
export const PromptModal: React.FC<PromptModalProps> = ({
  sessionId,
  imageType,
  promptTrack,
  title,
  version,
  onClose,
}) => {
  const [prompt, setPrompt] = useState<PromptHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [zoomedImage, setZoomedImage] = useState<{ src: string; label: string } | null>(null);

  const getSemanticReferenceLabel = (type: string, label?: string) => {
    const normalized = (type || '').toLowerCase();
    if (normalized === 'primary') return 'PRODUCT_PHOTO';
    if (normalized === 'style_reference') return 'STYLE_REFERENCE';
    if (normalized === 'logo') return 'BRAND_LOGO';
    if (normalized === 'source_image') return 'SOURCE_IMAGE';
    if (normalized.startsWith('additional_product_')) return normalized.toUpperCase();
    if (normalized.startsWith('previous_module_')) return 'PREVIOUS_MODULE';
    if (normalized === 'gradient_canvas') return 'CANVAS_TO_COMPLETE';
    if (normalized === 'focus_reference' && label) return label.toUpperCase().replace(/\s+/g, '_');
    return null;
  };

  // Fetch prompt data on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiClient.getImagePrompt(sessionId, imageType, version, promptTrack);
        if (!cancelled) setPrompt(data);
      } catch {
        if (!cancelled) setError('No prompt found for this image.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [sessionId, imageType, version, promptTrack]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (zoomedImage) setZoomedImage(null);
        else onClose();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose, zoomedImage]);

  return (
    <>
      {/* Main modal overlay */}
      <div
        className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <div
          className="bg-slate-800 rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden shadow-xl border border-slate-700 flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-800/80 shrink-0">
            <div>
              <h3 className="text-lg font-semibold text-white">
                {title}
                {prompt && ` (v${prompt.version})`}
              </h3>
              <div className="flex items-center gap-2">
                {prompt?.model_name && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-700 text-slate-300">
                    {prompt.model_name}
                  </span>
                )}
                {prompt?.created_at && (
                  <span className="text-xs text-slate-400">
                    Generated: {new Date(prompt.created_at).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="p-4 overflow-y-auto flex-1">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Spinner size="lg" className="text-redd-500" />
                <span className="ml-2 text-slate-300">Loading prompt...</span>
              </div>
            ) : error ? (
              <div className="p-4 bg-yellow-900/30 rounded border border-yellow-700">
                <p className="text-sm text-yellow-300">{error}</p>
              </div>
            ) : prompt ? (
              <div className="space-y-4">
                {/* Designer Context */}
                {prompt.designer_context && (
                  <details className="p-3 bg-purple-900/20 rounded border border-purple-500/30" open>
                    <summary className="text-sm font-medium text-purple-300 cursor-pointer hover:text-purple-200">
                      AI Designer Context (click to collapse)
                    </summary>
                    <div className="mt-3 space-y-3 text-sm">
                      {/* Product Info */}
                      <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                        <p className="font-medium text-purple-300">Product Info:</p>
                        <p className="text-slate-200">Title: {prompt.designer_context.product_info?.title}</p>
                        {prompt.designer_context.product_info?.brand_name && (
                          <p className="text-slate-300">Brand: {prompt.designer_context.product_info.brand_name}</p>
                        )}
                        {prompt.designer_context.product_info?.target_audience && (
                          <p className="text-slate-300">Audience: {prompt.designer_context.product_info.target_audience}</p>
                        )}
                      </div>

                      {/* Framework Summary */}
                      {prompt.designer_context.framework_summary && (
                        <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                          <p className="font-medium text-purple-300">
                            Framework: {prompt.designer_context.framework_summary.name}
                          </p>
                          <p className="text-slate-300 text-xs mt-1">
                            {prompt.designer_context.framework_summary.philosophy}
                          </p>
                          <p className="text-slate-400 text-xs mt-1">
                            Voice: {prompt.designer_context.framework_summary.brand_voice}
                          </p>
                          {/* Colors */}
                          <div className="flex gap-1 mt-2">
                            {normalizeColors(prompt.designer_context.framework_summary.colors).map((c, i) => (
                              <div
                                key={i}
                                className="w-6 h-6 rounded border border-slate-500"
                                style={{ backgroundColor: c.hex }}
                                title={`${c.name || 'Color'} (${c.role || 'color'}): ${c.hex}`}
                              />
                            ))}
                          </div>
                          {/* Typography */}
                          {prompt.designer_context.framework_summary.typography && (
                            <p className="text-xs text-slate-400 mt-2">
                              Fonts: {prompt.designer_context.framework_summary.typography.headline_font} / {prompt.designer_context.framework_summary.typography.body_font}
                            </p>
                          )}
                        </div>
                      )}

                      {/* Image-specific Copy */}
                      {prompt.designer_context.image_copy && (
                        <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                          <p className="font-medium text-purple-300">Copy for this image:</p>
                          <p className="text-slate-200">"{(prompt.designer_context.image_copy as any).headline}"</p>
                          {(prompt.designer_context.image_copy as any).feature_callouts?.length > 0 && (
                            <ul className="text-xs text-slate-300 mt-1 list-disc list-inside">
                              {(prompt.designer_context.image_copy as any).feature_callouts.map((f: string, i: number) => (
                                <li key={i}>{f}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      )}

                      {/* Visual Script (A+ modules) */}
                      {(prompt.designer_context as any).module_script && (
                        <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                          <p className="font-medium text-purple-300">Art Director Script:</p>
                          <p className="text-slate-200 text-xs mt-1">
                            Role: {(prompt.designer_context as any).module_script.role}
                          </p>
                          <p className="text-slate-300 text-xs">
                            Headline: "{(prompt.designer_context as any).module_script.headline}"
                          </p>
                          <p className="text-slate-400 text-xs">
                            Mood: {(prompt.designer_context as any).module_script.mood}
                          </p>
                        </div>
                      )}

                      {/* Global Note */}
                      {prompt.designer_context.global_note && (
                        <div className="p-2 bg-yellow-900/20 rounded border border-yellow-500/30">
                          <p className="font-medium text-yellow-300">Global Instructions:</p>
                          <p className="text-yellow-200 text-xs">{prompt.designer_context.global_note}</p>
                        </div>
                      )}

                      {/* Product Analysis */}
                      {prompt.designer_context.product_analysis && (
                        <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                          <p className="font-medium text-purple-300">AI Product Analysis:</p>
                          <pre className="text-xs text-slate-300 whitespace-pre-wrap mt-1 max-h-32 overflow-y-auto">
                            {JSON.stringify(prompt.designer_context.product_analysis, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </details>
                )}

                {/* Reference Images */}
                {prompt.reference_images && prompt.reference_images.length > 0 && (
                  <div className="p-3 bg-green-900/20 rounded border border-green-500/30">
                    <p className="text-sm font-medium text-green-300 mb-2">
                      Reference Images Used ({prompt.reference_images.length}):
                    </p>
                    <div className="flex flex-wrap gap-3">
                      {prompt.reference_images.map((ref, idx) => {
                        const imgSrc = apiClient.getFileUrl(ref.path);
                        const isStyleRef = ref.type === 'style_reference';
                        const refLabel = (ref as { label?: string }).label;
                        const semanticLabel = getSemanticReferenceLabel(ref.type, refLabel);
                        const fallbackLabel = ref.type ? ref.type.replace(/_/g, ' ').toUpperCase() : 'REFERENCE_IMAGE';
                        const label = semanticLabel || refLabel || fallbackLabel;
                        const sourceLabel = refLabel && refLabel !== label ? refLabel : null;
                        return (
                          <button
                            key={idx}
                            onClick={() => setZoomedImage({ src: imgSrc, label })}
                            className={`group flex flex-col items-center cursor-pointer ${isStyleRef ? 'p-2 bg-blue-900/30 rounded-lg' : ''}`}
                          >
                            <div className={`relative rounded overflow-hidden border ${
                              isStyleRef
                                ? 'w-24 h-24 border-blue-500 border-2'
                                : 'w-16 h-16 border-green-600'
                            }`}>
                              <img
                                src={imgSrc}
                                alt={label}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  (e.currentTarget as HTMLImageElement).style.display = 'none';
                                }}
                              />
                              {/* Hover zoom overlay */}
                              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center">
                                <svg className="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                                </svg>
                              </div>
                            </div>
                            <span className={`text-xs mt-1 ${
                              isStyleRef ? 'text-blue-300 font-semibold' : 'text-green-300'
                            }`}>
                              {label}
                            </span>
                            {sourceLabel && (
                              <span className="text-[10px] text-slate-400">
                                source: {sourceLabel}
                              </span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                    <p className="text-xs text-green-400 mt-2">
                      These images were sent to Gemini as visual context
                    </p>
                  </div>
                )}

                {/* User Feedback */}
                {prompt.user_feedback && (
                  <div className="p-3 bg-yellow-900/20 rounded border border-yellow-500/30">
                    <p className="text-sm font-medium text-yellow-300 mb-1">
                      User Regeneration Request:
                    </p>
                    <p className="text-sm text-yellow-200">{prompt.user_feedback}</p>
                  </div>
                )}

                {/* AI Interpretation */}
                {prompt.change_summary && (
                  <div className="p-3 bg-blue-900/20 rounded border border-blue-500/30">
                    <p className="text-sm font-medium text-blue-300 mb-1">
                      AI Interpretation:
                    </p>
                    <p className="text-sm text-blue-200">{prompt.change_summary}</p>
                  </div>
                )}

                {/* Full Prompt */}
                <div>
                  <p className="text-sm font-medium text-slate-200 mb-2">
                    Full Prompt Sent to Gemini:
                  </p>
                  <pre className="whitespace-pre-wrap text-sm bg-slate-900 p-4 rounded border border-slate-600 font-mono text-slate-300 max-h-96 overflow-y-auto">
                    {prompt.prompt_text}
                  </pre>
                </div>
              </div>
            ) : null}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-slate-700 bg-slate-800/80 shrink-0">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-700 text-white rounded hover:bg-slate-600 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>

      {/* Zoomed reference image overlay */}
      {zoomedImage && (
        <div
          className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setZoomedImage(null)}
        >
          <div
            className="relative bg-slate-800 rounded-xl shadow-2xl max-w-lg w-full mx-4 overflow-hidden border border-slate-700"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
              <span className="text-sm font-medium text-slate-200 capitalize">{zoomedImage.label}</span>
              <button
                onClick={() => setZoomedImage(null)}
                className="p-1 text-slate-400 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 flex items-center justify-center bg-slate-900 min-h-[200px]">
              <img
                src={zoomedImage.src}
                alt={zoomedImage.label}
                className="max-w-full max-h-[60vh] object-contain rounded"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  const parent = e.currentTarget.parentElement;
                  if (parent) {
                    const msg = document.createElement('p');
                    msg.className = 'text-sm text-slate-400';
                    msg.textContent = 'Failed to load image';
                    parent.appendChild(msg);
                  }
                }}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

