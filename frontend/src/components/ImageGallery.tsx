import React, { useState } from 'react';
import { apiClient } from '../api/client';
import type { SessionImage, GenerationStatus, PromptHistory } from '../api/types';
import { normalizeColors } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';

interface ImageGalleryProps {
  sessionId: string;
  images: SessionImage[];
  status: GenerationStatus;
  onRetry?: () => void;
  onRegenerateSingle?: (imageType: string, note?: string) => void;
  onEditSingle?: (imageType: string, editInstructions: string) => void;
}

export const ImageGallery: React.FC<ImageGalleryProps> = ({
  sessionId,
  images,
  status: _status, // Used for component context
  onRetry,
  onRegenerateSingle,
  onEditSingle,
}) => {
  const [selectedImage, setSelectedImage] = useState<SessionImage | null>(null);
  // Cache-busting: track when each image was last updated to force browser reload
  const [imageCacheKey, setImageCacheKey] = useState<Record<string, number>>({});
  // Edit state for lightbox
  const [editNote, setEditNote] = useState('');
  const [showEditInput, setShowEditInput] = useState(false);
  // Prompt viewer state
  const [showPromptModal, setShowPromptModal] = useState<string | null>(null);
  const [currentPrompt, setCurrentPrompt] = useState<PromptHistory | null>(null);
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [promptError, setPromptError] = useState<string | null>(null);

  void _status; // Acknowledge unused prop

  const hasFailedImages = images.some((img) => img.status === 'failed');

  // Get image URL with cache-busting parameter to force reload after edit/regenerate
  const getImageUrlWithCache = (imageType: string) => {
    const baseUrl = apiClient.getImageUrl(sessionId, imageType);
    const cacheKey = imageCacheKey[imageType];
    return cacheKey ? apiClient.withCacheBust(baseUrl, cacheKey) : baseUrl;
  };

  const handleQuickRegenerate = (imageType: string) => {
    onRegenerateSingle?.(imageType);
    setImageCacheKey((prev) => ({ ...prev, [imageType]: Date.now() }));
  };

  const handleEditSubmit = (imageType: string) => {
    if (editNote && editNote.trim().length >= 5) {
      onEditSingle?.(imageType, editNote.trim());
      setShowEditInput(false);
      setEditNote('');
      setImageCacheKey((prev) => ({ ...prev, [imageType]: Date.now() }));
    }
  };

  const handleViewPrompt = async (imageType: string) => {
    setLoadingPrompt(true);
    setPromptError(null);
    try {
      const prompt = await apiClient.getImagePrompt(sessionId, imageType);
      setCurrentPrompt(prompt);
      setShowPromptModal(imageType);
    } catch (err) {
      console.error('Failed to load prompt:', err);
      setPromptError('No prompt found for this image.');
      setShowPromptModal(imageType);
    } finally {
      setLoadingPrompt(false);
    }
  };

  const downloadImage = async (imageType: string, label: string) => {
    const url = apiClient.getImageUrl(sessionId, imageType);
    const response = await fetch(url);
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `${label.toLowerCase().replace(' ', '_')}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);
  };

  const downloadAll = async () => {
    const completeImages = images.filter((img) => img.status === 'complete');
    for (const img of completeImages) {
      await downloadImage(img.type, img.label);
      // Small delay between downloads
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  };

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex justify-end gap-2">
        {hasFailedImages && onRetry && (
          <button
            onClick={onRetry}
            className="px-3 py-1.5 text-sm bg-yellow-600/20 text-yellow-400 rounded-lg hover:bg-yellow-600/30 transition-colors border border-yellow-600/30"
          >
            Retry Failed
          </button>
        )}
        {images.some((img) => img.status === 'complete') && (
          <button
            onClick={downloadAll}
            className="px-3 py-1.5 text-sm bg-redd-500 text-white rounded-lg hover:bg-redd-600 transition-colors"
          >
            Download All
          </button>
        )}
      </div>

      {/* Image Grid - Mockup Style */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        {images.map((image, index) => (
          <div key={`${image.type}-${index}`} className="group">
            {/* Image Card */}
            <div
              className="relative aspect-square bg-slate-800 rounded-xl overflow-hidden cursor-pointer
                         border border-slate-700 hover:border-redd-500/50 transition-all"
              onClick={() => image.status === 'complete' && setSelectedImage(image)}
            >
              {image.status === 'complete' && image.url ? (
                <>
                  <img
                    src={getImageUrlWithCache(image.type)}
                    alt={image.label}
                    className="w-full h-full object-cover"
                  />
                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <button
                      onClick={(e) => { e.stopPropagation(); downloadImage(image.type, image.label); }}
                      className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
                      title="Download"
                    >
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                    </button>
                    {onRegenerateSingle && (
                      <button
                        onClick={(e) => { e.stopPropagation(); handleQuickRegenerate(image.type); }}
                        className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
                        title="Regenerate"
                      >
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      </button>
                    )}
                    {onEditSingle && (
                      <button
                        onClick={(e) => { e.stopPropagation(); setShowEditInput(true); setSelectedImage(image); }}
                        className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
                        title="Edit"
                      >
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    )}
                    <button
                      onClick={(e) => { e.stopPropagation(); handleViewPrompt(image.type); }}
                      className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
                      title="View Prompt"
                    >
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </button>
                  </div>
                </>
              ) : image.status === 'processing' ? (
                <div className="absolute inset-0 flex items-center justify-center bg-slate-800">
                  <Spinner size="lg" className="text-redd-500" />
                </div>
              ) : image.status === 'pending' ? (
                <div className="absolute inset-0 flex items-center justify-center bg-slate-800">
                  <div className="text-slate-500 text-3xl">○</div>
                </div>
              ) : (
                <div className="absolute inset-0 flex items-center justify-center bg-slate-800">
                  <div className="text-red-400 text-3xl">!</div>
                </div>
              )}
            </div>

            {/* Label */}
            <p className="mt-2 text-sm text-slate-400 text-center">{image.label}</p>
          </div>
        ))}
      </div>

      {/* Lightbox Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center p-4"
          onClick={() => { setSelectedImage(null); setShowEditInput(false); setEditNote(''); }}
        >
          <div className="relative max-w-4xl w-full" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => { setSelectedImage(null); setShowEditInput(false); setEditNote(''); }}
              className="absolute -top-12 right-0 text-white hover:text-slate-300 transition-colors"
            >
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <img
              src={getImageUrlWithCache(selectedImage.type)}
              alt={selectedImage.label}
              className="w-full h-auto rounded-lg"
            />
            <div className="mt-4 flex items-center justify-between">
              <h3 className="text-white text-lg font-medium">{selectedImage.label}</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => downloadImage(selectedImage.type, selectedImage.label)}
                  className="px-4 py-2 bg-redd-500 text-white text-sm rounded-lg hover:bg-redd-600 transition-colors"
                >
                  Download
                </button>
              </div>
            </div>

            {/* Edit Section */}
            {showEditInput && onEditSingle && (
              <div className="mt-4 p-4 bg-slate-800 rounded-lg border border-slate-700">
                <p className="text-sm text-slate-300 mb-2">
                  Describe what to change:
                </p>
                <textarea
                  value={editNote}
                  onChange={(e) => setEditNote(e.target.value)}
                  placeholder="e.g., 'Change headline to Premium Quality' or 'Make background lighter'"
                  className="w-full px-3 py-2 text-sm bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:ring-2 focus:ring-redd-500 focus:border-redd-500"
                  rows={2}
                />
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={() => handleEditSubmit(selectedImage.type)}
                    disabled={!editNote || editNote.trim().length < 5}
                    className="px-4 py-2 text-sm bg-redd-500 text-white rounded-lg hover:bg-redd-600 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors"
                  >
                    Apply Edit
                  </button>
                  <button
                    onClick={() => { setShowEditInput(false); setEditNote(''); }}
                    className="px-4 py-2 text-sm bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Prompt Viewer Modal */}
      {showPromptModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-4"
          onClick={() => {
            setShowPromptModal(null);
            setCurrentPrompt(null);
            setPromptError(null);
          }}
        >
          <div
            className="bg-slate-800 rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden shadow-xl border border-slate-700"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-800/80">
              <div>
                <h3 className="text-lg font-semibold text-white">
                  Prompt for {showPromptModal.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  {currentPrompt && ` (v${currentPrompt.version})`}
                </h3>
                {currentPrompt?.created_at && (
                  <p className="text-xs text-slate-400">
                    Generated: {new Date(currentPrompt.created_at).toLocaleString()}
                  </p>
                )}
              </div>
              <button
                onClick={() => {
                  setShowPromptModal(null);
                  setCurrentPrompt(null);
                  setPromptError(null);
                }}
                className="text-slate-400 hover:text-white p-1 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {loadingPrompt ? (
                <div className="flex items-center justify-center py-8">
                  <Spinner size="lg" className="text-redd-500" />
                  <span className="ml-2 text-slate-300">Loading prompt...</span>
                </div>
              ) : promptError ? (
                <div className="p-4 bg-yellow-900/30 rounded border border-yellow-700">
                  <p className="text-sm text-yellow-300">{promptError}</p>
                </div>
              ) : currentPrompt ? (
                <div className="space-y-4">
                  {/* Designer Context Section - Full transparency */}
                  {currentPrompt.designer_context && (
                    <details className="p-3 bg-purple-900/20 rounded border border-purple-500/30">
                      <summary className="text-sm font-medium text-purple-300 cursor-pointer hover:text-purple-200">
                        🧠 AI Designer Context (click to expand)
                      </summary>
                      <div className="mt-3 space-y-3 text-sm">
                        {/* Product Info */}
                        <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                          <p className="font-medium text-purple-300">Product Info:</p>
                          <p className="text-slate-200">Title: {currentPrompt.designer_context.product_info.title}</p>
                          {currentPrompt.designer_context.product_info.brand_name && (
                            <p className="text-slate-300">Brand: {currentPrompt.designer_context.product_info.brand_name}</p>
                          )}
                          {currentPrompt.designer_context.product_info.target_audience && (
                            <p className="text-slate-300">Audience: {currentPrompt.designer_context.product_info.target_audience}</p>
                          )}
                        </div>

                        {/* Framework Summary */}
                        {currentPrompt.designer_context.framework_summary && (
                          <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                            <p className="font-medium text-purple-300">
                              Framework: {currentPrompt.designer_context.framework_summary.name}
                            </p>
                            <p className="text-slate-300 text-xs mt-1">
                              {currentPrompt.designer_context.framework_summary.philosophy}
                            </p>
                            <p className="text-slate-400 text-xs mt-1">
                              Voice: {currentPrompt.designer_context.framework_summary.brand_voice}
                            </p>
                            {/* Colors */}
                            <div className="flex gap-1 mt-2">
                              {normalizeColors(currentPrompt.designer_context.framework_summary.colors).map((c, i) => (
                                <div
                                  key={i}
                                  className="w-6 h-6 rounded border border-slate-500"
                                  style={{ backgroundColor: c.hex }}
                                  title={`${c.name || 'Color'} (${c.role || 'color'}): ${c.hex}`}
                                />
                              ))}
                            </div>
                            {/* Typography */}
                            <p className="text-xs text-slate-400 mt-2">
                              Fonts: {currentPrompt.designer_context.framework_summary.typography.headline_font} / {currentPrompt.designer_context.framework_summary.typography.body_font}
                            </p>
                          </div>
                        )}

                        {/* Image-specific Copy */}
                        {currentPrompt.designer_context.image_copy && (
                          <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                            <p className="font-medium text-purple-300">Copy for this image:</p>
                            <p className="text-slate-200">"{currentPrompt.designer_context.image_copy.headline}"</p>
                            {currentPrompt.designer_context.image_copy.feature_callouts && currentPrompt.designer_context.image_copy.feature_callouts.length > 0 && (
                              <ul className="text-xs text-slate-300 mt-1 list-disc list-inside">
                                {currentPrompt.designer_context.image_copy.feature_callouts.map((f, i) => (
                                  <li key={i}>{f}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}

                        {/* Global Note */}
                        {currentPrompt.designer_context.global_note && (
                          <div className="p-2 bg-yellow-900/20 rounded border border-yellow-500/30">
                            <p className="font-medium text-yellow-300">Global Instructions:</p>
                            <p className="text-yellow-200 text-xs">{currentPrompt.designer_context.global_note}</p>
                          </div>
                        )}

                        {/* Product Analysis */}
                        {currentPrompt.designer_context.product_analysis && (
                          <div className="p-2 bg-slate-700/50 rounded border border-purple-500/20">
                            <p className="font-medium text-purple-300">AI Product Analysis:</p>
                            <pre className="text-xs text-slate-300 whitespace-pre-wrap mt-1 max-h-32 overflow-y-auto">
                              {JSON.stringify(currentPrompt.designer_context.product_analysis, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </details>
                  )}

                  {/* Reference Images Section */}
                  {currentPrompt.reference_images && currentPrompt.reference_images.length > 0 && (
                    <div className="p-3 bg-green-900/20 rounded border border-green-500/30">
                      <p className="text-sm font-medium text-green-300 mb-2">
                        🖼️ Reference Images Used ({currentPrompt.reference_images.length}):
                      </p>
                      <div className="flex flex-wrap gap-3">
                        {currentPrompt.reference_images.map((ref, idx) => {
                          const isStyleRef = ref.type === 'style_reference';
                          const fallbackLabel = isStyleRef ? 'Style Reference' : ref.type.replace(/_/g, ' ');
                          const label = ref.label || fallbackLabel;
                          return (
                            <div
                              key={idx}
                              className={`flex flex-col items-center ${isStyleRef ? 'p-2 bg-blue-900/30 rounded-lg' : ''}`}
                            >
                              <img
                                src={apiClient.getFileUrl(ref.path)}
                                alt={label}
                                className={`object-cover rounded border ${
                                  isStyleRef
                                    ? 'w-24 h-24 border-blue-500 border-2'
                                    : 'w-16 h-16 border-green-600'
                                }`}
                                onError={(e) => {
                                  // Fallback for images that can't load
                                  (e.target as HTMLImageElement).style.display = 'none';
                                }}
                              />
                              <span className={`text-xs mt-1 ${
                                isStyleRef ? 'text-blue-300 font-semibold' : 'text-green-300'
                              }`}>
                                {isStyleRef ? '⭐ Style Reference' : label}
                              </span>
                              {isStyleRef && (
                                <span className="text-[10px] text-blue-400">
                                  (AI follows this style)
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                      <p className="text-xs text-green-400 mt-2">
                        These images were sent to Gemini as visual context
                      </p>
                    </div>
                  )}

                  {/* User Feedback Section (if regeneration) */}
                  {currentPrompt.user_feedback && (
                    <div className="p-3 bg-yellow-900/20 rounded border border-yellow-500/30">
                      <p className="text-sm font-medium text-yellow-300 mb-1">
                        🔄 User Regeneration Request:
                      </p>
                      <p className="text-sm text-yellow-200">{currentPrompt.user_feedback}</p>
                    </div>
                  )}

                  {/* AI Interpretation (if available) */}
                  {currentPrompt.change_summary && (
                    <div className="p-3 bg-blue-900/20 rounded border border-blue-500/30">
                      <p className="text-sm font-medium text-blue-300 mb-1">
                        🤖 AI Interpretation:
                      </p>
                      <p className="text-sm text-blue-200">{currentPrompt.change_summary}</p>
                    </div>
                  )}

                  {/* Main Prompt Text */}
                  <div>
                    <p className="text-sm font-medium text-slate-200 mb-2">
                      Full Prompt Sent to Gemini:
                    </p>
                    <pre className="whitespace-pre-wrap text-sm bg-slate-900 p-4 rounded border border-slate-600 font-mono text-slate-300 max-h-96 overflow-y-auto">
                      {currentPrompt.prompt_text}
                    </pre>
                  </div>
                </div>
              ) : null}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-700 bg-slate-800/80">
              <button
                onClick={() => {
                  setShowPromptModal(null);
                  setCurrentPrompt(null);
                  setPromptError(null);
                }}
                className="px-4 py-2 bg-slate-700 text-white rounded hover:bg-slate-600 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
