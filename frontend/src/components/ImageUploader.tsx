import React, { useCallback, useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { UploadResponse } from '../api/types';
import { Spinner } from '@/components/ui/spinner';

// Cached upload for quick reuse
interface CachedUpload {
  upload_id: string;
  file_path: string;
  filename: string;
  preview_url: string;
  timestamp: number;
}

const CACHE_KEY = 'listing_genie_recent_uploads';
const MAX_CACHED = 6;
const MAX_IMAGES = 5; // Maximum number of product images

// Cache helper functions
const getCachedUploads = (): CachedUpload[] => {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    return cached ? JSON.parse(cached) : [];
  } catch {
    return [];
  }
};

const saveCachedUpload = (upload: UploadResponse, previewDataUrl: string) => {
  try {
    const cached = getCachedUploads();
    const newEntry: CachedUpload = {
      upload_id: upload.upload_id,
      file_path: upload.file_path,
      filename: upload.filename,
      preview_url: previewDataUrl,
      timestamp: Date.now(),
    };
    // Remove duplicates and add new one at the front
    const filtered = cached.filter(c => c.upload_id !== upload.upload_id);
    const updated = [newEntry, ...filtered].slice(0, MAX_CACHED);

    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(updated));
    } catch (quotaError) {
      // localStorage quota exceeded - clear cache and try again with just this item
      console.warn('localStorage quota exceeded, clearing cache');
      localStorage.removeItem(CACHE_KEY);
      try {
        localStorage.setItem(CACHE_KEY, JSON.stringify([newEntry]));
      } catch {
        // Still failing - just skip caching
        console.warn('Unable to cache upload, skipping');
      }
    }
  } catch (error) {
    // Non-critical - just skip caching
    console.warn('Failed to cache upload:', error);
  }
};

const removeCachedUpload = (uploadId: string) => {
  const cached = getCachedUploads();
  const updated = cached.filter(c => c.upload_id !== uploadId);
  localStorage.setItem(CACHE_KEY, JSON.stringify(updated));
};

// Extended upload with preview
export interface UploadWithPreview extends UploadResponse {
  preview_url: string;
}

