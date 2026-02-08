import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { cn, normalizeColors } from '@/lib/utils';
import { apiClient } from '@/api/client';
import type { SessionImage, DesignFramework } from '@/api/types';
import { PromptModal } from '@/components/PromptModal';
import { ThumbnailGallery } from './ThumbnailGallery';
import { MainImageViewer } from './MainImageViewer';
import { ProductInfoPanel } from './ProductInfoPanel';
import { PreviewToolbar } from './PreviewToolbar';
import { AmazonHeader } from './AmazonHeader';
import { AmazonBreadcrumbs } from './AmazonBreadcrumbs';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';
import { ImageActionOverlay } from '@/components/shared/ImageActionOverlay';
import { Spinner } from '@/components/ui/spinner';
import FocusImagePicker, { useFocusImages } from '@/components/FocusImagePicker';
import type { ReferenceImage } from '@/api/types';
import type { ListingVersionState } from '@/pages/HomePage';
import type { AplusModule } from '@/components/preview-slots/AplusSection';

type DeviceMode = 'desktop' | 'mobile';

interface AmazonListingPreviewProps {
  // Product data
  productTitle: string;
  brandName?: string;
  features: (string | undefined)[];
  targetAudience?: string;

  // Images
  sessionId?: string;
  images: SessionImage[];

  // Design framework (for copy/colors)
  framework?: DesignFramework;

  // Generation callbacks (for clickable slots)
  onGenerateSingle?: (imageType: string) => void;
  onGenerateAll?: () => void;

  // Callbacks (preserve existing functionality)
  onRetry?: () => void;
  onRegenerateSingle?: (imageType: string, note?: string, referenceImagePaths?: string[]) => void;
  onEditSingle?: (imageType: string, instructions: string, referenceImagePaths?: string[]) => void;
  onCancelGeneration?: (imageType: string) => void;
  availableReferenceImages?: ReferenceImage[];
  onStartOver?: () => void;

  // Version tracking (lifted to HomePage)
  listingVersions?: ListingVersionState;
  onVersionChange?: (imageType: string, index: number) => void;

  // Controlled device mode (unified with A+ viewport)
  deviceMode?: DeviceMode;
  onDeviceModeChange?: (mode: DeviceMode) => void;

  // A+ content to render inside the same card container
  aplusContent?: React.ReactNode;
  aplusModules?: AplusModule[];

  // Re-plan all prompts (listing + A+)
  onReplanAll?: () => void;
  isReplanning?: boolean;
}

// Default image type order
const DEFAULT_IMAGE_ORDER = ['main', 'infographic_1', 'infographic_2', 'lifestyle', 'transformation', 'comparison'];

// Image labels
const IMAGE_LABELS: Record<string, string> = {
  main: 'Main Image',
  infographic_1: 'Infographic 1',
  infographic_2: 'Infographic 2',
  lifestyle: 'Lifestyle',
  transformation: 'Transformation',
  comparison: 'Comparison',
};

