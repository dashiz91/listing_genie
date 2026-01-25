import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { apiClient } from '@/api/client';
import type { SessionImage, DesignFramework, PromptHistory } from '@/api/types';
import { ThumbnailGallery } from './ThumbnailGallery';
import { MainImageViewer } from './MainImageViewer';
import { ProductInfoPanel } from './ProductInfoPanel';
import { PreviewToolbar } from './PreviewToolbar';
import { QuickEditBar } from './QuickEditBar';
import { VersionNavigator } from './VersionNavigator';
import { SaveConfirmModal } from './SaveConfirmModal';
import { CelebrationOverlay } from './CelebrationOverlay';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';

type DeviceMode = 'desktop' | 'mobile';

// Version info for each image
interface ImageVersion {
  version: number;
  url: string;
  timestamp: number;
}

// Track versions per image type
interface ImageVersions {
  [imageType: string]: {
    versions: ImageVersion[];
    currentIndex: number;
  };
}

interface AmazonListingPreviewProps {
  // Product data
  productTitle: string;
  brandName?: string;
  features: (string | undefined)[];
  targetAudience?: string;

  // Images
  sessionId: string;
  images: SessionImage[];

  // Design framework (for copy/colors)
  framework?: DesignFramework;

  // Callbacks (preserve existing functionality)
  onRetry?: () => void;
  onRegenerateSingle?: (imageType: string, note?: string) => void;
  onEditSingle?: (imageType: string, instructions: string) => void;
  onStartOver?: () => void;
}

// Default image type order
const DEFAULT_IMAGE_ORDER = ['main', 'infographic_1', 'infographic_2', 'lifestyle', 'comparison'];

// Image labels
const IMAGE_LABELS: Record<string, string> = {
  main: 'Main Image',
  infographic_1: 'Infographic 1',
  infographic_2: 'Infographic 2',
  lifestyle: 'Lifestyle',
  comparison: 'Comparison',
};

