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
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [logoPath, setLogoPath] = useState<string | null>(null);
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

  const stepLabels = ['Upload', 'Details', 'Design AI', 'Generate', 'Download'];
  const stepMap: Step[] = ['upload', 'form', 'frameworks', 'generating', 'results'];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Principal Designer AI for Amazon Listings
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          GPT-4o Vision analyzes your product and creates 4 unique design frameworks
        </p>
        <p className="text-sm text-gray-500">
          Each framework includes exact colors, typography, headlines, and story arc — tailored specifically to YOUR product
        </p>
      </div>

      {/* Health Status Warning */}
      {!healthLoading && (healthError || !isGeminiConfigured) && (
        <div className="mb-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          {healthError ? (
            <p className="text-yellow-800">
              <strong>Backend not connected.</strong> Make sure the server is running on port 8000.
            </p>
          ) : !isGeminiConfigured ? (
            <p className="text-yellow-800">
              <strong>Gemini API not configured.</strong> Set GEMINI_API_KEY in .env to enable image generation.
            </p>
          ) : null}
        </div>
      )}

      {/* Main Content */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        {/* Progress Steps */}
        <div className="flex items-center justify-center space-x-3 mb-8">
          {stepLabels.map((label, index) => {
            const isActive = stepMap.indexOf(step) >= index;
            const isCurrent = stepMap[index] === step;

            return (
              <React.Fragment key={label}>
                <div className="flex items-center">
                  <div
                    className={`
                      w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm
                      ${isActive ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'}
                      ${isCurrent ? 'ring-4 ring-primary-200' : ''}
                    `}
                  >
                    {index + 1}
                  </div>
                  <span
                    className={`ml-2 text-sm ${isActive ? 'text-gray-900' : 'text-gray-400'}`}
                  >
                    {label}
                  </span>
                </div>
                {index < stepLabels.length - 1 && (
                  <div
                    className={`w-8 h-0.5 ${isActive ? 'bg-primary-600' : 'bg-gray-200'}`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        )}

        {/* Step Content */}
        {step === 'upload' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Step 1: Upload Your Product Photos
            </h2>
            <ImageUploader
              onUploadsChange={handleUploadsChange}
              disabled={!health || !isGeminiConfigured}
              maxImages={5}
            />

            {/* Continue button - only show when at least one image uploaded */}
            {uploads.length > 0 && (
              <div className="flex justify-end pt-4 border-t">
                <button
                  onClick={handleContinueToForm}
                  className="px-6 py-3 bg-primary-600 text-white font-medium rounded-lg
                           hover:bg-primary-700 transition-colors flex items-center gap-2"
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
              <h2 className="text-xl font-semibold text-gray-900">
                Step 2: Enter Product Details
              </h2>
              <button
                onClick={handleStartOver}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Change photo
              </button>
            </div>

            {/* Upload Preview */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-3 overflow-x-auto">
                {uploads.map((upload, index) => (
                  <div key={upload.upload_id} className="flex-shrink-0 relative">
                    <img
                      src={upload.preview_url}
                      alt={`Product ${index + 1}`}
                      className="w-16 h-16 object-contain rounded border-2 border-gray-200"
                    />
                    {index === 0 && (
                      <span className="absolute -top-1 -left-1 bg-primary-600 text-white text-[8px] px-1 rounded">
                        Primary
                      </span>
                    )}
                  </div>
                ))}
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {uploads.length} image{uploads.length > 1 ? 's' : ''} uploaded
              </p>
            </div>

            <ProductForm onSubmit={handleFormSubmit} />
          </div>
        )}

        {step === 'analyzing' && (
          <div className="text-center py-16">
            <div className="relative w-24 h-24 mx-auto mb-8">
              {/* Outer ring */}
              <div className="absolute inset-0 rounded-full border-4 border-primary-100"></div>
              {/* Spinning ring */}
              <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-primary-600 animate-spin"></div>
              {/* Eye icon in center */}
              <div className="absolute inset-4 flex items-center justify-center bg-gradient-to-br from-primary-500 to-blue-600 rounded-full">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Principal Designer AI Working...
            </h2>
            <div className="space-y-2 max-w-md mx-auto">
              <p className="text-gray-600">
                1. GPT-4o Vision analyzing your product
              </p>
              <p className="text-gray-600">
                2. Creating 4 unique design frameworks
              </p>
              <p className="text-gray-600">
                3. Generating preview images for each style
              </p>
            </div>
            <p className="text-sm text-gray-500 mt-4">
              This takes 2-3 minutes (4 images are being generated)
            </p>
          </div>
        )}

        {step === 'frameworks' && uploads.length > 0 && frameworks.length > 0 && (
          <div className="space-y-6">
            <div className="flex justify-between items-start">
              <h2 className="text-xl font-semibold text-gray-900">
                Step 3: Choose Your Design Framework
              </h2>
              <button
                onClick={() => setStep('form')}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Back to details
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
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mx-auto mb-6"></div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Generating Your Images
            </h2>
            {selectedFramework && (
              <p className="text-primary-600 font-medium mb-2">
                Using "{selectedFramework.framework_name}" Framework
              </p>
            )}
            <p className="text-gray-600 mb-2">
              Creating 5 cohesive listing images with exact specifications
            </p>
            <p className="text-sm text-gray-500 mb-8">
              This may take a few minutes. Please don't close this page.
            </p>

            {/* Progress Grid */}
            <div className="grid grid-cols-5 gap-4 max-w-2xl mx-auto">
              {images.map((img) => (
                <div
                  key={img.type}
                  className={`p-4 rounded-lg ${
                    img.status === 'complete'
                      ? 'bg-green-100'
                      : img.status === 'processing'
                      ? 'bg-blue-100'
                      : img.status === 'failed'
                      ? 'bg-red-100'
                      : 'bg-gray-100'
                  }`}
                >
                  <div className="text-2xl mb-1">
                    {img.status === 'complete' && '\u2713'}
                    {img.status === 'processing' && '\u21BB'}
                    {img.status === 'failed' && '\u2717'}
                    {img.status === 'pending' && '\u25F7'}
                  </div>
                  <div className="text-xs font-medium truncate">{img.label}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 'results' && sessionId && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div />
              <button
                onClick={handleStartOver}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Generate New Images
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

      {/* System Status (Collapsible) */}
      {health && (
        <details className="mt-8">
          <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-700">
            System Status
          </summary>
          <div className="mt-2 bg-white rounded-lg shadow p-4 text-sm">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <span className="text-gray-500">Database:</span>
                <span
                  className={`ml-2 ${
                    health.dependencies.database === 'connected'
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  {health.dependencies.database}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Storage:</span>
                <span
                  className={`ml-2 ${
                    health.dependencies.storage === 'accessible'
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  {health.dependencies.storage}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Gemini:</span>
                <span
                  className={`ml-2 ${
                    health.dependencies.gemini === 'configured'
                      ? 'text-green-600'
                      : 'text-yellow-600'
                  }`}
                >
                  {health.dependencies.gemini}
                </span>
              </div>
            </div>
          </div>
        </details>
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
