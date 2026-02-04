import React, { useState, useMemo } from 'react';
import { cn } from '@/lib/utils';
import type { SessionImage, DesignFramework } from '@/api/types';
import type { UploadWithPreview } from '../ImageUploader';

// Preview states
export type PreviewState =
  | 'empty'          // No uploads yet
  | 'photos_only'    // Photos uploaded but form not filled
  | 'filling'        // Form being filled, show real-time updates
  | 'framework_selected' // Framework selected, styled preview
  | 'generating'     // Generation in progress
  | 'complete';      // All images generated

interface LivePreviewProps {
  // Preview state
  state: PreviewState;

  // Product info (updates in real-time from form)
  productTitle: string;
  brandName?: string;
  features: string[];

  // Uploads
  productImages: UploadWithPreview[];

  // Framework
  selectedFramework?: DesignFramework;

  // Generation
  sessionId?: string;
  images: SessionImage[];
  generationProgress?: number; // 0-100 (reserved for future use)

  // Device mode
  deviceMode?: 'desktop' | 'mobile';
  onDeviceModeChange?: (mode: 'desktop' | 'mobile') => void;

  // Fullscreen
  isFullscreen?: boolean;
  onFullscreenToggle?: () => void;

  // Selected image (for thumbnail clicks)
  selectedImageType?: string;
  onSelectImage?: (imageType: string) => void;

  // Get image URL helper
  getImageUrl?: (imageType: string) => string;

  className?: string;
}

// Image labels
const IMAGE_LABELS: Record<string, string> = {
  main: 'Main Image',
  infographic_1: 'Infographic 1',
  infographic_2: 'Infographic 2',
  lifestyle: 'Lifestyle',
  comparison: 'Comparison',
};

/**
 * LivePreview - Always-visible Amazon listing preview that updates in real-time
 */