export const AmazonListingPreview: React.FC<AmazonListingPreviewProps> = ({
  productTitle,
  brandName,
  features,
  sessionId,
  images,
  framework,
  onGenerateSingle,
  onGenerateAll: _onGenerateAll, // Reserved for "Generate All" button
  onRegenerateSingle,
  onEditSingle,
  onCancelGeneration,
  availableReferenceImages = [],
  onStartOver,
  listingVersions,
  onVersionChange,
  deviceMode: controlledDeviceMode,
  onDeviceModeChange,
  aplusContent,
  aplusModules = [],
  onReplanAll,
  isReplanning = false,
}) => {
  void _onGenerateAll; // Reserved for future "Generate All" button
  // Get accent color from framework
  const frameworkColors = framework ? normalizeColors(framework.colors) : [];
  const accentColor = frameworkColors.find((c) => c.role === 'primary')?.hex || '#C85A35';
  // Local state - supports both controlled and uncontrolled modes
  const [internalDeviceMode, setInternalDeviceMode] = useState<DeviceMode>('desktop');
  const deviceMode = controlledDeviceMode ?? internalDeviceMode;
  const setDeviceMode = onDeviceModeChange ?? setInternalDeviceMode;
  const [selectedImageType, setSelectedImageType] = useState<string>('main');
  const [isDownloading, setIsDownloading] = useState(false);
  const [imageCacheKey, setImageCacheKey] = useState<Record<string, number>>({});
  const [customImageOrder, setCustomImageOrder] = useState<string[]>(DEFAULT_IMAGE_ORDER);

  // Edit panel state
  const [editPanelOpen, setEditPanelOpen] = useState(false);
  const [editingImageType, setEditingImageType] = useState<string | null>(null);
  const [editInstructions, setEditInstructions] = useState('');
  const focusImages = useFocusImages();

  // Regenerate note panel state
  const [regenPanelOpen, setRegenPanelOpen] = useState(false);
  const [regenImageType, setRegenImageType] = useState<string | null>(null);
  const [regenNote, setRegenNote] = useState('');
  const regenFocusImages = useFocusImages();

  // Fullscreen state
  const [isFullscreen, setIsFullscreen] = useState(false);
  const previewContainerRef = useRef<HTMLDivElement>(null);

  // Prompt viewer state (dev mode) — image type string or null
  const [showPromptModal, setShowPromptModal] = useState<string | null>(null);

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
    const versionData = listingVersions?.[selectedImageType];
    if (!versionData || versionData.versions.length === 0) {
      return { currentVersion: 1, totalVersions: 1 };
    }
    return {
      currentVersion: versionData.activeIndex + 1,
      totalVersions: versionData.versions.length,
    };
  }, [listingVersions, selectedImageType]);

  // Image URL — use versioned URL if available, otherwise backend proxy
  const getImageUrl = useCallback(
    (imageType: string) => {
      const versionData = listingVersions?.[imageType];
      if (versionData && versionData.versions.length > 0) {
        return versionData.versions[versionData.activeIndex].imageUrl;
      }
      // Fallback to backend proxy
      if (!sessionId) return '';
      const baseUrl = apiClient.getImageUrl(sessionId, imageType);
      const cacheKey = imageCacheKey[imageType];
      return cacheKey ? apiClient.withCacheBust(baseUrl, cacheKey) : baseUrl;
    },
    [sessionId, imageCacheKey, listingVersions]
  );


  // Navigate to previous version
  const handlePreviousVersion = useCallback(() => {
    const vd = listingVersions?.[selectedImageType];
    if (!vd || vd.activeIndex <= 0) return;
    onVersionChange?.(selectedImageType, vd.activeIndex - 1);
  }, [selectedImageType, listingVersions, onVersionChange]);

  // Navigate to next version
  const handleNextVersion = useCallback(() => {
    const vd = listingVersions?.[selectedImageType];
    if (!vd || vd.activeIndex >= vd.versions.length - 1) return;
    onVersionChange?.(selectedImageType, vd.activeIndex + 1);
  }, [selectedImageType, listingVersions, onVersionChange]);

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

  const slugify = useCallback((text: string) => {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }, []);

  const downloadFromUrl = useCallback(async (url: string, fileName: string) => {
    const response = await fetch(url);
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);
  }, []);

  // Download a single listing image.
  const downloadImage = useCallback(
    async (imageType: string, label: string) => {
      if (!sessionId) return;
      const url = apiClient.getImageUrl(sessionId, imageType);
      const fileName = `${slugify(productTitle)}-${slugify(label)}.png`;
      await downloadFromUrl(url, fileName);
    },
    [sessionId, productTitle, slugify, downloadFromUrl]
  );

  // Download all listing + A+ images.
  const handleDownloadAll = useCallback(async () => {
    setIsDownloading(true);
    try {
      const completeImages = images
        .filter((img) => img.status === 'complete')
        .sort((a, b) => DEFAULT_IMAGE_ORDER.indexOf(a.type) - DEFAULT_IMAGE_ORDER.indexOf(b.type));

      for (let i = 0; i < completeImages.length; i++) {
        const img = completeImages[i];
        await downloadImage(img.type, `${i + 1}-${IMAGE_LABELS[img.type] || img.type}`);
        await new Promise((resolve) => setTimeout(resolve, 250));
      }

      for (let i = 0; i < aplusModules.length; i++) {
        const module = aplusModules[i];
        const desktop = module.versions[module.activeVersionIndex];
        if (desktop?.imageUrl) {
          const fileName = `${slugify(productTitle)}-aplus-module-${i + 1}-desktop.png`;
          await downloadFromUrl(desktop.imageUrl, fileName);
          await new Promise((resolve) => setTimeout(resolve, 250));
        }

        const mobile = module.mobileVersions[module.mobileActiveVersionIndex];
        if (mobile?.imageUrl) {
          const fileName = `${slugify(productTitle)}-aplus-module-${i + 1}-mobile.png`;
          await downloadFromUrl(mobile.imageUrl, fileName);
          await new Promise((resolve) => setTimeout(resolve, 250));
        }
      }
    } finally {
      setIsDownloading(false);
    }
  }, [images, downloadImage, aplusModules, productTitle, slugify, downloadFromUrl]);

  // Handle edit click — default all reference images to selected
  const handleEditClick = useCallback((imageType: string) => {
    setEditingImageType(imageType);
    setEditInstructions('');
    focusImages.selectAll(availableReferenceImages.map(i => i.path));
    setEditPanelOpen(true);
  }, [focusImages, availableReferenceImages]);

  // Handle regenerate click — open note panel, default all refs selected
  const handleRegenerateClick = useCallback(
    (imageType: string) => {
      setRegenImageType(imageType);
      setRegenNote('');
      regenFocusImages.selectAll(availableReferenceImages.map(i => i.path));
      setRegenPanelOpen(true);
    },
    [availableReferenceImages]
  );

  // Submit regenerate with optional note
  const handleRegenSubmit = useCallback(async () => {
    if (regenImageType) {
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
      onRegenerateSingle?.(regenImageType, regenNote.trim() || undefined, refs);
      setImageCacheKey((prev) => ({ ...prev, [regenImageType]: Date.now() }));
      setRegenPanelOpen(false);
      setRegenImageType(null);
      setRegenNote('');
    }
  }, [regenImageType, regenNote, onRegenerateSingle, regenFocusImages]);

  // Submit edit — version management is now in HomePage
  const handleEditSubmit = useCallback(async () => {
    if (editingImageType && editInstructions.trim().length >= 5) {
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
      onEditSingle?.(editingImageType, editInstructions.trim(), refs);
      setImageCacheKey((prev) => ({ ...prev, [editingImageType]: Date.now() }));
      setEditPanelOpen(false);
      setEditingImageType(null);
      setEditInstructions('');
      focusImages.reset();
    }
  }, [editingImageType, editInstructions, onEditSingle, focusImages]);

  // Handle view prompt (dev mode)
  const handleViewPrompt = useCallback((imageType: string) => {
    if (sessionId) setShowPromptModal(imageType);
  }, [sessionId]);

  // Check if selected image is processing or pending
  const isSelectedProcessing = selectedImage?.status === 'processing';
  const isSelectedPending = !selectedImage || selectedImage?.status === 'pending' || selectedImage?.status === 'failed';

  // Handle generate single image
  const handleGenerateSingle = useCallback(
    (imageType: string) => {
      onGenerateSingle?.(imageType);
    },
    [onGenerateSingle]
  );

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

  // Overlay for the main image viewer (shared across all layout modes)
  const imageOverlay = selectedImage?.status === 'complete' ? (
    <ImageActionOverlay
      versionInfo={{ current: currentVersionInfo.currentVersion, total: currentVersionInfo.totalVersions }}
      onPreviousVersion={handlePreviousVersion}
      onNextVersion={handleNextVersion}
      onRegenerate={() => handleRegenerateClick(selectedImageType)}
      onEdit={() => handleEditClick(selectedImageType)}
      onDownload={() => downloadImage(selectedImageType, IMAGE_LABELS[selectedImageType] || selectedImageType)}
      onViewPrompt={() => handleViewPrompt(selectedImageType)}
      isProcessing={isSelectedProcessing}
    />
  ) : undefined;

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <PreviewToolbar
        deviceMode={deviceMode}
        onDeviceModeChange={setDeviceMode}
        onDownloadAll={handleDownloadAll}
        onStartOver={onStartOver || (() => {})}
        onFullscreen={handleFullscreenToggle}
        isDownloading={isDownloading}
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
          <div className="flex-1 overflow-auto p-4 md:p-8 flex items-center justify-center">
            <div
              ref={previewContainerRef}
              className={cn(
                'rounded-xl overflow-hidden border border-slate-200 shadow-2xl',
                'bg-white max-w-6xl w-full',
                deviceMode === 'mobile' ? 'max-w-sm' : ''
              )}
            >
              {/* Desktop or Mobile layout with Amazon header */}
              {deviceMode === 'desktop' ? (
                <div className="flex flex-col">
                  <AmazonHeader />
                  <AmazonBreadcrumbs productTitle={productTitle} />
                  <div className="grid grid-cols-12 gap-0 border-t border-slate-200">
                    <div className="col-span-1 p-4 border-r border-slate-200 bg-white">
                      <ThumbnailGallery
                        images={sortedImages}
                        selectedType={selectedImageType}
                        onSelect={setSelectedImageType}
                        getImageUrl={getImageUrl}
                        onReorder={handleReorder}
                      />
                    </div>
                    <div className="col-span-6 p-6 border-r border-slate-200 bg-white">
                      <MainImageViewer
                        imageUrl={getImageUrl(selectedImage?.type || 'main')}
                        imageLabel={IMAGE_LABELS[selectedImage?.type || 'main'] || 'Image'}
                        imageType={selectedImage?.type || 'main'}
                        isProcessing={isSelectedProcessing}
                        isPending={isSelectedPending}
                        accentColor={accentColor}
                        onGenerate={isSelectedPending && onGenerateSingle ? () => handleGenerateSingle(selectedImage?.type || 'main') : undefined}
                        onCancel={isSelectedProcessing && onCancelGeneration ? () => onCancelGeneration(selectedImageType) : undefined}
                        onRegenerate={isSelectedProcessing ? () => handleRegenerateClick(selectedImageType) : undefined}
                        overlay={imageOverlay}
                      />
                    </div>
                    <div className="col-span-5 p-6 bg-white overflow-y-auto max-h-[600px]">
                      <ProductInfoPanel
                        productTitle={productTitle}
                        brandName={brandName}
                        features={features}
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col">
                  <div className="bg-[#131921] px-3 py-2 flex items-center gap-3">
                    <span className="text-white text-lg font-bold">amazon</span>
                    <div className="flex-1 flex items-center bg-white rounded-md px-2 py-1.5">
                      <svg className="w-4 h-4 text-[#565959]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <input type="text" placeholder="Search" className="flex-1 ml-2 text-sm focus:outline-none" />
                    </div>
                  </div>
                  <div className="p-4 bg-white">
                    <MainImageViewer
                      imageUrl={getImageUrl(selectedImage?.type || 'main')}
                      imageLabel={IMAGE_LABELS[selectedImage?.type || 'main'] || 'Image'}
                      imageType={selectedImage?.type || 'main'}
                      isProcessing={isSelectedProcessing}
                      isPending={isSelectedPending}
                      accentColor={accentColor}
                      onGenerate={isSelectedPending && onGenerateSingle ? () => handleGenerateSingle(selectedImage?.type || 'main') : undefined}
                      onCancel={isSelectedProcessing && onCancelGeneration ? () => onCancelGeneration(selectedImageType) : undefined}
                      onRegenerate={isSelectedProcessing ? () => handleRegenerateClick(selectedImageType) : undefined}
                    />
                  </div>
                  <div className="flex gap-2 px-4 pb-4 overflow-x-auto bg-white">
                    {sortedImages.map((image, index) => (
                      <button
                        key={image.type}
                        onClick={() => setSelectedImageType(image.type)}
                        className={cn(
                          'flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden border-2 transition-all',
                          image.type === selectedImageType ? 'border-[#FF9900]' : 'border-slate-200',
                          image.status !== 'complete' && 'opacity-50'
                        )}
                      >
                        {image.status === 'complete' ? (
                          <img src={getImageUrl(image.type)} alt={`Thumbnail ${index + 1}`} className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />
                        ) : (
                          <div className="w-full h-full bg-slate-100 flex items-center justify-center">
                            <span className="text-slate-400 text-xs">{index + 1}</span>
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                  <div className="p-4 border-t border-slate-200 bg-white">
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
          'rounded-xl overflow-hidden border border-slate-300 shadow-lg',
          'bg-white', // Amazon-style white background
          deviceMode === 'mobile' ? 'max-w-sm mx-auto' : ''
        )}
      >
        {deviceMode === 'desktop' ? (
          // Desktop Layout - Amazon-style with header
          <div className="flex flex-col">
            {/* Amazon Header */}
            <AmazonHeader />

            {/* Breadcrumbs */}
            <AmazonBreadcrumbs
              category="Home & Kitchen"
              subcategory="Planters"
              productTitle={productTitle}
            />

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-0 border-t border-slate-200">
              {/* Thumbnails Column */}
              <div className="order-2 md:order-1 md:col-span-1 p-3 md:p-4 border-t md:border-t-0 md:border-r border-slate-200 bg-white">
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
              <div className="order-1 md:order-2 md:col-span-6 p-4 md:p-6 border-b md:border-b-0 md:border-r border-slate-200 bg-white">
                <MainImageViewer
                  imageUrl={getImageUrl(selectedImage?.type || 'main')}
                  imageLabel={IMAGE_LABELS[selectedImage?.type || 'main'] || 'Image'}
                  imageType={selectedImage?.type || 'main'}
                  isProcessing={isSelectedProcessing}
                  isPending={isSelectedPending}
                  accentColor={accentColor}
                  onGenerate={isSelectedPending && onGenerateSingle ? () => handleGenerateSingle(selectedImage?.type || 'main') : undefined}
                  onCancel={isSelectedProcessing && onCancelGeneration ? () => onCancelGeneration(selectedImageType) : undefined}
                  versionInfo={selectedImage?.status === 'complete' ? { current: currentVersionInfo.currentVersion, total: currentVersionInfo.totalVersions } : undefined}
                  onPreviousVersion={handlePreviousVersion}
                  onNextVersion={handleNextVersion}
                  onRegenerate={selectedImage?.status === 'complete' || isSelectedProcessing ? () => handleRegenerateClick(selectedImageType) : undefined}
                  onEdit={selectedImage?.status === 'complete' ? () => handleEditClick(selectedImageType) : undefined}
                  onDownload={selectedImage?.status === 'complete' ? () => downloadImage(selectedImageType, IMAGE_LABELS[selectedImageType] || selectedImageType) : undefined}
                  onViewPrompt={selectedImage?.status === 'complete' ? () => handleViewPrompt(selectedImageType) : undefined}
                />
              </div>

              {/* Product Info Column */}
              <div className="order-3 md:col-span-5 p-4 md:p-6 bg-white overflow-y-auto max-h-[600px]">
                <ProductInfoPanel
                  productTitle={productTitle}
                  brandName={brandName}
                  features={features}
                />
              </div>
            </div>

            {/* Re-plan All Prompts Button - between listings and A+ */}
            {aplusContent && onReplanAll && (
              <div className="px-4 py-3 border-t border-slate-200 bg-slate-50">
                <button
                  onClick={onReplanAll}
                  disabled={isReplanning}
                  className="w-full py-2.5 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isReplanning ? (
                    <>
                      <Spinner size="sm" className="text-current" />
                      Re-planning...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Re-plan Art Direction
                    </>
                  )}
                </button>
              </div>
            )}

            {/* A+ Content - flows continuously inside the same card */}
            {aplusContent}
          </div>
        ) : (
          // Mobile Layout - Amazon App Style
          <div className="flex flex-col">
            {/* Mobile Header */}
            <div className="bg-[#131921] px-3 py-2 flex items-center gap-3">
              <span className="text-white text-lg font-bold">amazon</span>
              <div className="flex-1 flex items-center bg-white rounded-md px-2 py-1.5">
                <svg className="w-4 h-4 text-[#565959]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="Search Amazon"
                  className="flex-1 ml-2 text-sm text-slate-800 focus:outline-none"
                />
              </div>
            </div>

            {/* Main Image */}
            <div className="p-4 bg-white">
              <MainImageViewer
                imageUrl={getImageUrl(selectedImage?.type || 'main')}
                imageLabel={IMAGE_LABELS[selectedImage?.type || 'main'] || 'Image'}
                imageType={selectedImage?.type || 'main'}
                isProcessing={isSelectedProcessing}
                isPending={isSelectedPending}
                accentColor={accentColor}
                onGenerate={isSelectedPending && onGenerateSingle ? () => handleGenerateSingle(selectedImage?.type || 'main') : undefined}
                onCancel={isSelectedProcessing && onCancelGeneration ? () => onCancelGeneration(selectedImageType) : undefined}
                versionInfo={selectedImage?.status === 'complete' ? { current: currentVersionInfo.currentVersion, total: currentVersionInfo.totalVersions } : undefined}
                onPreviousVersion={handlePreviousVersion}
                onNextVersion={handleNextVersion}
                onRegenerate={selectedImage?.status === 'complete' || isSelectedProcessing ? () => handleRegenerateClick(selectedImageType) : undefined}
                onEdit={selectedImage?.status === 'complete' ? () => handleEditClick(selectedImageType) : undefined}
                onDownload={selectedImage?.status === 'complete' ? () => downloadImage(selectedImageType, IMAGE_LABELS[selectedImageType] || selectedImageType) : undefined}
                onViewPrompt={selectedImage?.status === 'complete' ? () => handleViewPrompt(selectedImageType) : undefined}
              />
            </div>

            {/* Horizontal Thumbnails */}
            <div className="flex gap-2 px-4 pb-4 overflow-x-auto bg-white">
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
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
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

            {/* Re-plan All Prompts Button - between listings and A+ (Mobile) */}
            {aplusContent && onReplanAll && (
              <div className="px-4 py-3 border-t border-slate-200 bg-slate-50">
                <button
                  onClick={onReplanAll}
                  disabled={isReplanning}
                  className="w-full py-2.5 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isReplanning ? (
                    <>
                      <Spinner size="sm" className="text-current" />
                      Re-planning...
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Re-plan Art Direction
                    </>
                  )}
                </button>
              </div>
            )}

            {/* A+ Content - flows continuously inside the same card */}
            {aplusContent}
          </div>
        )}
      </div>

      {/* Actions are now rendered directly on the main image via MainImageViewer */}

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

            {/* Focus images — select which references to send with edit */}
            {availableReferenceImages.length > 0 && (
              <FocusImagePicker
                availableImages={availableReferenceImages}
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

      {/* Regenerate Note Panel */}
      <Sheet open={regenPanelOpen} onOpenChange={setRegenPanelOpen}>
        <SheetContent className="bg-slate-900 border-slate-700">
          <SheetHeader>
            <SheetTitle className="text-white">
              Regenerate {regenImageType ? IMAGE_LABELS[regenImageType] : 'Image'}
            </SheetTitle>
            <SheetDescription className="text-slate-400">
              Optionally describe what you'd like different. Leave empty to regenerate freely.
            </SheetDescription>
          </SheetHeader>

          <div className="mt-6 space-y-4">
            {regenImageType && (
              <div className="rounded-lg overflow-hidden border border-slate-700">
                <img
                  src={getImageUrl(regenImageType)}
                  alt="Image to regenerate"
                  className="w-full h-48 object-contain bg-white"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Feedback / Note <span className="text-slate-500">(optional)</span>
              </label>
              <textarea
                value={regenNote}
                onChange={(e) => setRegenNote(e.target.value)}
                placeholder="e.g., 'Try a more minimal style' or 'Make it more vibrant and colorful'"
                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-redd-500 focus:border-transparent resize-none"
                rows={4}
              />
            </div>

            {/* Focus Images for regen */}
            {availableReferenceImages && availableReferenceImages.length > 0 && (
              <FocusImagePicker
                availableImages={availableReferenceImages}
                selectedPaths={regenFocusImages.selectedPaths}
                onToggle={regenFocusImages.toggle}
                extraFile={regenFocusImages.extraFile}
                onExtraFile={regenFocusImages.addExtra}
                onRemoveExtra={regenFocusImages.removeExtra}
                variant="dark"
              />
            )}

            <div className="flex gap-3 pt-4">
              <button
                onClick={handleRegenSubmit}
                className="flex-1 px-4 py-2 bg-redd-500 text-white font-medium rounded-lg hover:bg-redd-600 transition-colors"
              >
                Regenerate
              </button>
              <button
                onClick={() => setRegenPanelOpen(false)}
                className="px-4 py-2 bg-slate-800 text-slate-300 font-medium rounded-lg hover:bg-slate-700 border border-slate-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </SheetContent>
      </Sheet>

      {/* Prompt Viewer Modal (Dev Mode) */}
      {showPromptModal && sessionId && (
        <PromptModal
          sessionId={sessionId}
          imageType={showPromptModal}
          version={listingVersions?.[showPromptModal] ? listingVersions[showPromptModal].activeIndex + 1 : undefined}
          title={`Prompt for ${showPromptModal.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}`}
          onClose={() => setShowPromptModal(null)}
        />
      )}
    </div>
  );
};
