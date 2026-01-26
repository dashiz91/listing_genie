import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { apiClient } from '../api/client';
import { SplitScreenLayout, WorkshopPanel, ShowroomPanel } from '../components/split-layout';
import type { WorkshopFormData } from '../components/split-layout';
import type { UploadWithPreview } from '../components/ImageUploader';
import type { PreviewState } from '../components/live-preview';
import type {
  HealthResponse,
  SessionImage,
  GenerationStatus,
  DesignFramework,
} from '../api/types';

// Helper to extract error message from various error formats
const extractErrorMessage = (err: any, fallback: string): string => {
  const detail = err?.response?.data?.detail;

  if (!detail) {
    return err?.message || fallback;
  }

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((e: any) => {
        if (typeof e === 'string') return e;
        if (e.msg) {
          const location = Array.isArray(e.loc) ? e.loc.join(' -> ') : '';
          return location ? `${location}: ${e.msg}` : e.msg;
        }
        return JSON.stringify(e);
      })
      .slice(0, 3);
    return messages.join('; ') || fallback;
  }

  if (typeof detail === 'object' && detail.message) {
    return detail.message;
  }

  return fallback;
};

// Initial form data
const initialFormData: WorkshopFormData = {
  productTitle: '',
  feature1: '',
  feature2: '',
  feature3: '',
  targetAudience: '',
  keywords: '',
  brandName: '',
  brandColors: [],
  logoFile: null,
  logoPreview: null,
  styleReferenceFile: null,
  styleReferencePreview: null,
  colorCount: null,
  colorPalette: [],
  globalNote: '',
};