export const LivePreview: React.FC<LivePreviewProps> = ({
  state,
  productTitle,
  brandName,
  features,
  productImages,
  selectedFramework: _selectedFramework, // Reserved for framework-styled preview
  images,
  generationProgress: _generationProgress = 0, // Reserved for progress bar
  deviceMode = 'desktop',
  onDeviceModeChange,
  isFullscreen = false,
  onFullscreenToggle,
  selectedImageType = 'main',
  onSelectImage,
  getImageUrl,
  className,
}) => {
  // Suppress unused variable warnings (reserved for future use)
  void _selectedFramework;
  void _generationProgress;
  const [internalSelectedType, setInternalSelectedType] = useState('main');

  // Use controlled or internal selected type
  const activeSelectedType = selectedImageType || internalSelectedType;
  const handleSelectImage = onSelectImage || setInternalSelectedType;

  // Filter valid features
  const validFeatures = features.filter(Boolean);

  // Get display title (with placeholder if empty)
  const displayTitle = productTitle.trim() || 'Your Product Title';
  const displayBrand = brandName?.trim() || 'BRAND NAME';

  // Sorted images
  const sortedImages = useMemo(() => {
    const order = ['main', 'infographic_1', 'infographic_2', 'lifestyle', 'transformation', 'comparison'];
    return [...images].sort((a, b) => order.indexOf(a.type) - order.indexOf(b.type));
  }, [images]);

  // Get selected image
  const selectedImage = useMemo(
    () => sortedImages.find((img) => img.type === activeSelectedType) || sortedImages[0],
    [sortedImages, activeSelectedType]
  );

  // Count complete images
  const completeCount = images.filter((img) => img.status === 'complete').length;

  // Render empty state
  const renderEmptyState = () => (
    <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center">
      <div className="w-24 h-24 mb-6 rounded-xl bg-slate-700/50 border-2 border-dashed border-slate-600 flex items-center justify-center">
        <svg className="w-10 h-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-white mb-2">Upload your product photos</h3>
      <p className="text-sm text-slate-400 max-w-xs">
        to see your listing come to life
      </p>
    </div>
  );

  // Render photos-only state (placeholder main image)
  const renderPhotosOnlyState = () => (
    <div className="h-full">
      {/* Mini Amazon Preview */}
      <div className={cn(
        'bg-white rounded-xl overflow-hidden border border-slate-200 shadow-lg',
        deviceMode === 'mobile' ? 'max-w-sm mx-auto' : ''
      )}>
        {deviceMode === 'desktop' ? (
          <div className="grid grid-cols-12 gap-0">
            {/* Thumbnails placeholder */}
            <div className="col-span-1 p-3 border-r border-slate-200 bg-slate-50">
              <div className="flex flex-col gap-2">
                {productImages.slice(0, 5).map((upload, index) => (
                  <div
                    key={upload.upload_id}
                    className={cn(
                      'w-12 h-12 rounded-lg overflow-hidden border-2 transition-all',
                      index === 0 ? 'border-redd-500' : 'border-slate-200'
                    )}
                  >
                    <img
                      src={upload.preview_url}
                      alt={`Product ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
                {/* Add placeholder slots */}
                {Array.from({ length: Math.max(0, 5 - productImages.length) }).map((_, i) => (
                  <div
                    key={`placeholder-${i}`}
                    className="w-12 h-12 rounded-lg border-2 border-dashed border-slate-300 bg-slate-100"
                  />
                ))}
              </div>
            </div>

            {/* Main image with overlay */}
            <div className="col-span-6 p-6 border-r border-slate-200">
              <div className="relative aspect-square bg-slate-100 rounded-lg overflow-hidden">
                {productImages[0] && (
                  <img
                    src={productImages[0].preview_url}
                    alt="Product"
                    className="w-full h-full object-contain"
                  />
                )}
                {/* Overlay message */}
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                  <div className="text-center text-white p-4">
                    <svg className="w-12 h-12 mx-auto mb-3 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <p className="text-sm font-medium">Fill in product details</p>
                    <p className="text-xs text-white/70 mt-1">to see your listing preview</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Product info placeholder */}
            <div className="col-span-5 p-6 bg-white">
              <div className="space-y-4 text-left">
                <span className="text-sm text-slate-400">BRAND NAME</span>
                <h1 className="text-xl text-slate-400">Your Product Title</h1>
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <svg key={i} className="w-4 h-4 text-slate-300 fill-current" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <span className="text-sm text-slate-300">(Reviews)</span>
                </div>
                <hr className="border-slate-200" />
                <div>
                  <span className="text-sm text-slate-400">Price: </span>
                  <span className="text-2xl font-medium text-slate-300">$XX.XX</span>
                </div>
                <div className="space-y-2">
                  <span className="text-sm text-slate-400">About this item</span>
                  <div className="text-sm text-slate-300">
                    <p className="flex items-start gap-2">
                      <span className="text-slate-400">•</span>
                      <span>Your features appear here</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // Mobile layout
          <div className="p-4 space-y-4">
            <div className="relative aspect-square bg-slate-100 rounded-lg overflow-hidden">
              {productImages[0] && (
                <img
                  src={productImages[0].preview_url}
                  alt="Product"
                  className="w-full h-full object-contain"
                />
              )}
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                <div className="text-center text-white p-4">
                  <p className="text-sm font-medium">Fill in product details</p>
                </div>
              </div>
            </div>
            <div className="text-slate-400 text-sm">Your Product Title</div>
          </div>
        )}
      </div>
    </div>
  );

  // Render filling state (live form updates)
  const renderFillingState = () => (
    <div className="h-full">
      <div className={cn(
        'bg-white rounded-xl overflow-hidden border border-slate-200 shadow-lg',
        deviceMode === 'mobile' ? 'max-w-sm mx-auto' : ''
      )}>
        {deviceMode === 'desktop' ? (
          <div className="grid grid-cols-12 gap-0">
            {/* Thumbnails */}
            <div className="col-span-1 p-3 border-r border-slate-200 bg-slate-50">
              <div className="flex flex-col gap-2">
                {productImages.slice(0, 5).map((upload, index) => (
                  <div
                    key={upload.upload_id}
                    className={cn(
                      'w-12 h-12 rounded-lg overflow-hidden border-2 transition-all',
                      index === 0 ? 'border-redd-500' : 'border-slate-200'
                    )}
                  >
                    <img
                      src={upload.preview_url}
                      alt={`Product ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
                {Array.from({ length: Math.max(0, 5 - productImages.length) }).map((_, i) => (
                  <div
                    key={`placeholder-${i}`}
                    className="w-12 h-12 rounded-lg border-2 border-dashed border-slate-300 bg-slate-100"
                  />
                ))}
              </div>
            </div>

            {/* Main image */}
            <div className="col-span-6 p-6 border-r border-slate-200">
              <div className="relative aspect-square bg-white rounded-lg overflow-hidden border border-slate-100">
                {productImages[0] && (
                  <img
                    src={productImages[0].preview_url}
                    alt="Product"
                    className="w-full h-full object-contain"
                  />
                )}
              </div>
            </div>

            {/* Product info - LIVE UPDATES */}
            <div className="col-span-5 p-6 bg-white">
              <div className="space-y-4 text-left">
                {/* Brand Name */}
                <a href="#" className="text-sm text-teal-600 hover:underline block">
                  {displayBrand}
                </a>

                {/* Product Title - Live update */}
                <h1 className={cn(
                  'text-xl font-normal leading-tight transition-colors',
                  productTitle.trim() ? 'text-slate-900' : 'text-slate-400'
                )}>
                  {displayTitle}
                </h1>

                {/* Rating */}
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {[1, 2, 3, 4].map((i) => (
                      <svg key={i} className="w-4 h-4 text-amber-400 fill-current" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                    <svg className="w-4 h-4 text-amber-400" viewBox="0 0 20 20">
                      <defs>
                        <linearGradient id="half-star-live">
                          <stop offset="50%" stopColor="currentColor" />
                          <stop offset="50%" stopColor="#E5E7EB" />
                        </linearGradient>
                      </defs>
                      <path fill="url(#half-star-live)" d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                  <span className="text-sm text-teal-600">4.5</span>
                  <span className="text-sm text-slate-500">(1,247 ratings)</span>
                </div>

                <hr className="border-slate-200" />

                <div>
                  <span className="text-sm text-slate-600">Price: </span>
                  <span className="text-2xl font-medium text-slate-900">$XX.XX</span>
                </div>

                {/* Features - Live update */}
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-700">About this item</p>
                  <ul className="space-y-1.5 text-sm text-slate-700">
                    {validFeatures.length > 0 ? (
                      validFeatures.map((feature, index) => (
                        <li key={index} className="flex items-start gap-2 animate-fadeIn">
                          <span className="text-slate-400 mt-0.5">•</span>
                          <span>{feature}</span>
                        </li>
                      ))
                    ) : (
                      <li className="flex items-start gap-2 text-slate-400">
                        <span>•</span>
                        <span>Your features appear here as you type</span>
                      </li>
                    )}
                  </ul>
                </div>

                {/* CTA buttons */}
                <div className="mt-4 space-y-2">
                  <button disabled className="w-full py-2 px-4 bg-amber-400 text-slate-900 text-sm font-medium rounded-full opacity-70 cursor-not-allowed">
                    Add to Cart
                  </button>
                  <button disabled className="w-full py-2 px-4 bg-amber-500 text-slate-900 text-sm font-medium rounded-full opacity-70 cursor-not-allowed">
                    Buy Now
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // Mobile layout
          <div className="flex flex-col">
            <div className="p-4">
              <div className="aspect-square bg-white rounded-lg overflow-hidden">
                {productImages[0] && (
                  <img
                    src={productImages[0].preview_url}
                    alt="Product"
                    className="w-full h-full object-contain"
                  />
                )}
              </div>
            </div>
            <div className="flex gap-2 px-4 pb-4 overflow-x-auto">
              {productImages.slice(0, 5).map((upload, index) => (
                <div
                  key={upload.upload_id}
                  className={cn(
                    'flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden border-2',
                    index === 0 ? 'border-redd-500' : 'border-slate-200'
                  )}
                >
                  <img
                    src={upload.preview_url}
                    alt={`Thumbnail ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </div>
            <div className="p-4 border-t border-slate-200 space-y-3">
              <a href="#" className="text-sm text-teal-600">{displayBrand}</a>
              <h1 className={cn(
                'text-lg',
                productTitle.trim() ? 'text-slate-900' : 'text-slate-400'
              )}>
                {displayTitle}
              </h1>
              {validFeatures.length > 0 && (
                <ul className="text-sm text-slate-700 space-y-1">
                  {validFeatures.map((f, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-slate-400">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Status message */}
      <div className="mt-4 text-center">
        <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          <span className="text-blue-400 text-sm">Live Preview - Updates as you type</span>
        </span>
      </div>
    </div>
  );

  // Render generating state
  const renderGeneratingState = () => (
    <div className="h-full">
      <div className={cn(
        'bg-white rounded-xl overflow-hidden border border-slate-200 shadow-lg',
        deviceMode === 'mobile' ? 'max-w-sm mx-auto' : ''
      )}>
        {deviceMode === 'desktop' ? (
          <div className="grid grid-cols-12 gap-0">
            {/* Thumbnails with progress */}
            <div className="col-span-1 p-3 border-r border-slate-200 bg-slate-50">
              <div className="flex flex-col gap-2">
                {sortedImages.map((img, index) => (
                  <div
                    key={img.type}
                    className={cn(
                      'w-12 h-12 rounded-lg overflow-hidden border-2 transition-all relative',
                      img.type === activeSelectedType ? 'border-redd-500' : 'border-slate-200',
                      img.status === 'complete' ? 'cursor-pointer' : ''
                    )}
                    onClick={() => img.status === 'complete' && handleSelectImage(img.type)}
                  >
                    {img.status === 'complete' && getImageUrl ? (
                      <img
                        src={getImageUrl(img.type)}
                        alt={IMAGE_LABELS[img.type]}
                        className="w-full h-full object-cover"
                      />
                    ) : img.status === 'processing' ? (
                      <div className="w-full h-full bg-slate-100 flex items-center justify-center">
                        <div className="w-5 h-5 border-2 border-redd-500 border-t-transparent rounded-full animate-spin" />
                      </div>
                    ) : (
                      <div className="w-full h-full bg-slate-100 flex items-center justify-center">
                        <span className="text-slate-400 text-xs">{index + 1}</span>
                      </div>
                    )}
                    {/* Number badge */}
                    <span className={cn(
                      'absolute top-0.5 left-0.5 w-4 h-4 rounded text-[10px] font-medium flex items-center justify-center',
                      img.status === 'complete' ? 'bg-green-500 text-white' : 'bg-slate-800/80 text-slate-300'
                    )}>
                      {img.status === 'complete' ? '✓' : index + 1}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Main image area */}
            <div className="col-span-6 p-6 border-r border-slate-200">
              <div className="relative aspect-square bg-slate-100 rounded-lg overflow-hidden">
                {selectedImage?.status === 'complete' && getImageUrl ? (
                  <img
                    src={getImageUrl(selectedImage.type)}
                    alt={IMAGE_LABELS[selectedImage.type]}
                    className="w-full h-full object-contain"
                  />
                ) : selectedImage?.status === 'processing' ? (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-12 h-12 mx-auto mb-4 border-4 border-redd-500 border-t-transparent rounded-full animate-spin" />
                      <p className="text-slate-500 text-sm">Generating {IMAGE_LABELS[selectedImage.type]}...</p>
                    </div>
                  </div>
                ) : productImages[0] ? (
                  <img
                    src={productImages[0].preview_url}
                    alt="Product"
                    className="w-full h-full object-contain opacity-50"
                  />
                ) : null}
              </div>
            </div>

            {/* Product info */}
            <div className="col-span-5 p-6 bg-white">
              <div className="space-y-4 text-left">
                <a href="#" className="text-sm text-teal-600 hover:underline block">{displayBrand}</a>
                <h1 className="text-xl font-normal text-slate-900 leading-tight">{displayTitle}</h1>
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {[1, 2, 3, 4].map((i) => (
                      <svg key={i} className="w-4 h-4 text-amber-400 fill-current" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                    <svg className="w-4 h-4 text-amber-400" viewBox="0 0 20 20">
                      <defs>
                        <linearGradient id="half-star-gen">
                          <stop offset="50%" stopColor="currentColor" />
                          <stop offset="50%" stopColor="#E5E7EB" />
                        </linearGradient>
                      </defs>
                      <path fill="url(#half-star-gen)" d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                  <span className="text-sm text-teal-600">4.5</span>
                  <span className="text-sm text-slate-500">(1,247)</span>
                </div>
                <hr className="border-slate-200" />
                <div>
                  <span className="text-sm text-slate-600">Price: </span>
                  <span className="text-2xl font-medium text-slate-900">$XX.XX</span>
                </div>
                {validFeatures.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-slate-700">About this item</p>
                    <ul className="space-y-1.5 text-sm text-slate-700">
                      {validFeatures.map((feature, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-slate-400 mt-0.5">•</span>
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          // Mobile generating layout
          <div className="p-4 space-y-4">
            <div className="relative aspect-square bg-slate-100 rounded-lg overflow-hidden">
              {selectedImage?.status === 'complete' && getImageUrl ? (
                <img
                  src={getImageUrl(selectedImage.type)}
                  alt={IMAGE_LABELS[selectedImage.type]}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-10 h-10 border-4 border-redd-500 border-t-transparent rounded-full animate-spin" />
                </div>
              )}
            </div>
            <div className="flex gap-2 overflow-x-auto">
              {sortedImages.map((img, index) => (
                <div
                  key={img.type}
                  className={cn(
                    'flex-shrink-0 w-10 h-10 rounded-lg overflow-hidden border-2',
                    img.type === activeSelectedType ? 'border-redd-500' : 'border-slate-200'
                  )}
                >
                  {img.status === 'complete' && getImageUrl ? (
                    <img src={getImageUrl(img.type)} alt="" className="w-full h-full object-cover" />
                  ) : img.status === 'processing' ? (
                    <div className="w-full h-full bg-slate-100 flex items-center justify-center">
                      <div className="w-4 h-4 border-2 border-redd-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                  ) : (
                    <div className="w-full h-full bg-slate-100 flex items-center justify-center text-slate-400 text-xs">
                      {index + 1}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div className="mt-4">
        <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
          <span>Generating images...</span>
          <span>{completeCount} of {images.length}</span>
        </div>
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-redd-500 transition-all duration-500"
            style={{ width: `${(completeCount / images.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );

  // Render complete state (full preview)
  const renderCompleteState = () => (
    <div className="h-full">
      <div className={cn(
        'bg-white rounded-xl overflow-hidden border border-slate-200 shadow-lg',
        deviceMode === 'mobile' ? 'max-w-sm mx-auto' : ''
      )}>
        {deviceMode === 'desktop' ? (
          <div className="grid grid-cols-12 gap-0">
            {/* Thumbnails */}
            <div className="col-span-1 p-3 border-r border-slate-200 bg-slate-50">
              <div className="flex flex-col gap-2">
                {sortedImages.map((img, index) => (
                  <button
                    key={img.type}
                    onClick={() => img.status === 'complete' && handleSelectImage(img.type)}
                    disabled={img.status !== 'complete'}
                    className={cn(
                      'w-12 h-12 rounded-lg overflow-hidden border-2 transition-all relative',
                      img.type === activeSelectedType ? 'border-redd-500 ring-2 ring-redd-500/30' : 'border-slate-200 hover:border-slate-300',
                      img.status !== 'complete' && 'opacity-50 cursor-not-allowed'
                    )}
                  >
                    {img.status === 'complete' && getImageUrl ? (
                      <img
                        src={getImageUrl(img.type)}
                        alt={IMAGE_LABELS[img.type]}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-slate-100 flex items-center justify-center">
                        <span className="text-slate-400 text-xs">{index + 1}</span>
                      </div>
                    )}
                    <span className={cn(
                      'absolute top-0.5 left-0.5 w-4 h-4 rounded text-[10px] font-medium flex items-center justify-center',
                      img.type === activeSelectedType ? 'bg-redd-500 text-white' : 'bg-slate-800/80 text-slate-300'
                    )}>
                      {index + 1}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Main image */}
            <div className="col-span-6 p-6 border-r border-slate-200">
              <div className="relative aspect-square bg-white rounded-lg overflow-hidden">
                {selectedImage?.status === 'complete' && getImageUrl ? (
                  <>
                    <img
                      src={getImageUrl(selectedImage.type)}
                      alt={IMAGE_LABELS[selectedImage.type]}
                      className="w-full h-full object-contain"
                    />
                    <div className="absolute bottom-3 left-3 px-2 py-1 bg-slate-900/80 backdrop-blur-sm rounded text-xs text-white font-medium">
                      {IMAGE_LABELS[selectedImage.type]}
                    </div>
                  </>
                ) : null}
              </div>
            </div>

            {/* Product info */}
            <div className="col-span-5 p-6 bg-white">
              <div className="space-y-4 text-left">
                <a href="#" className="text-sm text-teal-600 hover:underline block">{displayBrand}</a>
                <h1 className="text-xl font-normal text-slate-900 leading-tight">{displayTitle}</h1>
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {[1, 2, 3, 4].map((i) => (
                      <svg key={i} className="w-4 h-4 text-amber-400 fill-current" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                    <svg className="w-4 h-4 text-amber-400" viewBox="0 0 20 20">
                      <defs>
                        <linearGradient id="half-star-complete">
                          <stop offset="50%" stopColor="currentColor" />
                          <stop offset="50%" stopColor="#E5E7EB" />
                        </linearGradient>
                      </defs>
                      <path fill="url(#half-star-complete)" d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                  <span className="text-sm text-teal-600">4.5</span>
                  <span className="text-sm text-slate-500">(1,247 ratings)</span>
                </div>
                <hr className="border-slate-200" />
                <div>
                  <span className="text-sm text-slate-600">Price: </span>
                  <span className="text-2xl font-medium text-slate-900">$XX.XX</span>
                </div>
                {validFeatures.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-slate-700">About this item</p>
                    <ul className="space-y-1.5 text-sm text-slate-700">
                      {validFeatures.map((feature, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-slate-400 mt-0.5">•</span>
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="mt-4 space-y-2">
                  <button disabled className="w-full py-2 px-4 bg-amber-400 text-slate-900 text-sm font-medium rounded-full opacity-70 cursor-not-allowed">
                    Add to Cart
                  </button>
                  <button disabled className="w-full py-2 px-4 bg-amber-500 text-slate-900 text-sm font-medium rounded-full opacity-70 cursor-not-allowed">
                    Buy Now
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // Mobile complete layout
          <div className="flex flex-col">
            <div className="p-4">
              <div className="aspect-square bg-white rounded-lg overflow-hidden">
                {selectedImage?.status === 'complete' && getImageUrl && (
                  <img
                    src={getImageUrl(selectedImage.type)}
                    alt={IMAGE_LABELS[selectedImage.type]}
                    className="w-full h-full object-contain"
                  />
                )}
              </div>
            </div>
            <div className="flex gap-2 px-4 pb-4 overflow-x-auto">
              {sortedImages.map((img, index) => (
                <button
                  key={img.type}
                  onClick={() => img.status === 'complete' && handleSelectImage(img.type)}
                  disabled={img.status !== 'complete'}
                  className={cn(
                    'flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden border-2',
                    img.type === activeSelectedType ? 'border-redd-500' : 'border-slate-200',
                    img.status !== 'complete' && 'opacity-50'
                  )}
                >
                  {img.status === 'complete' && getImageUrl ? (
                    <img src={getImageUrl(img.type)} alt={`Thumb ${index + 1}`} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full bg-slate-100 flex items-center justify-center text-slate-400 text-xs">
                      {index + 1}
                    </div>
                  )}
                </button>
              ))}
            </div>
            <div className="p-4 border-t border-slate-200">
              <a href="#" className="text-sm text-teal-600 block mb-2">{displayBrand}</a>
              <h1 className="text-lg text-slate-900 mb-2">{displayTitle}</h1>
              {validFeatures.length > 0 && (
                <ul className="text-sm text-slate-700 space-y-1">
                  {validFeatures.map((f, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-slate-400">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Ready status */}
      <div className="mt-4 text-center">
        <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-green-400 text-sm">All images ready</span>
        </span>
      </div>
    </div>
  );

  // Render toolbar
  const renderToolbar = () => (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        {/* Device mode toggle */}
        {onDeviceModeChange && (
          <div className="flex items-center rounded-lg bg-slate-700 p-1">
            <button
              onClick={() => onDeviceModeChange('desktop')}
              className={cn(
                'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                deviceMode === 'desktop' ? 'bg-slate-600 text-white' : 'text-slate-400 hover:text-white'
              )}
            >
              Desktop
            </button>
            <button
              onClick={() => onDeviceModeChange('mobile')}
              className={cn(
                'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                deviceMode === 'mobile' ? 'bg-slate-600 text-white' : 'text-slate-400 hover:text-white'
              )}
            >
              Mobile
            </button>
          </div>
        )}
      </div>

      {/* Fullscreen toggle */}
      {onFullscreenToggle && (
        <button
          onClick={onFullscreenToggle}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
          aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isFullscreen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            )}
          </svg>
        </button>
      )}
    </div>
  );

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* Toolbar (only show for certain states) */}
      {(state === 'filling' || state === 'framework_selected' || state === 'generating' || state === 'complete') && renderToolbar()}

      {/* Main content based on state */}
      <div className="flex-1">
        {state === 'empty' && renderEmptyState()}
        {state === 'photos_only' && renderPhotosOnlyState()}
        {(state === 'filling' || state === 'framework_selected') && renderFillingState()}
        {state === 'generating' && renderGeneratingState()}
        {state === 'complete' && renderCompleteState()}
      </div>
    </div>
  );
};

export default LivePreview;