export const AmazonListingPreview: React.FC<AmazonListingPreviewProps> = ({
  productTitle,
  brandName,
  features,
  sessionId,
  images,
  onRegenerateSingle,
  onEditSingle,
  onStartOver,
}) => {
  // Local state
  const [deviceMode, setDeviceMode] = useState<DeviceMode>('desktop');
  const [selectedImageType, setSelectedImageType] = useState<string>('main');
  const [isDownloading, setIsDownloading] = useState(false);
  const [imageCacheKey, setImageCacheKey] = useState<Record<string, number>>({});
  const [customImageOrder, setCustomImageOrder] = useState<string[]>(DEFAULT_IMAGE_ORDER);

  // Version state - track versions per image type
  const [imageVersions, setImageVersions] = useState<ImageVersions>({});

  // Edit panel state
  const [editPanelOpen, setEditPanelOpen] = useState(false);
  const [editingImageType, setEditingImageType] = useState<string | null>(null);
  const [editInstructions, setEditInstructions] = useState('');

  // Save to Projects state
  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);

  // Fullscreen and export state
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const previewContainerRef = useRef<HTMLDivElement>(null);

  // Prompt viewer state (dev mode)
  const [showPromptModal, setShowPromptModal] = useState<string | null>(null);
  const [currentPrompt, setCurrentPrompt] = useState<PromptHistory | null>(null);
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [promptError, setPromptError] = useState<string | null>(null);

  // Navigation
  const navigate = useNavigate();

  // Initialize versions from images
  useEffect(() => {
    const newVersions: ImageVersions = {};
    images.forEach((img) => {
      if (img.status === 'complete' && img.url) {
        // If we don't have this image type in versions yet, initialize it
        if (!imageVersions[img.type]) {
          newVersions[img.type] = {
            versions: [
              {
                version: 1,
                url: img.url,
                timestamp: Date.now(),
              },
            ],
            currentIndex: 0,
          };
        } else {
          // Keep existing version history
          newVersions[img.type] = imageVersions[img.type];
        }
      }
    });

    // Only update if there are changes
    if (Object.keys(newVersions).length > 0) {
      setImageVersions((prev) => ({ ...prev, ...newVersions }));
    }
  }, [images]);

  // Get sorted images based on custom order
  const sortedImages = useMemo(
    () =>
      [...images].sort(
        (a, b) => customImageOrder.indexOf(a.type) - customImageOrder.indexOf(b.type)
      ),
    [images, customImageOrder]
  );

  // Handle reorder from drag-and-drop
  const handleReorder = useCallback((newOrder: string[]) => {
    setCustomImageOrder(newOrder);
  }, []);

  // Get currently selected image
  const selectedImage = useMemo(
    () => sortedImages.find((img) => img.type === selectedImageType) || sortedImages[0],
    [sortedImages, selectedImageType]
  );

  // Check if we have complete images
  const hasCompleteImages = useMemo(
    () => images.some((img) => img.status === 'complete'),
    [images]
  );

  // Get current version info for selected image
  const currentVersionInfo = useMemo(() => {
    const versionData = imageVersions[selectedImageType];
    if (!versionData || versionData.versions.length === 0) {
      return { currentVersion: 1, totalVersions: 1 };
    }
    return {
      currentVersion: versionData.currentIndex + 1,
      totalVersions: versionData.versions.length,
    };
  }, [imageVersions, selectedImageType]);

  // Image URL with cache busting
  const getImageUrl = useCallback(
    (imageType: string) => {
      const baseUrl = apiClient.getImageUrl(sessionId, imageType);
      const cacheKey = imageCacheKey[imageType];
      return cacheKey ? `${baseUrl}?t=${cacheKey}` : baseUrl;
    },
    [sessionId, imageCacheKey]
  );

  // Navigate to previous version
  const handlePreviousVersion = useCallback(() => {
    setImageVersions((prev) => {
      const current = prev[selectedImageType];
      if (!current || current.currentIndex <= 0) return prev;
      return {
        ...prev,
        [selectedImageType]: {
          ...current,
          currentIndex: current.currentIndex - 1,
        },
      };
    });
  }, [selectedImageType]);

  // Navigate to next version
  const handleNextVersion = useCallback(() => {
    setImageVersions((prev) => {
      const current = prev[selectedImageType];
      if (!current || current.currentIndex >= current.versions.length - 1) return prev;
      return {
        ...prev,
        [selectedImageType]: {
          ...current,
          currentIndex: current.currentIndex + 1,
        },
      };
    });
  }, [selectedImageType]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't capture if user is typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        handlePreviousVersion();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        handleNextVersion();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlePreviousVersion, handleNextVersion]);

  // Download a single image
  const downloadImage = useCallback(
    async (imageType: string, label: string) => {
      const url = apiClient.getImageUrl(sessionId, imageType);
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      // Amazon-ready filename format
      a.download = `${productTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${label
        .toLowerCase()
        .replace(/\s+/g, '-')}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    },
    [sessionId, productTitle]
  );

  // Download all images
  const handleDownloadAll = useCallback(async () => {
    setIsDownloading(true);
    try {
      const completeImages = images.filter((img) => img.status === 'complete');
      for (let i = 0; i < completeImages.length; i++) {
        const img = completeImages[i];
        await downloadImage(img.type, `${i + 1}-${IMAGE_LABELS[img.type] || img.type}`);
        // Small delay between downloads
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    } finally {
      setIsDownloading(false);
    }
  }, [images, downloadImage]);

  // Handle edit click
  const handleEditClick = useCallback((imageType: string) => {
    setEditingImageType(imageType);
    setEditInstructions('');
    setEditPanelOpen(true);
  }, []);

  // Handle regenerate click - adds new version
  const handleRegenerateClick = useCallback(
    (imageType: string) => {
      onRegenerateSingle?.(imageType);

      // Add a new version entry (will be updated when image completes)
      setImageVersions((prev) => {
        const current = prev[imageType] || { versions: [], currentIndex: 0 };
        const newVersion: ImageVersion = {
          version: current.versions.length + 1,
          url: '', // Will be populated when generation completes
          timestamp: Date.now(),
        };
        return {
          ...prev,
          [imageType]: {
            versions: [...current.versions, newVersion],
            currentIndex: current.versions.length, // Point to new version
          },
        };
      });

      setImageCacheKey((prev) => ({ ...prev, [imageType]: Date.now() }));
    },
    [onRegenerateSingle]
  );

  // Submit edit
  const handleEditSubmit = useCallback(() => {
    if (editingImageType && editInstructions.trim().length >= 5) {
      onEditSingle?.(editingImageType, editInstructions.trim());

      // Add a new version entry for the edit
      setImageVersions((prev) => {
        const current = prev[editingImageType] || { versions: [], currentIndex: 0 };
        const newVersion: ImageVersion = {
          version: current.versions.length + 1,
          url: '',
          timestamp: Date.now(),
        };
        return {
          ...prev,
          [editingImageType]: {
            versions: [...current.versions, newVersion],
            currentIndex: current.versions.length,
          },
        };
      });

      setImageCacheKey((prev) => ({ ...prev, [editingImageType]: Date.now() }));
      setEditPanelOpen(false);
      setEditingImageType(null);
      setEditInstructions('');
    }
  }, [editingImageType, editInstructions, onEditSingle]);

  // Handle view prompt (dev mode)
  const handleViewPrompt = useCallback(async (imageType: string) => {
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
  }, [sessionId]);

  // Check if selected image is processing
  const isSelectedProcessing = selectedImage?.status === 'processing';

  // Count complete images
  const completeImageCount = useMemo(
    () => images.filter((img) => img.status === 'complete').length,
    [images]
  );

  // Handle save to projects
  const handleSaveToProjects = useCallback(() => {
    setSaveModalOpen(true);
  }, []);

  // Confirm save
  const handleConfirmSave = useCallback(async () => {
    setIsSaving(true);
    try {
      // The session is already stored in backend database
      // Just mark it as "saved" in local state and show celebration
      // In a full implementation, we might call an API to mark it as finalized

      // Simulate a brief delay for UX
      await new Promise((resolve) => setTimeout(resolve, 500));

      setSaveModalOpen(false);
      setIsSaved(true);
      setShowCelebration(true);
    } catch (error) {
      console.error('Failed to save project:', error);
    } finally {
      setIsSaving(false);
    }
  }, []);

  // Handle celebration complete
  const handleCelebrationComplete = useCallback(() => {
    setShowCelebration(false);
  }, []);

  // Navigate to projects page
  const handleViewProjects = useCallback(() => {
    navigate('/app/projects');
  }, [navigate]);

  // Toggle fullscreen mode
  const handleFullscreenToggle = useCallback(() => {
    setIsFullscreen((prev) => !prev);
  }, []);

  // Handle escape key to exit fullscreen
  useEffect(() => {
    const handleEscKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };

    if (isFullscreen) {
      window.addEventListener('keydown', handleEscKey);
      // Prevent body scroll when fullscreen
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      window.removeEventListener('keydown', handleEscKey);
      document.body.style.overflow = '';
    };
  }, [isFullscreen]);

  // Export preview as PNG
  const handleExportImage = useCallback(async () => {
    if (!previewContainerRef.current) return;

    setIsExporting(true);
    try {
      // Use canvas approach for export
      const element = previewContainerRef.current;
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        throw new Error('Could not get canvas context');
      }

      // Set canvas size (higher resolution for better quality)
      const scale = 2;
      const rect = element.getBoundingClientRect();
      canvas.width = rect.width * scale;
      canvas.height = rect.height * scale;

      // Draw white background
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // For now, create a simple composite image by drawing each image
      // In production, you'd use html-to-image or similar library
      const completeImages = images.filter((img) => img.status === 'complete');

      // Calculate grid layout
      const padding = 20 * scale;
      const imageSize = Math.min(
        (canvas.width - padding * 3) / 2,
        (canvas.height - padding * 4) / 3
      );

      let x = padding;
      let y = padding;

      for (let i = 0; i < completeImages.length; i++) {
        const img = completeImages[i];
        const imgUrl = apiClient.getImageUrl(sessionId, img.type);

        try {
          const image = new Image();
          image.crossOrigin = 'anonymous';

          await new Promise<void>((resolve, reject) => {
            image.onload = () => {
              // Draw image maintaining aspect ratio
              const aspectRatio = image.width / image.height;
              let drawWidth = imageSize;
              let drawHeight = imageSize;

              if (aspectRatio > 1) {
                drawHeight = imageSize / aspectRatio;
              } else {
                drawWidth = imageSize * aspectRatio;
              }

              const offsetX = (imageSize - drawWidth) / 2;
              const offsetY = (imageSize - drawHeight) / 2;

              ctx.drawImage(image, x + offsetX, y + offsetY, drawWidth, drawHeight);
              resolve();
            };
            image.onerror = reject;
            image.src = imgUrl;
          });
        } catch (err) {
          console.warn(`Failed to load image ${img.type}:`, err);
        }

        // Move to next position
        x += imageSize + padding;
        if (x + imageSize > canvas.width) {
          x = padding;
          y += imageSize + padding;
        }
      }

      // Add title
      ctx.fillStyle = '#1f2937';
      ctx.font = `bold ${24 * scale}px Inter, sans-serif`;
      ctx.fillText(productTitle, padding, canvas.height - padding);

      // Convert to blob and download
      canvas.toBlob((blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${productTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-amazon-preview.png`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }
      }, 'image/png');
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  }, [images, sessionId, productTitle]);

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <PreviewToolbar
        deviceMode={deviceMode}
        onDeviceModeChange={setDeviceMode}
        onDownloadAll={handleDownloadAll}
        onStartOver={onStartOver || (() => {})}
        onSaveToProjects={handleSaveToProjects}
        onViewProjects={handleViewProjects}
        onFullscreen={handleFullscreenToggle}
        onExportImage={handleExportImage}
        isDownloading={isDownloading}
        isExporting={isExporting}
        isSaved={isSaved}
        isFullscreen={isFullscreen}
        hasCompleteImages={hasCompleteImages}
      />

      {/* Fullscreen Overlay */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 bg-slate-900 flex flex-col">
          {/* Fullscreen header */}
          <div className="flex items-center justify-between p-4 border-b border-slate-700">
            <h2 className="text-white font-medium">Amazon Listing Preview</h2>
            <button
              onClick={handleFullscreenToggle}
              className="p-2 text-slate-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          {/* Fullscreen content */}
          <div className="flex-1 overflow-auto p-8 flex items-center justify-center">
            <div
              ref={previewContainerRef}
              className={cn(
                'rounded-xl overflow-hidden border border-slate-200 shadow-2xl',
                'bg-white max-w-5xl w-full',
                deviceMode === 'mobile' ? 'max-w-sm' : ''
              )}
            >
              {/* Desktop or Mobile layout - same as below */}
              {deviceMode === 'desktop' ? (
                <div className="grid grid-cols-12 gap-0">
                  <div className="col-span-1 p-4 border-r border-slate-200 bg-slate-50">
                    <ThumbnailGallery
                      images={sortedImages}
                      selectedType={selectedImageType}
                      onSelect={setSelectedImageType}
                      getImageUrl={getImageUrl}
                      onReorder={handleReorder}
                    />
                  </div>
                  <div className="col-span-6 p-6 border-r border-slate-200">
                    <MainImageViewer
                      imageUrl={getImageUrl(selectedImage?.type || 'main')}
                      imageLabel={IMAGE_LABELS[selectedImage?.type || 'main'] || 'Image'}
                      imageType={selectedImage?.type || 'main'}
                      isProcessing={isSelectedProcessing}
                    />
                  </div>
                  <div className="col-span-5 p-6 bg-white">
                    <ProductInfoPanel
                      productTitle={productTitle}
                      brandName={brandName}
                      features={features}
                    />
                  </div>
                </div>
              ) : (
                <div className="flex flex-col">
                  <div className="flex items-center justify-between p-3 border-b border-slate-200 bg-slate-50">
                    <span className="text-sm font-medium text-slate-700">amazon</span>
                    <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <div className="p-4">
                    <MainImageViewer
                      imageUrl={getImageUrl(selectedImage?.type || 'main')}
                      imageLabel={IMAGE_LABELS[selectedImage?.type || 'main'] || 'Image'}
                      imageType={selectedImage?.type || 'main'}
                      isProcessing={isSelectedProcessing}
                    />
                  </div>
                  <div className="flex gap-2 px-4 pb-4 overflow-x-auto">
                    {sortedImages.map((image, index) => (
                      <button
                        key={image.type}
                        onClick={() => image.status === 'complete' && setSelectedImageType(image.type)}
                        disabled={image.status !== 'complete'}
                        className={cn(
                          'flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden border-2 transition-all',
                          image.type === selectedImageType ? 'border-redd-500' : 'border-slate-200',
                          image.status !== 'complete' && 'opacity-50'
                        )}
                      >
                        {image.status === 'complete' ? (
                          <img src={getImageUrl(image.type)} alt={`Thumbnail ${index + 1}`} className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full bg-slate-100 flex items-center justify-center">
                            <span className="text-slate-400 text-xs">{index + 1}</span>
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                  <div className="p-4 border-t border-slate-200">
                    <ProductInfoPanel productTitle={productTitle} brandName={brandName} features={features} />
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* Fullscreen hint */}
          <div className="p-2 text-center text-slate-500 text-xs">
            Press ESC to exit fullscreen
          </div>
        </div>
      )}

      {/* Main Preview Container */}
      <div
        ref={!isFullscreen ? previewContainerRef : undefined}
        className={cn(
          'rounded-xl overflow-hidden border border-slate-700',
          'bg-white', // Amazon-style white background
          deviceMode === 'mobile' ? 'max-w-sm mx-auto' : ''
        )}
      >
        {deviceMode === 'desktop' ? (
          // Desktop Layout - Amazon-style grid with responsive breakpoints
          <div className="grid grid-cols-1 md:grid-cols-12 gap-0">
            {/* Thumbnails Column - horizontal on tablet, vertical on desktop */}
            <div className="order-2 md:order-1 md:col-span-1 p-3 md:p-4 border-t md:border-t-0 md:border-r border-slate-200 bg-slate-50">
              <ThumbnailGallery
                images={sortedImages}
                selectedType={selectedImageType}
                onSelect={setSelectedImageType}
                getImageUrl={getImageUrl}
                onReorder={handleReorder}
                className="flex-row md:flex-col overflow-x-auto md:overflow-x-visible"
              />
            </div>

            {/* Main Image Column */}
            <div className="order-1 md:order-2 md:col-span-6 p-4 md:p-6 border-b md:border-b-0 md:border-r border-slate-200">
              <MainImageViewer
                imageUrl={getImageUrl(selectedImage?.type || 'main')}
                imageLabel={IMAGE_LABELS[selectedImage?.type || 'main'] || 'Image'}
                imageType={selectedImage?.type || 'main'}
                isProcessing={isSelectedProcessing}
              />
            </div>

            {/* Product Info Column */}
            <div className="order-3 md:col-span-5 p-4 md:p-6 bg-white">
              <ProductInfoPanel
                productTitle={productTitle}
                brandName={brandName}
                features={features}
              />
            </div>
          </div>
        ) : (
          // Mobile Layout
          <div className="flex flex-col">
            {/* Mobile Header */}
            <div className="flex items-center justify-between p-3 border-b border-slate-200 bg-slate-50">
              <span className="text-sm font-medium text-slate-700">amazon</span>
              <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>

            {/* Main Image */}
            <div className="p-4">
              <MainImageViewer
                imageUrl={getImageUrl(selectedImage?.type || 'main')}
                imageLabel={IMAGE_LABELS[selectedImage?.type || 'main'] || 'Image'}
                imageType={selectedImage?.type || 'main'}
                isProcessing={isSelectedProcessing}
              />
            </div>

            {/* Horizontal Thumbnails */}
            <div className="flex gap-2 px-4 pb-4 overflow-x-auto">
              {sortedImages.map((image, index) => {
                const isSelected = image.type === selectedImageType;
                const isComplete = image.status === 'complete';

                return (
                  <button
                    key={image.type}
                    onClick={() => isComplete && setSelectedImageType(image.type)}
                    disabled={!isComplete}
                    className={cn(
                      'flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden border-2 transition-all',
                      isSelected ? 'border-redd-500' : 'border-slate-200',
                      !isComplete && 'opacity-50'
                    )}
                  >
                    {isComplete ? (
                      <img
                        src={getImageUrl(image.type)}
                        alt={`Thumbnail ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-slate-100 flex items-center justify-center">
                        <span className="text-slate-400 text-xs">{index + 1}</span>
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Product Info */}
            <div className="p-4 border-t border-slate-200">
              <ProductInfoPanel
                productTitle={productTitle}
                brandName={brandName}
                features={features}
              />
            </div>
          </div>
        )}
      </div>

      {/* Version Navigator (below the preview) */}
      {selectedImage?.status === 'complete' && (
        <VersionNavigator
          currentVersion={currentVersionInfo.currentVersion}
          totalVersions={currentVersionInfo.totalVersions}
          onPrevious={handlePreviousVersion}
          onNext={handleNextVersion}
          onEdit={() => handleEditClick(selectedImageType)}
          onRegenerate={() => handleRegenerateClick(selectedImageType)}
          isProcessing={isSelectedProcessing}
        />
      )}

      {/* Quick Edit Bar */}
      <QuickEditBar
        images={sortedImages}
        selectedType={selectedImageType}
        onEdit={handleEditClick}
        onRegenerate={handleRegenerateClick}
        onViewPrompt={handleViewPrompt}
      />

      {/* Edit Panel (Sheet) */}
      <Sheet open={editPanelOpen} onOpenChange={setEditPanelOpen}>
        <SheetContent className="bg-slate-900 border-slate-700">
          <SheetHeader>
            <SheetTitle className="text-white">
              Edit {editingImageType ? IMAGE_LABELS[editingImageType] : 'Image'}
            </SheetTitle>
            <SheetDescription className="text-slate-400">
              Describe what changes you'd like to make. This will create a new version.
            </SheetDescription>
          </SheetHeader>

          <div className="mt-6 space-y-4">
            {/* Preview of image being edited */}
            {editingImageType && (
              <div className="rounded-lg overflow-hidden border border-slate-700">
                <img
                  src={getImageUrl(editingImageType)}
                  alt="Image to edit"
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
                placeholder="e.g., 'Change headline to Premium Quality' or 'Make the background lighter'"
                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-redd-500 focus:border-transparent resize-none"
                rows={4}
              />
              <p className="mt-1 text-xs text-slate-500">
                Minimum 5 characters required
              </p>
            </div>

            {/* Action buttons */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleEditSubmit}
                disabled={editInstructions.trim().length < 5}
                className="flex-1 px-4 py-2 bg-redd-500 text-white font-medium rounded-lg hover:bg-redd-600 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed transition-colors"
              >
                Apply Edit
              </button>
              <button
                onClick={() => setEditPanelOpen(false)}
                className="px-4 py-2 bg-slate-800 text-slate-300 font-medium rounded-lg hover:bg-slate-700 border border-slate-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      {/* Save Confirmation Modal */}
      <SaveConfirmModal
        isOpen={saveModalOpen}
        onClose={() => setSaveModalOpen(false)}
        onConfirm={handleConfirmSave}
        productTitle={productTitle}
        imageCount={completeImageCount}
        isLoading={isSaving}
      />

      {/* Celebration Overlay */}
      <CelebrationOverlay
        isVisible={showCelebration}
        onComplete={handleCelebrationComplete}
        message="Saved!"
        subMessage="Your listing is saved to Projects"
      />

      {/* Prompt Viewer Modal (Dev Mode) */}
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
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-redd-500"></div>
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
                    <details className="p-3 bg-purple-900/20 rounded border border-purple-500/30" open>
                      <summary className="text-sm font-medium text-purple-300 cursor-pointer hover:text-purple-200">
                        🧠 AI Designer Context (click to collapse)
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
                              {currentPrompt.designer_context.framework_summary.colors.map((c, i) => (
                                <div
                                  key={i}
                                  className="w-6 h-6 rounded border border-slate-500"
                                  style={{ backgroundColor: c.hex }}
                                  title={`${c.name} (${c.role}): ${c.hex}`}
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
                          return (
                            <div
                              key={idx}
                              className={`flex flex-col items-center ${isStyleRef ? 'p-2 bg-blue-900/30 rounded-lg' : ''}`}
                            >
                              <img
                                src={`/api/images/file?path=${encodeURIComponent(ref.path)}`}
                                alt={ref.type}
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
                              <span className={`text-xs mt-1 capitalize ${
                                isStyleRef ? 'text-blue-300 font-semibold' : 'text-green-300'
                              }`}>
                                {isStyleRef ? '⭐ Style Reference' : ref.type.replace('_', ' ')}
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