export const HomePage: React.FC = () => {
  // Health check state
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Uploads state
  const [uploads, setUploads] = useState<UploadWithPreview[]>([]);

  // Form state (real-time updates)
  const [formData, setFormData] = useState<WorkshopFormData>(initialFormData);

  // Framework state
  const [frameworks, setFrameworks] = useState<DesignFramework[]>([]);
  const [selectedFramework, setSelectedFramework] = useState<DesignFramework | null>(null);
  const [productAnalysis, setProductAnalysis] = useState<string>('');
  const [productAnalysisRaw, setProductAnalysisRaw] = useState<Record<string, unknown> | null>(null);

  // Generation state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>('pending');
  const [images, setImages] = useState<SessionImage[]>([]);

  // UI state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>(['photos', 'product']);

  // Uploaded paths (for API calls)
  const [logoPath, setLogoPath] = useState<string | null>(null);

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

    if (!isGenerating) {
      return;
    }

    const pollStatus = async () => {
      try {
        const response = await apiClient.getSessionImages(sessionId);
        setImages(response.images);
        setGenerationStatus(response.status);

        if (response.status === 'complete' || response.status === 'partial' || response.status === 'failed') {
          setIsGenerating(false);
        }
      } catch (err) {
        console.error('Failed to poll status:', err);
      }
    };

    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [sessionId, generationStatus, isGenerating]);

  // Calculate preview state
  const previewState: PreviewState = useMemo(() => {
    if (isGenerating || (generationStatus !== 'pending' && images.some((img) => img.status === 'processing'))) {
      return 'generating';
    }
    if (generationStatus === 'complete' || generationStatus === 'partial') {
      return 'complete';
    }
    if (selectedFramework) {
      return 'framework_selected';
    }
    if (uploads.length === 0) {
      return 'empty';
    }
    if (!formData.productTitle.trim()) {
      return 'photos_only';
    }
    return 'filling';
  }, [uploads.length, formData.productTitle, selectedFramework, isGenerating, generationStatus, images]);

  // Features array for preview
  const features = useMemo(
    () => [formData.feature1, formData.feature2, formData.feature3],
    [formData.feature1, formData.feature2, formData.feature3]
  );

  // Can analyze?
  const canAnalyze = uploads.length > 0 && formData.productTitle.trim().length > 0 && !isAnalyzing;

  // Can generate?
  const canGenerate = selectedFramework !== null && !isGenerating;

  // Handle form changes (real-time)
  const handleFormChange = useCallback((partial: Partial<WorkshopFormData>) => {
    setFormData((prev) => ({ ...prev, ...partial }));
  }, []);

  // Handle section toggle
  const handleSectionToggle = useCallback((section: string) => {
    setExpandedSections((prev) =>
      prev.includes(section) ? prev.filter((s) => s !== section) : [...prev, section]
    );
  }, []);

  // Handle uploads change
  const handleUploadsChange = useCallback((newUploads: UploadWithPreview[]) => {
    setUploads(newUploads);
    setError(null);
  }, []);

  // Handle analyze (frameworks)
  const handleAnalyze = useCallback(async () => {
    if (uploads.length === 0 || !formData.productTitle.trim()) return;

    const primaryUpload = uploads[0];

    setError(null);
    setIsAnalyzing(true);
    setFrameworks([]);
    setSelectedFramework(null);

    try {
      // Upload logo if provided
      let uploadedLogoPath: string | undefined;
      if (formData.logoFile) {
        try {
          const logoUpload = await apiClient.uploadImage(formData.logoFile);
          uploadedLogoPath = logoUpload.file_path;
          setLogoPath(uploadedLogoPath);
        } catch (err) {
          console.error('Logo upload failed:', err);
        }
      }

      // Upload style reference if provided
      let uploadedStyleRefPath: string | undefined;
      if (formData.styleReferenceFile) {
        try {
          const styleUpload = await apiClient.uploadImage(formData.styleReferenceFile);
          uploadedStyleRefPath = styleUpload.file_path;
        } catch (err) {
          console.error('Style reference upload failed:', err);
        }
      }

      // Determine color mode
      const hasBrandColors = formData.brandColors.length > 0;
      const hasColorPalette = formData.colorPalette.length > 0;
      const hasLockedColors = hasBrandColors || hasColorPalette;
      const hasStyleReference = !!formData.styleReferenceFile;

      const lockedColors = hasBrandColors ? formData.brandColors : hasColorPalette ? formData.colorPalette : undefined;
      const primaryColor = lockedColors?.[0] || undefined;

      let colorMode: 'locked_palette' | 'suggest_primary' | 'ai_decides';
      if (hasLockedColors) {
        colorMode = 'locked_palette';
      } else if (hasStyleReference) {
        colorMode = 'suggest_primary';
      } else {
        colorMode = 'ai_decides';
      }

      // Call API
      const response = await apiClient.analyzeFrameworks({
        product_title: formData.productTitle,
        upload_path: primaryUpload.file_path,
        additional_upload_paths: uploads.slice(1).map((u) => u.file_path),
        brand_name: formData.brandName || undefined,
        features: [formData.feature1, formData.feature2, formData.feature3].filter(Boolean) as string[],
        target_audience: formData.targetAudience || undefined,
        primary_color: primaryColor,
        color_mode: colorMode,
        locked_colors: lockedColors,
        style_reference_path: uploadedStyleRefPath,
      });

      setProductAnalysis(response.product_analysis);
      setProductAnalysisRaw(response.product_analysis_raw || null);
      setFrameworks(response.frameworks);

      // Open framework section
      setExpandedSections((prev) => (prev.includes('framework') ? prev : [...prev, 'framework']));
    } catch (err: any) {
      console.error('Framework analysis failed:', err);
      setError(extractErrorMessage(err, 'Failed to analyze product. Please try again.'));
    } finally {
      setIsAnalyzing(false);
    }
  }, [uploads, formData]);

  // Handle framework select
  const handleSelectFramework = useCallback((framework: DesignFramework) => {
    setSelectedFramework(framework);
  }, []);

  // Handle generate
  const handleGenerate = useCallback(async () => {
    if (uploads.length === 0 || !selectedFramework) return;

    const primaryUpload = uploads[0];

    setError(null);
    setIsGenerating(true);
    setGenerationStatus('processing');

    try {
      // Parse keywords
      const keywords = formData.keywords
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0)
        .map((keyword) => ({ keyword, intents: [] }));

      // Generate
      const response = await apiClient.generateWithFramework(
        {
          product_title: formData.productTitle,
          feature_1: formData.feature1 || undefined,
          feature_2: formData.feature2 || undefined,
          feature_3: formData.feature3 || undefined,
          target_audience: formData.targetAudience || undefined,
          keywords,
          upload_path: primaryUpload.file_path,
          additional_upload_paths: uploads.slice(1).map((u) => u.file_path),
          brand_name: formData.brandName || undefined,
          brand_colors: formData.brandColors,
          logo_path: logoPath || undefined,
          style_reference_path: selectedFramework.preview_path || undefined,
          global_note: formData.globalNote || undefined,
        },
        selectedFramework,
        productAnalysisRaw || undefined
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
        setIsGenerating(false);
      }
    } catch (err: any) {
      console.error('Generation failed:', err);
      setError(extractErrorMessage(err, 'Failed to generate images. Please try again.'));
      setIsGenerating(false);
    }
  }, [uploads, formData, selectedFramework, logoPath, productAnalysisRaw]);

  // Handle retry
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

  // Handle regenerate single
  const handleRegenerateSingle = useCallback(
    async (imageType: string, note?: string) => {
      if (!sessionId) return;

      try {
        setImages((prev) =>
          prev.map((img) => (img.type === imageType ? { ...img, status: 'processing' as const } : img))
        );

        const result = await apiClient.regenerateSingleImage(sessionId, imageType, note);

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
            img.type === imageType ? { ...img, status: 'failed' as const, error: err.message || 'Regeneration failed' } : img
          )
        );
      }
    },
    [sessionId]
  );

  // Handle edit single
  const handleEditSingle = useCallback(
    async (imageType: string, editInstructions: string) => {
      if (!sessionId) return;

      try {
        setImages((prev) =>
          prev.map((img) => (img.type === imageType ? { ...img, status: 'processing' as const } : img))
        );

        const result = await apiClient.editSingleImage(sessionId, imageType, editInstructions);

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
            img.type === imageType ? { ...img, status: 'failed' as const, error: err.message || 'Edit failed' } : img
          )
        );
      }
    },
    [sessionId]
  );

  // Handle start over
  const handleStartOver = useCallback(() => {
    setUploads([]);
    setFormData(initialFormData);
    setFrameworks([]);
    setSelectedFramework(null);
    setProductAnalysis('');
    setProductAnalysisRaw(null);
    setSessionId(null);
    setGenerationStatus('pending');
    setImages([]);
    setIsAnalyzing(false);
    setIsGenerating(false);
    setLogoPath(null);
    setError(null);
    setExpandedSections(['photos', 'product']);
  }, []);

  const isGeminiConfigured = health?.dependencies?.gemini === 'configured';

  return (
    <div className="h-[calc(100vh-80px)]">
      {/* Health Status Warning */}
      {!healthLoading && (healthError || !isGeminiConfigured) && (
        <div className="mx-6 mt-4 bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-4">
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
        <div className="mx-6 mt-4 bg-red-900/20 border border-red-700/50 rounded-lg p-4 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Split Screen Layout */}
      <SplitScreenLayout
        leftPanel={
          <WorkshopPanel
            uploads={uploads}
            onUploadsChange={handleUploadsChange}
            maxImages={5}
            formData={formData}
            onFormChange={handleFormChange}
            frameworks={frameworks}
            selectedFramework={selectedFramework}
            onSelectFramework={handleSelectFramework}
            isAnalyzing={isAnalyzing}
            productAnalysis={productAnalysis}
            onAnalyze={handleAnalyze}
            onGenerate={handleGenerate}
            onStartOver={handleStartOver}
            isGenerating={isGenerating}
            canAnalyze={canAnalyze}
            canGenerate={canGenerate}
            expandedSections={expandedSections}
            onSectionToggle={handleSectionToggle}
          />
        }
        rightPanel={
          <ShowroomPanel
            previewState={previewState}
            productTitle={formData.productTitle}
            brandName={formData.brandName}
            features={features}
            targetAudience={formData.targetAudience}
            productImages={uploads}
            selectedFramework={selectedFramework || undefined}
            sessionId={sessionId || undefined}
            images={images}
            onRegenerateSingle={handleRegenerateSingle}
            onEditSingle={handleEditSingle}
            onRetry={handleRetry}
            onStartOver={handleStartOver}
          />
        }
      />
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
