import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Skeleton } from './ui/skeleton';
import { apiClient } from '../api/client';
import type { ProjectDetailResponse, ProjectImageDetail, GenerationStatus } from '../api/types';
import { Spinner } from '@/components/ui/spinner';

interface ProjectDetailModalProps {
  isOpen: boolean;
  sessionId: string | null;
  onClose: () => void;
  onDelete: () => void;
}

const imageTypeLabels: Record<string, string> = {
  main: 'Main',
  infographic_1: 'Infographic 1',
  infographic_2: 'Infographic 2',
  lifestyle: 'Lifestyle',
  comparison: 'Comparison',
};

const statusConfig: Record<GenerationStatus, { label: string; className: string }> = {
  complete: { label: 'Complete', className: 'bg-green-500/20 text-green-400 border-green-500/30' },
  partial: { label: 'Partial', className: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  processing: { label: 'Processing', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  pending: { label: 'Pending', className: 'bg-slate-500/20 text-slate-400 border-slate-500/30' },
  failed: { label: 'Failed', className: 'bg-red-500/20 text-red-400 border-red-500/30' },
};

export const ProjectDetailModal: React.FC<ProjectDetailModalProps> = ({
  isOpen,
  sessionId,
  onClose,
  onDelete,
}) => {
  const [project, setProject] = useState<ProjectDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<ProjectImageDetail | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (isOpen && sessionId) {
      loadProject();
    } else {
      setProject(null);
      setSelectedImage(null);
      setError(null);
    }
  }, [isOpen, sessionId]);

  const loadProject = async () => {
    if (!sessionId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await apiClient.getProjectDetail(sessionId);
      setProject(data);
      // Auto-select first complete image
      const firstComplete = data.images.find(img => img.status === 'complete');
      if (firstComplete) {
        setSelectedImage(firstComplete);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load project');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadImage = async (image: ProjectImageDetail) => {
    if (!image.image_url) return;

    try {
      const response = await fetch(image.image_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project?.product_title || 'image'}-${image.image_type}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handleDownloadAll = async () => {
    if (!project) return;

    setIsDownloading(true);

    const completeImages = project.images.filter(img => img.status === 'complete' && img.image_url);

    for (const image of completeImages) {
      await handleDownloadImage(image);
      // Small delay between downloads
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setIsDownloading(false);
  };

  const status = project ? statusConfig[project.status] : null;
  const completeCount = project?.images.filter(img => img.status === 'complete').length || 0;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 text-white sm:max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between pr-8">
            <div className="flex items-center gap-3">
              <DialogTitle className="text-white text-lg">
                {isLoading ? (
                  <Skeleton className="h-6 w-48 bg-slate-700" />
                ) : (
                  project?.product_title || 'Project Details'
                )}
              </DialogTitle>
              {status && (
                <Badge className={status.className}>
                  {status.label}
                </Badge>
              )}
            </div>
          </div>
        </DialogHeader>

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="space-y-6">
            {/* Selected image skeleton */}
            <Skeleton className="w-full aspect-video bg-slate-700 rounded-lg" />
            {/* Thumbnails skeleton */}
            <div className="flex gap-2">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="w-20 h-20 bg-slate-700 rounded-lg" />
              ))}
            </div>
          </div>
        ) : project && (
          <div className="space-y-6">
            {/* Selected Image Preview */}
            <div className="relative aspect-video bg-slate-900/50 rounded-lg overflow-hidden">
              {selectedImage?.image_url ? (
                <img
                  src={selectedImage.image_url}
                  alt={imageTypeLabels[selectedImage.image_type] || selectedImage.image_type}
                  className="w-full h-full object-contain"
                />
              ) : selectedImage ? (
                <div className="w-full h-full flex flex-col items-center justify-center text-slate-500">
                  {selectedImage.status === 'failed' ? (
                    <>
                      <svg className="w-12 h-12 mb-2 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <p className="text-red-400">Generation failed</p>
                      {selectedImage.error_message && (
                        <p className="text-xs text-slate-500 mt-1">{selectedImage.error_message}</p>
                      )}
                    </>
                  ) : (
                    <>
                      <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p>Image not available</p>
                    </>
                  )}
                </div>
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-500">
                  <p>Select an image to preview</p>
                </div>
              )}

              {/* Image label */}
              {selectedImage && (
                <div className="absolute bottom-3 left-3">
                  <Badge variant="outline" className="bg-slate-900/80 text-white border-slate-600">
                    {imageTypeLabels[selectedImage.image_type] || selectedImage.image_type}
                  </Badge>
                </div>
              )}
            </div>

            {/* Image Thumbnails */}
            <div className="flex gap-2 overflow-x-auto pb-2">
              {project.images.map((image) => {
                const isSelected = selectedImage?.image_type === image.image_type;

                return (
                  <button
                    key={image.image_type}
                    onClick={() => setSelectedImage(image)}
                    className={`relative flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all
                      ${isSelected
                        ? 'border-redd-500 ring-2 ring-redd-500/30'
                        : 'border-slate-600 hover:border-slate-500'
                      }
                    `}
                  >
                    {image.image_url ? (
                      <img
                        src={image.image_url}
                        alt={imageTypeLabels[image.image_type]}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-slate-700 flex items-center justify-center">
                        {image.status === 'failed' ? (
                          <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        ) : image.status === 'processing' ? (
                          <Spinner size="md" className="text-blue-400" />
                        ) : (
                          <svg className="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>
                    )}

                    {/* Status indicator */}
                    <div className={`absolute bottom-1 right-1 w-2 h-2 rounded-full ${
                      image.status === 'complete' ? 'bg-green-500' :
                      image.status === 'failed' ? 'bg-red-500' :
                      image.status === 'processing' ? 'bg-blue-500' :
                      'bg-slate-500'
                    }`} />
                  </button>
                );
              })}
            </div>

            {/* Info Row */}
            <div className="flex items-center justify-between text-sm text-slate-400">
              <div className="flex items-center gap-4">
                {project.brand_name && (
                  <span>Brand: <span className="text-white">{project.brand_name}</span></span>
                )}
                <span>
                  Images: <span className="text-white">{completeCount}/{project.images.length}</span>
                </span>
              </div>
              <span>
                Created: {new Date(project.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </span>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-700">
              <Button
                variant="outline"
                onClick={onDelete}
                className="border-red-500/50 text-red-400 hover:bg-red-500/10 hover:text-red-300"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </Button>

              <div className="flex items-center gap-2">
                {selectedImage?.image_url && (
                  <Button
                    variant="outline"
                    onClick={() => handleDownloadImage(selectedImage)}
                    className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download
                  </Button>
                )}

                {completeCount > 0 && (
                  <Button
                    onClick={handleDownloadAll}
                    disabled={isDownloading}
                    className="bg-redd-500 hover:bg-redd-600 text-white"
                  >
                    {isDownloading ? (
                      <span className="flex items-center gap-2">
                        <Spinner size="sm" className="text-current" />
                        Downloading...
                      </span>
                    ) : (
                      <>
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download All ({completeCount})
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
