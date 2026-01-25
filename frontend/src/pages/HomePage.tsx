import React, { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';
import { ImageUploader, UploadWithPreview } from '../components/ImageUploader';
import { ProductForm, ProductFormData } from '../components/ProductForm';
import { FrameworkSelector } from '../components/FrameworkSelector';
import { ImageGallery } from '../components/ImageGallery';
import type {
  HealthResponse,
  SessionImage,
  GenerationStatus,
  DesignFramework,
} from '../api/types';

type Step = 'upload' | 'form' | 'analyzing' | 'frameworks' | 'generating' | 'results';

// Helper to extract error message from various error formats (including Pydantic validation errors)
const extractErrorMessage = (err: any, fallback: string): string => {
  // Check for axios response error
  const detail = err?.response?.data?.detail;

  if (!detail) {
    return err?.message || fallback;
  }

  // If detail is a string, use it directly
  if (typeof detail === 'string') {
    return detail;
  }

  // If detail is an array (Pydantic validation errors), extract messages
  if (Array.isArray(detail)) {
    const messages = detail
      .map((e: any) => {
        if (typeof e === 'string') return e;
        // Pydantic validation error format: { type, loc, msg, input, ctx }
        if (e.msg) {
          const location = Array.isArray(e.loc) ? e.loc.join(' -> ') : '';
          return location ? `${location}: ${e.msg}` : e.msg;
        }
        return JSON.stringify(e);
      })
      .slice(0, 3); // Limit to first 3 errors to avoid overwhelming the user
    return messages.join('; ') || fallback;
  }

  // If detail is an object with a message property
  if (typeof detail === 'object' && detail.message) {
    return detail.message;
  }

  return fallback;
};

export const HomePage: React.FC = () => {
  // Health check state
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Generation flow state
  const [step, setStep] = useState<Step>('upload');
  const [uploads, setUploads] = useState<UploadWithPreview[]>([]);
  const [formData, setFormData] = useState<ProductFormData | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>('pending');
  const [images, setImages] = useState<SessionImage[]>([]);
  const [error, setError] = useState<string | null>(null);

  // MASTER Level: Framework selection state
  const [frameworks, setFrameworks] = useState<DesignFramework[]>([]);
  const [productAnalysis, setProductAnalysis] = useState<string>('');
  const [productAnalysisRaw, setProductAnalysisRaw] = useState<Record<string, unknown> | null>(null);  // Full analysis for regeneration
  const [selectedFramework, setSelectedFramework] = useState<DesignFramework | null>(null);
  const [, setIsAnalyzing] = useState(false);
  const [logoPath, setLogoPath] = useState<string | null>(null);
  const [, setStyleRefPath] = useState<string | null>(null);
  const [globalNote, setGlobalNote] = useState<string>('');

  // Health check on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await apiClient.health();
        setHealth(data);
        setHealthError(null);
      } catch (err) {
        setHealthError('Failed to connect to backend');
        console.error(err);
      } finally {
        setHealthLoading(false);
      }
    };

    checkHealth();
  }, []);

  // Poll for generation status
  useEffect(() => {
    if (!sessionId || generationStatus === 'complete' || generationStatus === 'failed') {
      return;
    }

    if (step !== 'generating') {
      return;
    }

    const pollStatus = async () => {
      try {
        const response = await apiClient.getSessionImages(sessionId);
        setImages(response.images);
        setGenerationStatus(response.status);

        if (response.status === 'complete' || response.status === 'partial' || response.status === 'failed') {
          setStep('results');
        }
      } catch (err) {
        console.error('Failed to poll status:', err);
      }
    };

    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [sessionId, generationStatus, step]);

  const handleUploadsChange = useCallback((newUploads: UploadWithPreview[]) => {
    setUploads(newUploads);
    // Don't auto-advance - let user add multiple images first
    // Only go back to upload if all images are removed while on form step
    if (newUploads.length === 0 && step === 'form') {
      setStep('upload');
    }
    setError(null);
  }, [step]);

  const handleContinueToForm = useCallback(() => {
    if (uploads.length > 0) {
      setStep('form');
    }
  }, [uploads.length]);

  const handleFormSubmit = useCallback(async (data: ProductFormData) => {
    if (uploads.length === 0) return;

    const primaryUpload = uploads[0]; // First image is primary

    setFormData(data);
    setGlobalNote(data.globalNote || '');
    setError(null);
    setIsAnalyzing(true);
    setStep('analyzing');
    setFrameworks([]);
    setSelectedFramework(null);

    try {
      // Upload logo if provided
      let uploadedLogoPath: string | undefined;
      if (data.logoFile) {
        try {
          const logoUpload = await apiClient.uploadImage(data.logoFile);
          uploadedLogoPath = logoUpload.file_path;
          setLogoPath(uploadedLogoPath);
        } catch (err) {
          console.error('Logo upload failed:', err);
          // Continue without logo
        }
      }

      // Upload style reference if provided - IMPORTANT: Do this BEFORE framework analysis
      // so the AI can see the style and extract colors from it
      let uploadedStyleRefPath: string | undefined;
      if (data.styleReferenceFile) {
        console.log('[HomePage] Uploading style reference:', {
          name: data.styleReferenceFile.name,
          type: data.styleReferenceFile.type,
          size: data.styleReferenceFile.size,
        });
        try {
          const styleUpload = await apiClient.uploadImage(data.styleReferenceFile);
          uploadedStyleRefPath = styleUpload.file_path;
          setStyleRefPath(uploadedStyleRefPath);
          console.log('[HomePage] Style reference uploaded successfully:', uploadedStyleRefPath);
        } catch (err: any) {
          console.error('[HomePage] Style reference upload failed:', err);
          console.error('[HomePage] Error details:', err.response?.data || err.message);
          // Show warning but continue without style reference
          console.warn('[HomePage] Continuing without style reference');
        }
      } else {
        console.log('[HomePage] No style reference file provided');
      }

      // MASTER LEVEL: Call GPT-4o Vision Principal Designer AI
      // Pass primary upload path, with additional paths for more context

      // Determine color mode based on user inputs:
      // Check BOTH brandColors (Brand Identity section) AND colorPalette (Style & Color section)
      // Either one means user wants to control colors
      const hasBrandColors = data.brandColors && data.brandColors.length > 0;
      const hasColorPalette = data.colorPalette && data.colorPalette.length > 0;
      const hasLockedColors = hasBrandColors || hasColorPalette;
      const hasStyleReference = !!data.styleReferenceFile;

      // Combine colors from both sources (brandColors takes priority if both exist)
      const lockedColors = hasBrandColors ? data.brandColors : (hasColorPalette ? data.colorPalette : undefined);
      const primaryColor = lockedColors?.[0] || undefined;

      let colorMode: 'locked_palette' | 'suggest_primary' | 'ai_decides';
      if (hasLockedColors) {
        // User explicitly provided colors - LOCK them
        colorMode = 'locked_palette';
      } else if (hasStyleReference) {
        // Style reference but no colors - use suggest_primary so AI extracts from style
        colorMode = 'suggest_primary';
      } else {
        colorMode = 'ai_decides';
      }

      console.log('[HomePage] Color Mode:', colorMode);
      console.log('[HomePage] Brand Colors:', data.brandColors);
      console.log('[HomePage] Color Palette:', data.colorPalette);
      console.log('[HomePage] Has Style Reference File:', hasStyleReference);
      console.log('[HomePage] Style Reference Path:', uploadedStyleRefPath);
      console.log('[HomePage] Final Locked Colors:', lockedColors);
      console.log('[HomePage] Primary Color:', primaryColor);

      const response = await apiClient.analyzeFrameworks({
        product_title: data.productTitle,
        upload_path: primaryUpload.file_path,
        additional_upload_paths: uploads.slice(1).map(u => u.file_path),
        brand_name: data.brandName || undefined,
        features: [data.feature1, data.feature2, data.feature3].filter(Boolean) as string[],
        target_audience: data.targetAudience || undefined,
        primary_color: primaryColor,
        // Color mode and locked colors - works with BOTH brandColors and colorPalette
        color_mode: colorMode,
        locked_colors: lockedColors,
        // Style reference image - AI sees this and extracts colors/style from it
        style_reference_path: uploadedStyleRefPath,
      });

      setProductAnalysis(response.product_analysis);
      setProductAnalysisRaw(response.product_analysis_raw || null);  // Store full analysis for regeneration
      setFrameworks(response.frameworks);
      setStep('frameworks');
    } catch (err: any) {
      console.error('Framework analysis failed:', err);
      setError(extractErrorMessage(err, 'Failed to analyze product. Please try again.'));
      setStep('form');
    } finally {
      setIsAnalyzing(false);
    }
  }, [uploads]);

  const handleFrameworkSelect = useCallback((framework: DesignFramework) => {
    setSelectedFramework(framework);
  }, []);

  const handleFrameworkConfirm = useCallback(async () => {
    if (uploads.length === 0 || !formData || !selectedFramework) return;

    const primaryUpload = uploads[0];

    setError(null);
    setStep('generating');
    setGenerationStatus('processing');

    try {
      // Parse keywords
      const keywords = formData.keywords
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0)
        .map((keyword) => ({ keyword, intents: [] }));

      // MASTER LEVEL: Generate all images with the selected framework
      // Use the framework's preview image as style reference for ALL 5 images
      const response = await apiClient.generateWithFramework(
        {
          product_title: formData.productTitle,
          feature_1: formData.feature1 || undefined,
          feature_2: formData.feature2 || undefined,
          feature_3: formData.feature3 || undefined,
          target_audience: formData.targetAudience || undefined,
          keywords,
          upload_path: primaryUpload.file_path,
          additional_upload_paths: uploads.slice(1).map(u => u.file_path),
          brand_name: formData.brandName || undefined,
          brand_colors: formData.brandColors,
          logo_path: logoPath || undefined,
          // KEY: Use the selected framework's preview image as style reference
          style_reference_path: selectedFramework.preview_path || undefined,
          // Global note/instructions for all images
          global_note: globalNote || undefined,
        },
        selectedFramework,
        productAnalysisRaw || undefined  // Pass AI's analysis for regeneration context
      );

      setSessionId(response.session_id);
      setGenerationStatus(response.status);

      // Convert to SessionImage format
      const sessionImages: SessionImage[] = response.images.map((img) => ({
        type: img.image_type,
        status: img.status,
        label: getImageLabel(img.image_type),
        url: img.storage_path,
        error: img.error_message,
      }));
      setImages(sessionImages);

      if (response.status === 'complete' || response.status === 'partial') {
        setStep('results');
      }
    } catch (err: any) {
      console.error('Generation failed:', err);
      setError(extractErrorMessage(err, 'Failed to generate images. Please try again.'));
      setStep('frameworks');
    }
  }, [uploads, formData, selectedFramework, logoPath, globalNote]);

  const handleRetry = useCallback(async () => {
    if (!sessionId) return;

    try {
      setGenerationStatus('processing');
      const response = await apiClient.retryFailedImages(sessionId);
      setGenerationStatus(response.status);

      const sessionImages: SessionImage[] = response.images.map((img) => ({
        type: img.image_type,
        status: img.status,
        label: getImageLabel(img.image_type),
        url: img.storage_path,
        error: img.error_message,
      }));
      setImages(sessionImages);
    } catch (err: any) {
      console.error('Retry failed:', err);
      setError(extractErrorMessage(err, 'Failed to retry. Please try again.'));
    }
  }, [sessionId]);

  const handleStartOver = useCallback(() => {
    setStep('upload');
    setUploads([]);
    setFormData(null);
    setSessionId(null);
    setGenerationStatus('pending');
    setImages([]);
    setFrameworks([]);
    setProductAnalysis('');
    setSelectedFramework(null);
    setLogoPath(null);
    setGlobalNote('');
    setError(null);
  }, []);

  const handleRegenerateSingle = useCallback(async (imageType: string, note?: string) => {
    if (!sessionId) return;

    try {
      // Mark the specific image as processing
      setImages((prev) =>
        prev.map((img) =>
          img.type === imageType ? { ...img, status: 'processing' as const } : img
        )
      );

      const result = await apiClient.regenerateSingleImage(sessionId, imageType, note);

      // Update the specific image with the result
      setImages((prev) =>
        prev.map((img) =>
          img.type === imageType
            ? {
                ...img,
                status: result.status as any,
                url: result.storage_path,
                error: result.error_message,
              }
            : img
        )
      );
    } catch (err: any) {
      console.error('Single image regeneration failed:', err);
      setImages((prev) =>
        prev.map((img) =>
          img.type === imageType
            ? { ...img, status: 'failed' as const, error: err.message || 'Regeneration failed' }
            : img
        )
      );
    }
  }, [sessionId]);

  // Edit image handler - modifies existing image instead of regenerating from scratch
  const handleEditImage = useCallback(async (imageType: string, editInstructions: string) => {
    if (!sessionId) return;

    try {
      // Mark the specific image as processing
      setImages((prev) =>
        prev.map((img) =>
          img.type === imageType ? { ...img, status: 'processing' as const } : img
        )
      );

      const result = await apiClient.editSingleImage(sessionId, imageType, editInstructions);

      // Update the specific image with the result
      setImages((prev) =>
        prev.map((img) =>
          img.type === imageType
            ? {
                ...img,
                status: result.status as any,
                url: result.storage_path,
                error: result.error_message,
              }
            : img
        )
      );
    } catch (err: any) {
      console.error('Image edit failed:', err);
      setImages((prev) =>
        prev.map((img) =>
          img.type === imageType
            ? { ...img, status: 'failed' as const, error: err.message || 'Edit failed' }
            : img
        )
      );
    }
  }, [sessionId]);

  const isGeminiConfigured = health?.dependencies?.gemini === 'configured';

  return (
    <div className="max-w-5xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">
          Amazon Listing Images
        </h1>
      </div>

      {/* Health Status Warning */}
      {!healthLoading && (healthError || !isGeminiConfigured) && (
        <div className="mb-6 bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-4">
          {healthError ? (
            <p className="text-yellow-300 text-sm">
              <strong>Backend not connected.</strong> Make sure the server is running on port 8000.
            </p>
          ) : !isGeminiConfigured ? (
            <p className="text-yellow-300 text-sm">
              <strong>Gemini API not configured.</strong> Set GEMINI_API_KEY in .env to enable image generation.
            </p>
          ) : null}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-6 bg-red-900/20 border border-red-700/50 rounded-lg p-4 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Upload Zone - Mockup Style */}
      {step === 'upload' && (
        <div className="mb-8">
          <ImageUploader
            onUploadsChange={handleUploadsChange}
            disabled={!health || !isGeminiConfigured}
            maxImages={5}
          />

          {/* Continue button */}
          {uploads.length > 0 && (
            <div className="flex justify-end mt-6">
              <button
                onClick={handleContinueToForm}
                className="px-6 py-3 bg-redd-500 text-white font-medium rounded-lg
                         hover:bg-redd-600 transition-colors flex items-center gap-2"
              >
                Continue to Product Details
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          )}
        </div>
      )}

      {step === 'form' && uploads.length > 0 && (
        <div className="space-y-6">
          <div className="flex justify-between items-start">
            <h2 className="text-xl font-semibold text-white">
              Product Details
            </h2>
            <button
              onClick={handleStartOver}
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              Change photo
            </button>
          </div>

          {/* Upload Preview */}
          <div className="flex items-center space-x-3 overflow-x-auto py-2">
            {uploads.map((upload, index) => (
              <div key={upload.upload_id} className="flex-shrink-0 relative">
                <img
                  src={upload.preview_url}
                  alt={`Product ${index + 1}`}
                  className="w-16 h-16 object-contain rounded-lg border-2 border-slate-700 bg-slate-800"
                />
                {index === 0 && (
                  <span className="absolute -top-1 -left-1 bg-redd-500 text-white text-[8px] px-1 rounded">
                    Primary
                  </span>
                )}
              </div>
            ))}
            <span className="text-sm text-slate-500">
              {uploads.length} image{uploads.length > 1 ? 's' : ''}
            </span>
          </div>

          <ProductForm onSubmit={handleFormSubmit} />
        </div>
      )}

      {step === 'analyzing' && (
        <div className="text-center py-16">
          <div className="relative w-20 h-20 mx-auto mb-6">
            <div className="absolute inset-0 rounded-full border-4 border-redd-500/20"></div>
            <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-redd-500 animate-spin"></div>
            <div className="absolute inset-3 flex items-center justify-center bg-redd-500 rounded-full">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">
            Analyzing Your Product...
          </h2>
          <p className="text-slate-400 text-sm">
            Creating design frameworks tailored to your product
          </p>
        </div>
      )}

      {step === 'frameworks' && uploads.length > 0 && frameworks.length > 0 && (
        <div className="space-y-6">
          <div className="flex justify-between items-start">
            <h2 className="text-xl font-semibold text-white">
              Choose Design Style
            </h2>
            <button
              onClick={() => setStep('form')}
              className="text-sm text-slate-400 hover:text-white transition-colors"
            >
              Back
            </button>
          </div>

          <FrameworkSelector
            frameworks={frameworks}
            productAnalysis={productAnalysis}
            selectedFramework={selectedFramework}
            onSelect={handleFrameworkSelect}
            onConfirm={handleFrameworkConfirm}
            isLoading={false}
          />
        </div>
      )}

      {step === 'generating' && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-redd-500 mx-auto mb-6"></div>
          <h2 className="text-xl font-semibold text-white mb-2">
            Generating Images
          </h2>
          <p className="text-slate-400 text-sm mb-8">
            Creating your listing images...
          </p>

          {/* Progress Grid */}
          <div className="grid grid-cols-5 gap-3 max-w-xl mx-auto">
            {images.map((img) => (
              <div
                key={img.type}
                className={`p-3 rounded-lg ${
                  img.status === 'complete'
                    ? 'bg-green-900/20 border border-green-700/50'
                    : img.status === 'processing'
                    ? 'bg-redd-500/10 border border-redd-500/30'
                    : img.status === 'failed'
                    ? 'bg-red-900/20 border border-red-700/50'
                    : 'bg-slate-800/50 border border-slate-700'
                }`}
              >
                <div className="text-xl mb-1">
                  {img.status === 'complete' && <span className="text-green-400">{'\u2713'}</span>}
                  {img.status === 'processing' && <span className="text-redd-400 animate-spin inline-block">{'\u21BB'}</span>}
                  {img.status === 'failed' && <span className="text-red-400">{'\u2717'}</span>}
                  {img.status === 'pending' && <span className="text-slate-500">{'\u25CB'}</span>}
                </div>
                <div className="text-xs font-medium truncate text-slate-400">{img.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {step === 'results' && sessionId && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-white">
              Your Listing Images
            </h2>
            <button
              onClick={handleStartOver}
              className="px-4 py-2 bg-slate-800 text-white text-sm rounded-lg hover:bg-slate-700 transition-colors border border-slate-700"
            >
              New Project
            </button>
          </div>

          <ImageGallery
            sessionId={sessionId}
            images={images}
            status={generationStatus}
            onRetry={handleRetry}
            onRegenerateSingle={handleRegenerateSingle}
            onEditSingle={handleEditImage}
          />
        </div>
      )}
    </div>
  );
};

function getImageLabel(type: string): string {
  const labels: Record<string, string> = {
    main: 'Main Image',
    infographic_1: 'Infographic 1',
    infographic_2: 'Infographic 2',
    lifestyle: 'Lifestyle',
    comparison: 'Comparison',
  };
  return labels[type] || type;
}
