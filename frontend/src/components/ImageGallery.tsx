import React, { useState } from 'react';
import { apiClient } from '../api/client';
import type { SessionImage, GenerationStatus, PromptHistory } from '../api/types';

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
  status,
  onRetry,
  onRegenerateSingle,
  onEditSingle,
}) => {
  const [selectedImage, setSelectedImage] = useState<SessionImage | null>(null);
  const [regenerateNote, setRegenerateNote] = useState<Record<string, string>>({});
  const [showNoteInput, setShowNoteInput] = useState<Record<string, boolean>>({});
  // Edit state
  const [editNote, setEditNote] = useState<Record<string, string>>({});
  const [showEditInput, setShowEditInput] = useState<Record<string, boolean>>({});
  // Cache-busting: track when each image was last updated to force browser reload
  const [imageCacheKey, setImageCacheKey] = useState<Record<string, number>>({});
  // Prompt viewer state
  const [showPromptModal, setShowPromptModal] = useState<string | null>(null); // image_type
  const [currentPrompt, setCurrentPrompt] = useState<PromptHistory | null>(null);
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [promptError, setPromptError] = useState<string | null>(null);

  const hasFailedImages = images.some((img) => img.status === 'failed');

  // Get image URL with cache-busting parameter to force reload after edit/regenerate
  const getImageUrlWithCache = (imageType: string) => {
    const baseUrl = apiClient.getImageUrl(sessionId, imageType);
    const cacheKey = imageCacheKey[imageType];
    return cacheKey ? `${baseUrl}?t=${cacheKey}` : baseUrl;
  };

  const handleRegenerateClick = (imageType: string) => {
    if (showNoteInput[imageType]) {
      // If note input is shown, trigger regeneration
      onRegenerateSingle?.(imageType, regenerateNote[imageType] || undefined);
      setShowNoteInput((prev) => ({ ...prev, [imageType]: false }));
      setRegenerateNote((prev) => ({ ...prev, [imageType]: '' }));
      // Set cache key to force image reload when done
      setImageCacheKey((prev) => ({ ...prev, [imageType]: Date.now() }));
    } else {
      // Show note input
      setShowNoteInput((prev) => ({ ...prev, [imageType]: true }));
    }
  };

  const handleQuickRegenerate = (imageType: string) => {
    onRegenerateSingle?.(imageType);
    // Set cache key to force image reload when done
    setImageCacheKey((prev) => ({ ...prev, [imageType]: Date.now() }));
  };

  const handleEditSubmit = (imageType: string) => {
    const instructions = editNote[imageType];
    if (instructions && instructions.trim().length >= 5) {
      onEditSingle?.(imageType, instructions.trim());
      setShowEditInput((prev) => ({ ...prev, [imageType]: false }));
      setEditNote((prev) => ({ ...prev, [imageType]: '' }));
      // Set cache key to force image reload when done
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
      setPromptError('No prompt found for this image. It may not have been generated through the framework system.');
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
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Generated Images</h2>
          <p className="text-gray-600">
            {status === 'complete' && 'All images generated successfully!'}
            {status === 'partial' && 'Some images generated. Others failed.'}
            {status === 'processing' && 'Generating images...'}
            {status === 'failed' && 'Generation failed.'}
          </p>
        </div>
        <div className="flex space-x-2">
          {hasFailedImages && onRetry && (
            <button
              onClick={onRetry}
              className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
            >
              Retry Failed
            </button>
          )}
          {images.some((img) => img.status === 'complete') && (
            <button
              onClick={downloadAll}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Download All
            </button>
          )}
        </div>
      </div>

      {/* Image Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {images.map((image, index) => (
          <div
            key={`${image.type}-${index}`}
            className="bg-white rounded-lg shadow-md overflow-hidden"
          >
            {/* Image Container */}
            <div
              className="relative aspect-square bg-gray-100 cursor-pointer"
              onClick={() => image.status === 'complete' && setSelectedImage(image)}
            >
              {image.status === 'complete' && image.url ? (
                <img
                  src={getImageUrlWithCache(image.type)}
                  alt={image.label}
                  className="w-full h-full object-contain hover:opacity-90 transition-opacity"
                />
              ) : image.status === 'processing' ? (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-2"></div>
                    <p className="text-gray-500">Generating...</p>
                  </div>
                </div>
              ) : image.status === 'pending' ? (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center text-gray-400">
                    <div className="text-4xl mb-2">⏳</div>
                    <p>Pending</p>
                  </div>
                </div>
              ) : (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center text-red-500">
                    <div className="text-4xl mb-2">⚠️</div>
                    <p className="px-4 text-sm">{image.error || 'Failed'}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Image Info */}
            <div className="p-4">
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-gray-900">{image.label}</h3>
                <div className="flex gap-2">
                  {image.status === 'complete' && (
                    <>
                      <button
                        onClick={() => handleViewPrompt(image.type)}
                        className="text-gray-500 hover:text-gray-700 text-sm font-medium"
                        title="View the prompt used to generate this image"
                      >
                        📝 Prompt
                      </button>
                      <button
                        onClick={() => downloadImage(image.type, image.label)}
                        className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                      >
                        Download
                      </button>
                    </>
                  )}
                </div>
              </div>
              <div className="mt-1 flex items-center justify-between">
                <span
                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                    ${image.status === 'complete' ? 'bg-green-100 text-green-800' : ''}
                    ${image.status === 'processing' ? 'bg-blue-100 text-blue-800' : ''}
                    ${image.status === 'pending' ? 'bg-gray-100 text-gray-800' : ''}
                    ${image.status === 'failed' ? 'bg-red-100 text-red-800' : ''}
                  `}
                >
                  {image.status === 'complete' && '✓ Complete'}
                  {image.status === 'processing' && '⟳ Processing'}
                  {image.status === 'pending' && '◷ Pending'}
                  {image.status === 'failed' && '✕ Failed'}
                </span>

                {/* Action buttons - show for complete or failed images */}
                {(image.status === 'complete' || image.status === 'failed') && (
                  <div className="flex gap-2">
                    {onRegenerateSingle && (
                      <button
                        onClick={() => handleQuickRegenerate(image.type)}
                        className="text-xs text-purple-600 hover:text-purple-700 font-medium"
                        title="Regenerate from scratch"
                      >
                        ↻ Regenerate
                      </button>
                    )}
                    {onEditSingle && image.status === 'complete' && (
                      <button
                        onClick={() => setShowEditInput((prev) => ({ ...prev, [image.type]: !prev[image.type] }))}
                        className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                        title="Edit this image"
                      >
                        ✎ Edit
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Note input for regeneration */}
              {onRegenerateSingle && (image.status === 'complete' || image.status === 'failed') && (
                <div className="mt-2">
                  {showNoteInput[image.type] ? (
                    <div className="space-y-2">
                      <textarea
                        value={regenerateNote[image.type] || ''}
                        onChange={(e) =>
                          setRegenerateNote((prev) => ({ ...prev, [image.type]: e.target.value }))
                        }
                        placeholder="Add instructions for regeneration (optional)..."
                        className="w-full px-2 py-1 text-xs border border-purple-300 rounded focus:ring-1 focus:ring-purple-500 focus:border-purple-500"
                        rows={2}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleRegenerateClick(image.type)}
                          className="flex-1 px-2 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700"
                        >
                          Regenerate with Note
                        </button>
                        <button
                          onClick={() => setShowNoteInput((prev) => ({ ...prev, [image.type]: false }))}
                          className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setShowNoteInput((prev) => ({ ...prev, [image.type]: true }))}
                      className="text-xs text-gray-500 hover:text-purple-600"
                    >
                      + Add note & regenerate
                    </button>
                  )}
                </div>
              )}

              {/* Edit input - for modifying existing image */}
              {onEditSingle && image.status === 'complete' && showEditInput[image.type] && (
                <div className="mt-2 space-y-2 p-2 bg-blue-50 rounded border border-blue-200">
                  <p className="text-xs text-blue-700 font-medium">
                    Edit this image (keeps layout, modifies specifics)
                  </p>
                  <textarea
                    value={editNote[image.type] || ''}
                    onChange={(e) =>
                      setEditNote((prev) => ({ ...prev, [image.type]: e.target.value }))
                    }
                    placeholder="Describe what to change (e.g., 'Change headline to Premium Quality' or 'Make background lighter')"
                    className="w-full px-2 py-1 text-xs border border-blue-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    rows={2}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEditSubmit(image.type)}
                      disabled={!editNote[image.type] || editNote[image.type].trim().length < 5}
                      className="flex-1 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      Apply Edit
                    </button>
                    <button
                      onClick={() => {
                        setShowEditInput((prev) => ({ ...prev, [image.type]: false }));
                        setEditNote((prev) => ({ ...prev, [image.type]: '' }));
                      }}
                      className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Lightbox Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl w-full">
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-12 right-0 text-white hover:text-gray-300"
            >
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <img
              src={getImageUrlWithCache(selectedImage.type)}
              alt={selectedImage.label}
              className="w-full h-auto rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
            <div className="mt-4 text-center">
              <h3 className="text-white text-xl font-semibold">{selectedImage.label}</h3>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  downloadImage(selectedImage.type, selectedImage.label);
                }}
                className="mt-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Download
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Prompt Viewer Modal */}
      {showPromptModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
          onClick={() => {
            setShowPromptModal(null);
            setCurrentPrompt(null);
            setPromptError(null);
          }}
        >
          <div
            className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-4 border-b flex justify-between items-center bg-gray-50">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Prompt for {showPromptModal.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  {currentPrompt && ` (v${currentPrompt.version})`}
                </h3>
                {currentPrompt?.created_at && (
                  <p className="text-xs text-gray-500">
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
                className="text-gray-400 hover:text-gray-600 p-1"
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
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  <span className="ml-2 text-gray-600">Loading prompt...</span>
                </div>
              ) : promptError ? (
                <div className="p-4 bg-yellow-50 rounded border border-yellow-200">
                  <p className="text-sm text-yellow-800">{promptError}</p>
                </div>
              ) : currentPrompt ? (
                <div className="space-y-4">
                  {/* Designer Context Section - Full transparency */}
                  {currentPrompt.designer_context && (
                    <details className="p-3 bg-purple-50 rounded border border-purple-200">
                      <summary className="text-sm font-medium text-purple-800 cursor-pointer hover:text-purple-900">
                        🧠 AI Designer Context (click to expand)
                      </summary>
                      <div className="mt-3 space-y-3 text-sm">
                        {/* Product Info */}
                        <div className="p-2 bg-white rounded border border-purple-100">
                          <p className="font-medium text-purple-700">Product Info:</p>
                          <p className="text-gray-700">Title: {currentPrompt.designer_context.product_info.title}</p>
                          {currentPrompt.designer_context.product_info.brand_name && (
                            <p className="text-gray-600">Brand: {currentPrompt.designer_context.product_info.brand_name}</p>
                          )}
                          {currentPrompt.designer_context.product_info.target_audience && (
                            <p className="text-gray-600">Audience: {currentPrompt.designer_context.product_info.target_audience}</p>
                          )}
                        </div>

                        {/* Framework Summary */}
                        {currentPrompt.designer_context.framework_summary && (
                          <div className="p-2 bg-white rounded border border-purple-100">
                            <p className="font-medium text-purple-700">
                              Framework: {currentPrompt.designer_context.framework_summary.name}
                            </p>
                            <p className="text-gray-600 text-xs mt-1">
                              {currentPrompt.designer_context.framework_summary.philosophy}
                            </p>
                            <p className="text-gray-500 text-xs mt-1">
                              Voice: {currentPrompt.designer_context.framework_summary.brand_voice}
                            </p>
                            {/* Colors */}
                            <div className="flex gap-1 mt-2">
                              {currentPrompt.designer_context.framework_summary.colors.map((c, i) => (
                                <div
                                  key={i}
                                  className="w-6 h-6 rounded border border-gray-300"
                                  style={{ backgroundColor: c.hex }}
                                  title={`${c.name} (${c.role}): ${c.hex}`}
                                />
                              ))}
                            </div>
                            {/* Typography */}
                            <p className="text-xs text-gray-500 mt-2">
                              Fonts: {currentPrompt.designer_context.framework_summary.typography.headline_font} / {currentPrompt.designer_context.framework_summary.typography.body_font}
                            </p>
                          </div>
                        )}

                        {/* Image-specific Copy */}
                        {currentPrompt.designer_context.image_copy && (
                          <div className="p-2 bg-white rounded border border-purple-100">
                            <p className="font-medium text-purple-700">Copy for this image:</p>
                            <p className="text-gray-700">"{currentPrompt.designer_context.image_copy.headline}"</p>
                            {currentPrompt.designer_context.image_copy.feature_callouts && currentPrompt.designer_context.image_copy.feature_callouts.length > 0 && (
                              <ul className="text-xs text-gray-600 mt-1 list-disc list-inside">
                                {currentPrompt.designer_context.image_copy.feature_callouts.map((f, i) => (
                                  <li key={i}>{f}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}

                        {/* Global Note */}
                        {currentPrompt.designer_context.global_note && (
                          <div className="p-2 bg-yellow-50 rounded border border-yellow-200">
                            <p className="font-medium text-yellow-700">Global Instructions:</p>
                            <p className="text-yellow-800 text-xs">{currentPrompt.designer_context.global_note}</p>
                          </div>
                        )}

                        {/* Product Analysis */}
                        {currentPrompt.designer_context.product_analysis && (
                          <div className="p-2 bg-white rounded border border-purple-100">
                            <p className="font-medium text-purple-700">AI Product Analysis:</p>
                            <pre className="text-xs text-gray-600 whitespace-pre-wrap mt-1 max-h-32 overflow-y-auto">
                              {JSON.stringify(currentPrompt.designer_context.product_analysis, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </details>
                  )}

                  {/* Reference Images Section */}
                  {currentPrompt.reference_images && currentPrompt.reference_images.length > 0 && (
                    <div className="p-3 bg-green-50 rounded border border-green-200">
                      <p className="text-sm font-medium text-green-800 mb-2">
                        🖼️ Reference Images Used ({currentPrompt.reference_images.length}):
                      </p>
                      <div className="flex flex-wrap gap-3">
                        {currentPrompt.reference_images.map((ref, idx) => {
                          const isStyleRef = ref.type === 'style_reference';
                          return (
                            <div
                              key={idx}
                              className={`flex flex-col items-center ${isStyleRef ? 'p-2 bg-blue-100 rounded-lg' : ''}`}
                            >
                              <img
                                src={`/api/images/file?path=${encodeURIComponent(ref.path)}`}
                                alt={ref.type}
                                className={`object-cover rounded border ${
                                  isStyleRef
                                    ? 'w-24 h-24 border-blue-500 border-2'
                                    : 'w-16 h-16 border-green-300'
                                }`}
                                onError={(e) => {
                                  // Fallback for images that can't load
                                  (e.target as HTMLImageElement).style.display = 'none';
                                }}
                              />
                              <span className={`text-xs mt-1 capitalize ${
                                isStyleRef ? 'text-blue-700 font-semibold' : 'text-green-700'
                              }`}>
                                {isStyleRef ? '⭐ Style Reference' : ref.type.replace('_', ' ')}
                              </span>
                              {isStyleRef && (
                                <span className="text-[10px] text-blue-600">
                                  (AI follows this style)
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                      <p className="text-xs text-green-600 mt-2">
                        These images were sent to Gemini as visual context
                      </p>
                    </div>
                  )}

                  {/* User Feedback Section (if regeneration) */}
                  {currentPrompt.user_feedback && (
                    <div className="p-3 bg-yellow-50 rounded border border-yellow-200">
                      <p className="text-sm font-medium text-yellow-800 mb-1">
                        🔄 User Regeneration Request:
                      </p>
                      <p className="text-sm text-yellow-700">{currentPrompt.user_feedback}</p>
                    </div>
                  )}

                  {/* AI Interpretation (if available) */}
                  {currentPrompt.change_summary && (
                    <div className="p-3 bg-blue-50 rounded border border-blue-200">
                      <p className="text-sm font-medium text-blue-800 mb-1">
                        🤖 AI Interpretation:
                      </p>
                      <p className="text-sm text-blue-700">{currentPrompt.change_summary}</p>
                    </div>
                  )}

                  {/* Main Prompt Text */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      Full Prompt Sent to Gemini:
                    </p>
                    <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded border border-gray-200 font-mono text-gray-800 max-h-96 overflow-y-auto">
                      {currentPrompt.prompt_text}
                    </pre>
                  </div>
                </div>
              ) : null}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t bg-gray-50">
              <button
                onClick={() => {
                  setShowPromptModal(null);
                  setCurrentPrompt(null);
                  setPromptError(null);
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
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