interface ImageUploaderProps {
  onUploadsChange: (uploads: UploadWithPreview[]) => void;
  disabled?: boolean;
  maxImages?: number;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  onUploadsChange,
  disabled = false,
  maxImages = MAX_IMAGES,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploads, setUploads] = useState<UploadWithPreview[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cachedUploads, setCachedUploads] = useState<CachedUpload[]>([]);

  // Load cached uploads on mount
  useEffect(() => {
    setCachedUploads(getCachedUploads());
  }, []);

  // Notify parent when uploads change
  useEffect(() => {
    onUploadsChange(uploads);
  }, [uploads, onUploadsChange]);

  const handleFiles = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files);

    // Check if adding these would exceed the limit
    if (uploads.length + fileArray.length > maxImages) {
      setError(`Maximum ${maxImages} images allowed. You can add ${maxImages - uploads.length} more.`);
      return;
    }

    setError(null);
    setIsUploading(true);

    const newUploads: UploadWithPreview[] = [];

    for (const file of fileArray) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please upload image files only (PNG, JPG)');
        continue;
      }

      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError('Some files are too large. Maximum size is 10MB per image');
        continue;
      }

      try {
        // Create preview data URL first (needed for cache)
        const previewDataUrl = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onload = (e) => {
            resolve(e.target?.result as string);
          };
          reader.readAsDataURL(file);
        });

        const uploadResponse = await apiClient.uploadImage(file);

        // Save to cache for quick reuse
        saveCachedUpload(uploadResponse, previewDataUrl);

        newUploads.push({
          ...uploadResponse,
          preview_url: previewDataUrl,
        });
      } catch (err) {
        console.error('Upload failed:', err);
        setError('Failed to upload one or more images. Please try again.');
      }
    }

    if (newUploads.length > 0) {
      setUploads(prev => [...prev, ...newUploads]);
      setCachedUploads(getCachedUploads());
    }

    setIsUploading(false);
  }, [uploads.length, maxImages]);

  // Handle selecting a cached upload
  const handleSelectCached = useCallback((cached: CachedUpload) => {
    if (uploads.length >= maxImages) {
      setError(`Maximum ${maxImages} images allowed`);
      return;
    }

    // Check if already added
    if (uploads.some(u => u.upload_id === cached.upload_id)) {
      setError('This image is already added');
      return;
    }

    const uploadWithPreview: UploadWithPreview = {
      upload_id: cached.upload_id,
      file_path: cached.file_path,
      filename: cached.filename,
      size: 0,
      preview_url: cached.preview_url,
    };

    setUploads(prev => [...prev, uploadWithPreview]);
    setError(null);
  }, [uploads, maxImages]);

  // Handle removing an upload
  const handleRemoveUpload = useCallback((uploadId: string) => {
    setUploads(prev => prev.filter(u => u.upload_id !== uploadId));
    setError(null);
  }, []);

  // Handle removing a cached upload
  const handleRemoveCached = useCallback((e: React.MouseEvent, uploadId: string) => {
    e.stopPropagation();
    removeCachedUpload(uploadId);
    setCachedUploads(getCachedUploads());
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
    // Reset input so same file can be selected again
    e.target.value = '';
  }, [handleFiles]);

  const clearAll = useCallback(() => {
    setUploads([]);
    setError(null);
  }, []);

  const canAddMore = uploads.length < maxImages;

  return (
    <div className="w-full">
      {/* Uploaded Images Grid */}
      {uploads.length > 0 && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-white">
              Product Images ({uploads.length}/{maxImages})
            </span>
            <button
              onClick={clearAll}
              disabled={disabled}
              className="text-xs text-red-400 hover:text-red-300 disabled:opacity-50 transition-colors"
            >
              Clear All
            </button>
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-5 gap-3">
            {uploads.map((upload, index) => (
              <div
                key={upload.upload_id}
                className="relative group rounded-lg overflow-hidden border-2 border-slate-600 bg-slate-700/50"
              >
                <img
                  src={upload.preview_url}
                  alt={`Product ${index + 1}`}
                  className="w-full aspect-square object-contain"
                />
                {/* Primary badge for first image */}
                {index === 0 && (
                  <div className="absolute top-1 left-1 bg-redd-500 text-white text-[10px] px-1.5 py-0.5 rounded">
                    Primary
                  </div>
                )}
                {/* Remove button */}
                <button
                  onClick={() => handleRemoveUpload(upload.upload_id)}
                  disabled={disabled}
                  className="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1
                             opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500
                             disabled:opacity-50"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>

          {/* Prominent Add More Section */}
          {canAddMore && (
            <label
              className={`
                mt-4 flex items-center justify-center gap-2 p-4 rounded-lg border-2 border-dashed
                border-redd-500/30 hover:border-redd-500/50 bg-redd-500/10 hover:bg-redd-500/20
                cursor-pointer transition-colors
                ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                multiple
                onChange={handleFileInput}
                disabled={disabled || isUploading}
                className="hidden"
              />
              <svg className="w-5 h-5 text-redd-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="text-sm font-medium text-redd-400">
                Add More Product Photos ({maxImages - uploads.length} remaining)
              </span>
            </label>
          )}

          <p className="text-xs text-slate-400 mt-3">
            <strong className="text-slate-300">Tip:</strong> Upload multiple angles of your product! For example: front view, back view, close-up of details, product in use. The AI uses all images to better understand your product.
          </p>
        </div>
      )}

      {/* Upload Zone - only show when no uploads */}
      {uploads.length === 0 && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`
            relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
            transition-colors duration-200 bg-slate-800/30
            ${isDragging
              ? 'border-redd-500 bg-redd-500/10'
              : 'border-slate-600 hover:border-slate-500'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input
            type="file"
            accept="image/png,image/jpeg,image/jpg"
            multiple
            onChange={handleFileInput}
            disabled={disabled || isUploading}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="flex flex-col items-center">
            {isUploading ? (
              <Spinner size="xl" className="text-redd-500 mb-4" />
            ) : (
              <svg className="w-12 h-12 text-slate-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            )}
            <p className="text-slate-400">
              {isUploading ? 'Uploading...' : (
                <>Drag and drop or <span className="text-redd-400 hover:text-redd-300">browse files</span></>
              )}
            </p>
            <p className="text-xs text-slate-500 mt-2">
              PNG, JPG up to {maxImages} images
            </p>
          </div>
        </div>
      )}

      {/* Uploading overlay */}
      {isUploading && uploads.length > 0 && (
        <div className="mt-2 flex items-center text-sm text-slate-300">
          <Spinner size="sm" className="text-redd-500 mr-2" />
          Uploading...
        </div>
      )}

      {error && (
        <div className="mt-2 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Recent Uploads - Quick Reuse */}
      {cachedUploads.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-white mb-3">
            Recent Uploads (click to add)
          </h3>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {cachedUploads.map((cached) => {
              const isAlreadyAdded = uploads.some(u => u.upload_id === cached.upload_id);
              return (
                <div
                  key={cached.upload_id}
                  onClick={() => !disabled && !isAlreadyAdded && handleSelectCached(cached)}
                  className={`
                    relative group rounded-lg overflow-hidden border-2 transition-all
                    ${isAlreadyAdded
                      ? 'border-green-500 opacity-50 cursor-not-allowed'
                      : 'border-slate-600 hover:border-redd-500/50 cursor-pointer'}
                    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  <img
                    src={cached.preview_url}
                    alt={cached.filename}
                    className="w-full aspect-square object-cover"
                  />
                  {isAlreadyAdded && (
                    <div className="absolute inset-0 bg-green-500/20 flex items-center justify-center">
                      <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  )}
                  {/* Remove button */}
                  {!isAlreadyAdded && (
                    <button
                      onClick={(e) => handleRemoveCached(e, cached.upload_id)}
                      className="absolute top-1 right-1 bg-red-600 text-white rounded-full p-0.5
                                 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500"
                      title="Remove from recent"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                  {/* Filename tooltip */}
                  <div className="absolute bottom-0 left-0 right-0 bg-black/80 text-white text-[10px]
                                  px-1 py-0.5 truncate opacity-0 group-hover:opacity-100 transition-opacity">
                    {cached.filename}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

// Legacy single-upload wrapper for backward compatibility
interface SingleImageUploaderProps {
  onUploadComplete: (upload: UploadResponse) => void;
  disabled?: boolean;
}

export const SingleImageUploader: React.FC<SingleImageUploaderProps> = ({
  onUploadComplete,
  disabled = false,
}) => {
  const handleUploadsChange = useCallback((uploads: UploadWithPreview[]) => {
    if (uploads.length > 0) {
      onUploadComplete(uploads[0]);
    }
  }, [onUploadComplete]);

  return (
    <ImageUploader
      onUploadsChange={handleUploadsChange}
      disabled={disabled}
      maxImages={1}
    />
  );
};
