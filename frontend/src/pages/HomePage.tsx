import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiClient } from '../api/client';
import { SplitScreenLayout, WorkshopPanel, ShowroomPanel } from '../components/split-layout';
import type { WorkshopFormData } from '../components/split-layout';
import type { UploadWithPreview } from '../components/ImageUploader';
import type { ReferenceImage } from '../api/types';
import type { PreviewState } from '../components/live-preview';
import type {
  HealthResponse,
  SessionImage,
  GenerationStatus,
  DesignFramework,
  AplusVisualScript,
  ImageVersion,
} from '../api/types';
import type { AplusModule, AplusViewportMode } from '../components/preview-slots/AplusSection';
import { getActiveImagePath } from '../components/preview-slots/AplusSection';
import type { SlotStatus } from '../components/preview-slots/ImageSlot';

// Listing image version tracking (uses unified ImageVersion)
export interface ListingVersionState {
  [imageType: string]: {
    versions: ImageVersion[];
    activeIndex: number;
  };
}

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
  styleCount: 4, // Default to 4 style options
  imageModel: 'gemini-3-pro-image-preview', // Default to Pro model
};

export const HomePage: React.FC = () => {
  // URL params for project loading
  const [searchParams, setSearchParams] = useSearchParams();
  const projectParam = searchParams.get('project');

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
  const sessionIdRef = useRef<string | null>(null);
  const sessionCreatingRef = useRef<Promise<string> | null>(null);
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>('pending');
  const [images, setImages] = useState<SessionImage[]>([]);

  // Keep ref in sync with state
  const updateSessionId = useCallback((id: string | null) => {
    sessionIdRef.current = id;
    setSessionId(id);
  }, []);

  // UI state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>(['photos', 'product']);
  const [_isLoadingProject, setIsLoadingProject] = useState(false);

  // Uploaded paths (for API calls)
  const [logoPath, setLogoPath] = useState<string | null>(null);
  const [originalStyleRefPath, setOriginalStyleRefPath] = useState<string | null>(null);
  const [useOriginalStyleRef, setUseOriginalStyleRef] = useState(false);

  // A+ Content modules state — default 6x full-width banners (1464x600)
  const [aplusModules, setAplusModules] = useState<AplusModule[]>(() => {
    return Array.from({ length: 6 }, (_, i) => ({
      id: `aplus-${i + 1}`,
      type: 'full_image' as const,
      index: i,
      status: 'ready' as SlotStatus,
      versions: [] as ImageVersion[],
      activeVersionIndex: 0,
      mobileVersions: [] as ImageVersion[],
      mobileActiveVersionIndex: 0,
      mobileStatus: 'ready' as SlotStatus,
    }));
  });

  // A+ Art Director visual script state
  const [aplusVisualScript, setAplusVisualScript] = useState<AplusVisualScript | null>(null);
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);

  // A+ viewport mode (desktop vs mobile)
  const [aplusViewportMode, setAplusViewportMode] = useState<AplusViewportMode>('desktop');

  // Listing image version tracking (lifted from AmazonListingPreview)
  const [listingVersions, setListingVersions] = useState<ListingVersionState>({});

  // Load project from URL param (?project= or ?session=)
  useEffect(() => {
    const loadProject = async () => {
      const sessionParam = projectParam || searchParams.get('session');
      if (!sessionParam) return;

      setIsLoadingProject(true);
      try {
        const project = await apiClient.getProjectDetail(sessionParam);

        // 1. Restore form data
        // Determine the best style reference preview to show:
        // - original_style_reference_path (user's uploaded style reference)
        // - or style_reference_path if it's not a framework preview
        const styleRefPath = project.original_style_reference_path ||
          (project.style_reference_path && !project.style_reference_path.includes('framework_preview')
            ? project.style_reference_path
            : null);

        setFormData((prev) => ({
          ...prev,
          productTitle: project.product_title,
          brandName: project.brand_name || '',
          feature1: project.feature_1 || '',
          feature2: project.feature_2 || '',
          feature3: project.feature_3 || '',
          targetAudience: project.target_audience || '',
          globalNote: project.global_note || '',
          brandColors: project.brand_colors || [],
          colorPalette: project.color_palette || [],
          colorCount: project.color_count || null,
          // Files can't be restored, but previews can via signed URLs
          logoFile: null,
          logoPreview: project.logo_path ? apiClient.getFileUrl(project.logo_path) : null,
          styleReferenceFile: null,
          // Use versioned style reference URL if available, otherwise fallback to path
          styleReferencePreview: project.style_reference_url || (styleRefPath ? apiClient.getFileUrl(styleRefPath) : null),
        }));

        // 1b. Restore original style reference path for generation calls
        if (project.original_style_reference_path) {
          setOriginalStyleRefPath(project.original_style_reference_path);
        } else if (project.style_reference_path && !project.style_reference_path.includes('framework_preview')) {
          // Fallback: if no original_style_reference_path but style_reference_path is not a framework preview
          setOriginalStyleRefPath(project.style_reference_path);
        }

        // 1c. Restore style reference versions (if any)
        if (project.style_reference_versions && project.style_reference_versions.length > 0) {
          // For now just log - version navigation UI would be added here
          console.log('[STYLE REF] Versions available:', project.style_reference_versions);
        }

        // 2. Restore upload previews from paths
        if (project.upload_path) {
          const allPaths = [project.upload_path, ...(project.additional_upload_paths || [])];
          const restoredUploads: UploadWithPreview[] = allPaths.map((path, idx) => ({
            upload_id: `restored-${idx}`,
            file_path: path,
            filename: `product-${idx + 1}.png`,
            size: 0,
            preview_url: apiClient.getFileUrl(path),
          }));
          setUploads(restoredUploads);
        }

        // 3. Restore logo path for generation calls
        if (project.logo_path) {
          setLogoPath(project.logo_path);
        }

        // 4. Restore design framework
        if (project.design_framework) {
          const fw = project.design_framework as DesignFramework;
          // If the framework has no preview_url, use the style_reference_path
          // (which stores the framework preview image after selection)
          if (!fw.preview_url && project.style_reference_path) {
            fw.preview_url = apiClient.getFileUrl(project.style_reference_path);
          }
          setSelectedFramework(fw);
          // Put it in frameworks array so the Workshop panel shows
          // "Generate" instead of "Preview Styles"
          setFrameworks([fw]);
        }

        // 5. Restore product analysis
        if (project.product_analysis_summary) {
          setProductAnalysis(project.product_analysis_summary);
        }
        if (project.product_analysis) {
          setProductAnalysisRaw(project.product_analysis);
        }

        // 6. Restore session and images
        updateSessionId(project.session_id);
        setGenerationStatus(project.status as GenerationStatus);

        const sessionImages: SessionImage[] = project.images.map((img) => ({
          type: img.image_type,
          status: img.status as 'complete' | 'processing' | 'failed' | 'pending',
          label: getImageLabel(img.image_type),
          url: img.image_url || undefined,
          error: img.error_message || undefined,
        }));
        setImages(sessionImages);

        // Restore listing image versions
        const restoredVersions: ListingVersionState = {};
        for (const img of project.images) {
          if (img.status === 'complete' && img.image_url) {
            console.log(`[VERSION DEBUG] ${img.image_type}: versions from API =`, img.versions);
            if (img.versions && img.versions.length > 0) {
              restoredVersions[img.image_type] = {
                versions: img.versions.map(v => ({ imageUrl: v.image_url, timestamp: Date.now() })),
                activeIndex: img.versions.length - 1,
              };
            } else {
              restoredVersions[img.image_type] = {
                versions: [{ imageUrl: img.image_url, timestamp: Date.now() }],
                activeIndex: 0,
              };
            }
          }
        }
        console.log('[VERSION DEBUG] Restored listing versions:', restoredVersions);
        setListingVersions(restoredVersions);

        // 7. Restore A+ Content state
        if (project.aplus_visual_script) {
          setAplusVisualScript(project.aplus_visual_script);
        }
        if (project.aplus_modules && project.aplus_modules.length > 0) {
          setAplusModules(
            project.aplus_modules.map((m, i) => ({
              id: `aplus-${i + 1}`,
              type: (m.module_type || 'full_image') as 'full_image',
              index: m.module_index,
              status: (m.image_url ? 'complete' : 'ready') as SlotStatus,
              versions: m.versions && m.versions.length > 0
                ? m.versions.map(v => ({ imageUrl: v.image_url, imagePath: v.image_path }))
                : m.image_url && m.image_path
                  ? [{ imageUrl: m.image_url, imagePath: m.image_path }]
                  : [],
              activeVersionIndex: m.versions && m.versions.length > 0
                ? m.versions.length - 1
                : 0,
              mobileVersions: m.mobile_versions && m.mobile_versions.length > 0
                ? m.mobile_versions.map(v => ({ imageUrl: v.image_url, imagePath: v.image_path }))
                : m.mobile_image_url && m.mobile_image_path
                  ? [{ imageUrl: m.mobile_image_url, imagePath: m.mobile_image_path }]
                  : [],
              mobileActiveVersionIndex: m.mobile_versions && m.mobile_versions.length > 0
                ? m.mobile_versions.length - 1
                : 0,
              mobileStatus: (m.mobile_image_url ? 'complete' : 'ready') as SlotStatus,
            }))
          );
        }

        // Persist session in URL (replace ?project= with ?session=)
        setSearchParams({ session: project.session_id }, { replace: true });
      } catch (err) {
        console.error('Failed to load project:', err);
        setError('Failed to load project. It may have been deleted.');
        setSearchParams({}, { replace: true });
      } finally {
        setIsLoadingProject(false);
      }
    };

    loadProject();
  }, [projectParam]);

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

        // Capture version snapshots for newly completed images
        response.images.forEach((img: SessionImage) => {
          if (img.status === 'complete') {
            setListingVersions(prev => {
              if (prev[img.type]?.versions.length) return prev; // already captured
              return { ...prev, [img.type]: {
                versions: [{ imageUrl: apiClient.getImageUrl(sessionId, img.type) + `?t=${Date.now()}`, timestamp: Date.now() }],
                activeIndex: 0,
              }};
            });
          }
        });

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
    // Clear any previous session — analyze creates a preview session that can't be
    // used for /generate/single (it only has STYLE_PREVIEW image records)
    updateSessionId(null);
    setSearchParams({}, { replace: true });

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
          setOriginalStyleRefPath(styleUpload.file_path);
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
        framework_count: formData.styleCount, // Number of styles to generate (1-4)
        skip_preview_generation: useOriginalStyleRef,
      });

      setProductAnalysis(response.product_analysis);
      setProductAnalysisRaw(response.product_analysis_raw || null);
      setFrameworks(response.frameworks);

      // Note: Do NOT store the analyze session in sessionIdRef — it's a preview session
      // without image records for main/infographic/etc. ensureSession() would reuse it
      // and /generate/single would fail with 400. The analyze session is saved in the DB
      // so it still appears in projects.

      // Open framework section
      setExpandedSections((prev) => (prev.includes('framework') ? prev : [...prev, 'framework']));
    } catch (err: any) {
      console.error('Framework analysis failed:', err);
      setError(extractErrorMessage(err, 'Failed to analyze product. Please try again.'));
    } finally {
      setIsAnalyzing(false);
    }
  }, [uploads, formData, useOriginalStyleRef, updateSessionId, setSearchParams]);

  // Handle framework select
  const handleSelectFramework = useCallback((framework: DesignFramework) => {
    setSelectedFramework(framework);
    // Initialize pending images when framework is selected
    if (images.length === 0 || images.every((img) => !img.url)) {
      setImages([
        { type: 'main', status: 'pending', label: 'Main Image' },
        { type: 'infographic_1', status: 'pending', label: 'Infographic 1' },
        { type: 'infographic_2', status: 'pending', label: 'Infographic 2' },
        { type: 'lifestyle', status: 'pending', label: 'Lifestyle' },
        { type: 'comparison', status: 'pending', label: 'Comparison' },
      ]);
    }
  }, [images]);

  // Helper: ensure a session exists (fast — create_only, no image generation)
  // Uses a mutex (ref) to prevent duplicate session creation when multiple slots are clicked concurrently
  const ensureSession = useCallback(async (): Promise<string> => {
    // Already have a generation session (not a preview-only session)
    // A preview session only has style_preview image records, not main/infographic/etc.
    // We detect this by checking if images state has listing image types
    const hasListingImages = images.some((img) =>
      ['main', 'infographic_1', 'infographic_2', 'lifestyle', 'comparison'].includes(img.type)
    );
    if (sessionIdRef.current && hasListingImages) return sessionIdRef.current;

    // Another call is already creating the session — wait for it
    if (sessionCreatingRef.current) {
      return sessionCreatingRef.current;
    }

    const primaryUpload = uploads[0];
    const keywords = formData.keywords
      .split(',')
      .map((k) => k.trim())
      .filter((k) => k.length > 0)
      .map((keyword) => ({ keyword, intents: [] }));

    // Create session only (no generation) — returns fast
    const creationPromise = (async () => {
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
          style_reference_path: (useOriginalStyleRef && originalStyleRefPath) ? originalStyleRefPath : (selectedFramework!.preview_path || undefined),
          // Track original style ref separately for project restoration
          original_style_reference_path: originalStyleRefPath || undefined,
          global_note: formData.globalNote || undefined,
        },
        selectedFramework!,
        productAnalysisRaw || undefined,
        undefined,  // no singleImageType
        true,  // create_only — fast, no generation
        formData.imageModel  // imageModel
      );

      updateSessionId(response.session_id);
      setGenerationStatus(response.status);
      // Persist session to URL for refresh resilience
      setSearchParams({ session: response.session_id }, { replace: true });

      // Set initial images (all pending)
      const sessionImages: SessionImage[] = response.images.map((img) => ({
        type: img.image_type,
        status: img.status,
        label: getImageLabel(img.image_type),
        url: img.storage_path,
        error: img.error_message,
      }));
      setImages(sessionImages);

      return response.session_id;
    })();

    sessionCreatingRef.current = creationPromise;

    try {
      return await creationPromise;
    } finally {
      sessionCreatingRef.current = null;
    }
  }, [uploads, selectedFramework, formData, logoPath, productAnalysisRaw, useOriginalStyleRef, originalStyleRefPath, updateSessionId, setSearchParams, images]);

  // Handle generate single image (when clicking individual slot) — fire-and-forget, concurrent
  const handleGenerateSingle = useCallback(
    async (imageType: string) => {
      if (uploads.length === 0 || !selectedFramework) return;

      // Set image to processing immediately
      setImages((prev) =>
        prev.map((img) => (img.type === imageType ? { ...img, status: 'processing' as const } : img))
      );
      setError(null);

      try {
        // Ensure we have a session (fast — create_only, no generation)
        const currentSessionId = await ensureSession();

        // Generate this single image via /single endpoint
        const result = await apiClient.regenerateSingleImage(currentSessionId, imageType, undefined, undefined, formData.imageModel);

        setImages((prev) =>
          prev.map((img) =>
            img.type === imageType
              ? {
                  ...img,
                  status: result.status as 'pending' | 'processing' | 'complete' | 'failed',
                  url: result.storage_path,
                  error: result.error_message,
                }
              : img
          )
        );

        // Capture version snapshot on completion
        if (result.status === 'complete') {
          const sid = sessionIdRef.current;
          if (sid) {
            setListingVersions(prev => {
              const existing = prev[imageType];
              // First generation — create version 1
              if (!existing || existing.versions.length === 0) {
                return { ...prev, [imageType]: {
                  versions: [{ imageUrl: apiClient.getImageUrl(sid, imageType) + `?t=${Date.now()}`, timestamp: Date.now() }],
                  activeIndex: 0,
                }};
              }
              return prev;
            });
          }
        }
      } catch (err: any) {
        console.error('Single image generation failed:', err);
        setImages((prev) =>
          prev.map((img) =>
            img.type === imageType
              ? { ...img, status: 'failed' as const, error: err.message || 'Generation failed' }
              : img
          )
        );
      }
    },
    [uploads, selectedFramework, ensureSession, formData.imageModel]
  );

  // Generate all 5 images - triggers 5 individual generations (same code path as clicking slots)
  const handleGenerate = useCallback(async () => {
    if (uploads.length === 0 || !selectedFramework) return;

    setError(null);
    setIsGenerating(true);
    setGenerationStatus('processing');

    // Initialize all 5 images as pending (will be set to processing by handleGenerateSingle)
    setImages([
      { type: 'main', status: 'pending', label: 'Main Image' },
      { type: 'infographic_1', status: 'pending', label: 'Infographic 1' },
      { type: 'infographic_2', status: 'pending', label: 'Infographic 2' },
      { type: 'lifestyle', status: 'pending', label: 'Lifestyle' },
      { type: 'comparison', status: 'pending', label: 'Comparison' },
    ]);

    // Fire all 5 generations concurrently (same as clicking all 5 slots)
    // handleGenerateSingle will handle session creation via ensureSession (with mutex)
    const imageTypes = ['main', 'infographic_1', 'infographic_2', 'lifestyle', 'comparison'];

    // Wait for all to complete (but they run concurrently)
    const results = await Promise.allSettled(
      imageTypes.map((type) => handleGenerateSingle(type))
    );

    // Check if any failed
    const anyFailed = results.some((r) => r.status === 'rejected');
    if (anyFailed) {
      setGenerationStatus('partial');
    } else {
      setGenerationStatus('complete');
    }
    setIsGenerating(false);
  }, [uploads, selectedFramework, handleGenerateSingle]);

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
    async (imageType: string, note?: string, referenceImagePaths?: string[]) => {
      console.log('[HOMEPAGE REGEN] Called with:', { imageType, note, referenceImagePaths });
      if (!sessionId) return;

      try {
        setImages((prev) =>
          prev.map((img) => (img.type === imageType ? { ...img, status: 'processing' as const } : img))
        );

        console.log('[HOMEPAGE REGEN] Calling API with referenceImagePaths:', referenceImagePaths);
        const result = await apiClient.regenerateSingleImage(sessionId, imageType, note, referenceImagePaths, formData.imageModel);

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

        // Append new version on success
        if (result.status === 'complete' && sessionId) {
          setListingVersions(prev => {
            const current = prev[imageType] || { versions: [], activeIndex: 0 };
            const newVersions = [...current.versions, {
              imageUrl: apiClient.getImageUrl(sessionId, imageType) + `?t=${Date.now()}`,
              timestamp: Date.now(),
            }];
            return { ...prev, [imageType]: { versions: newVersions, activeIndex: newVersions.length - 1 } };
          });
        }
      } catch (err: any) {
        console.error('Single image regeneration failed:', err);
        setImages((prev) =>
          prev.map((img) =>
            img.type === imageType ? { ...img, status: 'failed' as const, error: err.message || 'Regeneration failed' } : img
          )
        );
      }
    },
    [sessionId, formData.imageModel]
  );

  // Handle cancel generation (client-side only — reverts status)
  const handleCancelGeneration = useCallback(
    (imageType: string) => {
      setImages((prev) =>
        prev.map((img) =>
          img.type === imageType && img.status === 'processing'
            ? { ...img, status: 'failed' as const, error: 'Cancelled by user' }
            : img
        )
      );
    },
    []
  );

  // Handle edit single
  const handleEditSingle = useCallback(
    async (imageType: string, editInstructions: string, referenceImagePaths?: string[]) => {
      if (!sessionId) return;

      try {
        setImages((prev) =>
          prev.map((img) => (img.type === imageType ? { ...img, status: 'processing' as const } : img))
        );

        const result = await apiClient.editSingleImage(sessionId, imageType, editInstructions, referenceImagePaths, formData.imageModel);

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

        // Append new version on success
        if (result.status === 'complete' && sessionId) {
          setListingVersions(prev => {
            const current = prev[imageType] || { versions: [], activeIndex: 0 };
            const newVersions = [...current.versions, {
              imageUrl: apiClient.getImageUrl(sessionId, imageType) + `?t=${Date.now()}`,
              timestamp: Date.now(),
            }];
            return { ...prev, [imageType]: { versions: newVersions, activeIndex: newVersions.length - 1 } };
          });
        }
      } catch (err: any) {
        console.error('Image edit failed:', err);
        setImages((prev) =>
          prev.map((img) =>
            img.type === imageType ? { ...img, status: 'failed' as const, error: err.message || 'Edit failed' } : img
          )
        );
      }
    },
    [sessionId, formData.imageModel]
  );

  // Ensure visual script exists (auto-generate if missing)
  const ensureVisualScript = useCallback(async (sid: string): Promise<AplusVisualScript | null> => {
    if (aplusVisualScript) return aplusVisualScript;

    setIsGeneratingScript(true);
    try {
      const response = await apiClient.generateAplusVisualScript(sid, 6);
      setAplusVisualScript(response.visual_script);
      return response.visual_script;
    } catch (err: any) {
      console.error('Visual script generation failed:', err);
      return null; // Will fall back to legacy prompts
    } finally {
      setIsGeneratingScript(false);
    }
  }, [aplusVisualScript]);

  // Force-regenerate visual script (replaces existing one)
  const regenerateVisualScript = useCallback(async () => {
    if (!sessionId) return;
    setIsGeneratingScript(true);
    setAplusVisualScript(null);
    try {
      const response = await apiClient.generateAplusVisualScript(sessionId, 6);
      setAplusVisualScript(response.visual_script);
      // Adjust module count if needed, but preserve existing images/versions
      const count = response.visual_script.modules?.length || 6;
      setAplusModules((prev) => {
        const updated: typeof prev = [];
        for (let i = 0; i < count; i++) {
          if (i < prev.length) {
            // Keep existing module with its versions intact
            updated.push(prev[i]);
          } else {
            // New slot
            updated.push({
              id: `aplus-${i + 1}`,
              type: 'full_image' as const,
              index: i,
              status: 'ready' as SlotStatus,
              versions: [],
              activeVersionIndex: 0,
              mobileVersions: [],
              mobileActiveVersionIndex: 0,
              mobileStatus: 'ready' as SlotStatus,
            });
          }
        }
        return updated;
      });
    } catch (err: any) {
      console.error('Visual script regeneration failed:', err);
    } finally {
      setIsGeneratingScript(false);
    }
  }, [sessionId]);

  // Handle generate hero pair (modules 0+1 as one image split in half)
  const handleGenerateHeroPair = useCallback(
    async (note?: string, referenceImagePaths?: string[]) => {
      if (!sessionId) return;

      // Set both modules 0 and 1 to generating
      setAplusModules((prev) =>
        prev.map((m, idx) =>
          idx === 0 || idx === 1 ? { ...m, status: 'generating' as SlotStatus } : m
        )
      );

      try {
        // Auto-generate visual script if missing
        await ensureVisualScript(sessionId);

        // Call hero pair endpoint — one Gemini call, split in half
        const result = await apiClient.generateAplusHeroPair(sessionId, note, referenceImagePaths, formData.imageModel);

        // Update both modules with results
        setAplusModules((prev) =>
          prev.map((m, idx) => {
            if (idx === 0) {
              const newVersions = [...m.versions, {
                imageUrl: result.module_0.image_url,
                imagePath: result.module_0.image_path,
                promptText: result.module_0.prompt_text,
              }];
              return {
                ...m,
                status: 'complete' as SlotStatus,
                versions: newVersions,
                activeVersionIndex: newVersions.length - 1,
              };
            }
            if (idx === 1) {
              const newVersions = [...m.versions, {
                imageUrl: result.module_1.image_url,
                imagePath: result.module_1.image_path,
                promptText: result.module_1.prompt_text,
              }];
              return {
                ...m,
                status: 'complete' as SlotStatus,
                versions: newVersions,
                activeVersionIndex: newVersions.length - 1,
              };
            }
            return m;
          })
        );
      } catch (err: any) {
        console.error('Hero pair generation failed:', err);
        setAplusModules((prev) =>
          prev.map((m, idx) =>
            idx === 0 || idx === 1
              ? {
                  ...m,
                  status: 'error' as SlotStatus,
                  errorMessage: extractErrorMessage(err, 'Hero pair generation failed'),
                }
              : m
          )
        );
      }
    },
    [sessionId, ensureVisualScript, formData.imageModel]
  );

  // Handle generate A+ module (for modules 2+)
  const handleGenerateAplusModule = useCallback(
    async (moduleIndex: number, note?: string, referenceImagePaths?: string[]) => {
      if (!sessionId) return;

      // Modules 0 and 1 are always generated together as a hero pair
      if (moduleIndex <= 1) {
        return handleGenerateHeroPair(note, referenceImagePaths);
      }

      const module = aplusModules[moduleIndex];
      if (!module) return;

      // Set module to generating
      setAplusModules((prev) =>
        prev.map((m, idx) =>
          idx === moduleIndex ? { ...m, status: 'generating' as SlotStatus } : m
        )
      );

      try {
        // Auto-generate visual script if missing
        await ensureVisualScript(sessionId);

        // Get previous module path for chaining (if not first module)
        const prevModule = moduleIndex > 0 ? aplusModules[moduleIndex - 1] : null;
        const previousModulePath = prevModule ? getActiveImagePath(prevModule) : undefined;

        // Call API to generate A+ module
        const result = await apiClient.generateAplusModule({
          session_id: sessionId,
          module_type: module.type,
          module_index: moduleIndex,
          previous_module_path: previousModulePath,
          custom_instructions: note,
          reference_image_paths: referenceImagePaths,
          image_model: formData.imageModel,
        });

        // Update module with result — add new version
        // Also update previous module if canvas extension refined it
        setAplusModules((prev) =>
          prev.map((m, idx) => {
            if (idx === moduleIndex) {
              const newVersions = [...m.versions, {
                imageUrl: result.image_url,
                imagePath: result.image_path,
                promptText: result.prompt_text,
              }];
              return {
                ...m,
                status: 'complete' as SlotStatus,
                versions: newVersions,
                activeVersionIndex: newVersions.length - 1,
              };
            }
            // Canvas extension refined the previous module — replace its active version
            if (result.refined_previous && idx === result.refined_previous.module_index) {
              const refined = result.refined_previous;
              const updatedVersions = [...m.versions];
              updatedVersions[m.activeVersionIndex] = {
                ...updatedVersions[m.activeVersionIndex],
                imageUrl: refined.image_url + `?t=${Date.now()}`,
                imagePath: refined.image_path,
              };
              return { ...m, versions: updatedVersions };
            }
            return m;
          })
        );
      } catch (err: any) {
        console.error('A+ module generation failed:', err);
        setAplusModules((prev) =>
          prev.map((m, idx) =>
            idx === moduleIndex
              ? {
                  ...m,
                  status: 'error' as SlotStatus,
                  errorMessage: extractErrorMessage(err, 'A+ generation failed'),
                }
              : m
          )
        );
      }
    },
    [sessionId, aplusModules, ensureVisualScript, handleGenerateHeroPair, formData.imageModel]
  );

  // Handle generate ALL A+ modules: hero pair first, then modules 2+ sequentially
  const handleGenerateAllAplus = useCallback(async () => {
    if (!sessionId) return;

    setIsGeneratingScript(true);
    try {
      // Step 1: Ensure visual script
      await ensureVisualScript(sessionId);
      setIsGeneratingScript(false);

      // Step 2: Generate hero pair (modules 0+1 together)
      setAplusModules((prev) =>
        prev.map((m, idx) =>
          idx === 0 || idx === 1 ? { ...m, status: 'generating' as SlotStatus } : m
        )
      );

      let module1Path: string | undefined;
      try {
        const heroPairResult = await apiClient.generateAplusHeroPair(sessionId, undefined, undefined, formData.imageModel);
        module1Path = heroPairResult.module_1.image_path;

        setAplusModules((prev) =>
          prev.map((m, idx) => {
            if (idx === 0) {
              const newVersions = [...m.versions, {
                imageUrl: heroPairResult.module_0.image_url,
                imagePath: heroPairResult.module_0.image_path,
                promptText: heroPairResult.module_0.prompt_text,
              }];
              return { ...m, status: 'complete' as SlotStatus, versions: newVersions, activeVersionIndex: newVersions.length - 1 };
            }
            if (idx === 1) {
              const newVersions = [...m.versions, {
                imageUrl: heroPairResult.module_1.image_url,
                imagePath: heroPairResult.module_1.image_path,
                promptText: heroPairResult.module_1.prompt_text,
              }];
              return { ...m, status: 'complete' as SlotStatus, versions: newVersions, activeVersionIndex: newVersions.length - 1 };
            }
            return m;
          })
        );
      } catch (err: any) {
        console.error('Hero pair generation failed:', err);
        setAplusModules((prev) =>
          prev.map((m, idx) =>
            idx === 0 || idx === 1
              ? { ...m, status: 'error' as SlotStatus, errorMessage: extractErrorMessage(err, 'Hero pair generation failed') }
              : m
          )
        );
        return; // Stop on hero pair failure
      }

      // Step 3: Generate modules 2+ sequentially, using module 1's path as starting chain
      let prevPath = module1Path;
      for (let i = 2; i < aplusModules.length; i++) {
        setAplusModules((prev) =>
          prev.map((m, idx) =>
            idx === i ? { ...m, status: 'generating' as SlotStatus } : m
          )
        );

        try {
          const result = await apiClient.generateAplusModule({
            session_id: sessionId,
            module_type: 'full_image',
            module_index: i,
            previous_module_path: prevPath,
            image_model: formData.imageModel,
          });

          prevPath = result.image_path;

          setAplusModules((prev) =>
            prev.map((m, idx) => {
              if (idx === i) {
                const newVersions = [...m.versions, {
                  imageUrl: result.image_url,
                  imagePath: result.image_path,
                  promptText: result.prompt_text,
                }];
                return { ...m, status: 'complete' as SlotStatus, versions: newVersions, activeVersionIndex: newVersions.length - 1 };
              }
              if (result.refined_previous && idx === result.refined_previous.module_index) {
                const refined = result.refined_previous;
                const updatedVersions = [...m.versions];
                updatedVersions[m.activeVersionIndex] = {
                  ...updatedVersions[m.activeVersionIndex],
                  imageUrl: refined.image_url + `?t=${Date.now()}`,
                  imagePath: refined.image_path,
                };
                return { ...m, versions: updatedVersions };
              }
              return m;
            })
          );
        } catch (err: any) {
          console.error(`A+ module ${i} generation failed:`, err);
          setAplusModules((prev) =>
            prev.map((m, idx) =>
              idx === i
                ? { ...m, status: 'error' as SlotStatus, errorMessage: extractErrorMessage(err, 'A+ generation failed') }
                : m
            )
          );
          break; // Stop chain on error
        }
      }
    } catch (err: any) {
      console.error('A+ generation failed:', err);
      setIsGeneratingScript(false);
    }
  }, [sessionId, aplusModules, ensureVisualScript, formData.imageModel]);

  // Handle regenerate A+ module
  // For modules 0 or 1: regenerate hero pair (both together)
  // For modules 2+: regenerate individually
  const handleRegenerateAplusModule = useCallback(
    async (moduleIndex: number, note?: string, referenceImagePaths?: string[]) => {
      if (moduleIndex <= 1) {
        // Hero pair — regenerate both 0+1 together
        setAplusModules((prev) =>
          prev.map((m, idx) => {
            if (idx === 0 || idx === 1) {
              return { ...m, status: 'ready' as SlotStatus, errorMessage: undefined };
            }
            return m;
          })
        );
        handleGenerateHeroPair(note, referenceImagePaths);
      } else {
        setAplusModules((prev) =>
          prev.map((m, idx) => {
            if (idx === moduleIndex) {
              return { ...m, status: 'ready' as SlotStatus, errorMessage: undefined };
            }
            return m;
          })
        );
        handleGenerateAplusModule(moduleIndex, note, referenceImagePaths);
      }
    },
    [handleGenerateAplusModule, handleGenerateHeroPair]
  );

  // Handle A+ module version change (browsing through previous versions)
  // Hero pair (modules 0+1) are linked — changing one changes both
  const handleAplusVersionChange = useCallback(
    (moduleIndex: number, versionIndex: number) => {
      setAplusModules((prev) =>
        prev.map((m, idx) => {
          if (idx === moduleIndex) {
            return { ...m, activeVersionIndex: versionIndex };
          }
          // Link hero pair: if changing 0 or 1, also change the other
          if (moduleIndex <= 1 && idx <= 1 && idx !== moduleIndex) {
            // Clamp to valid range for the sibling module
            const clampedIndex = Math.min(versionIndex, m.versions.length - 1);
            return { ...m, activeVersionIndex: Math.max(0, clampedIndex) };
          }
          return m;
        })
      );
    },
    []
  );

  // Handle edit A+ module
  const handleEditAplusModule = useCallback(
    async (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => {
      const currentSessionId = sessionIdRef.current;
      if (!currentSessionId) return;

      // Mark generating
      setAplusModules((prev) =>
        prev.map((m, i) => (i === moduleIndex ? { ...m, status: 'generating' as SlotStatus } : m))
      );

      try {
        const result = await apiClient.editSingleImage(currentSessionId, `aplus_${moduleIndex}`, editInstructions, referenceImagePaths, formData.imageModel);

        // Append new version, advance activeVersionIndex
        setAplusModules((prev) =>
          prev.map((m, i) => {
            if (i !== moduleIndex) return m;
            const newVersion: ImageVersion = {
              imageUrl: result.storage_path
                ? apiClient.getFileUrl(result.storage_path) + `&t=${Date.now()}`
                : m.versions[m.activeVersionIndex]?.imageUrl || '',
              imagePath: result.storage_path,
              timestamp: Date.now(),
            };
            const newVersions = [...m.versions, newVersion];
            return {
              ...m,
              status: (result.status === 'complete' ? 'complete' : 'error') as SlotStatus,
              versions: result.status === 'complete' ? newVersions : m.versions,
              activeVersionIndex: result.status === 'complete' ? newVersions.length - 1 : m.activeVersionIndex,
              errorMessage: result.error_message,
            };
          })
        );
      } catch (err: any) {
        console.error('A+ module edit failed:', err);
        setAplusModules((prev) =>
          prev.map((m, i) =>
            i === moduleIndex
              ? { ...m, status: 'error' as SlotStatus, errorMessage: extractErrorMessage(err, 'Edit failed') }
              : m
          )
        );
      }
    },
    [formData.imageModel]
  );

  // Handle generate mobile A+ module (recompose desktop → mobile 4:3)
  const handleGenerateMobileModule = useCallback(
    async (moduleIndex: number) => {
      const currentSessionId = sessionIdRef.current;
      if (!currentSessionId) return;

      // Mark module mobile status as generating
      setAplusModules((prev) =>
        prev.map((m, i) => (i === moduleIndex ? { ...m, mobileStatus: 'generating' as SlotStatus } : m))
      );

      try {
        const result = await apiClient.generateAplusMobile(currentSessionId, moduleIndex);

        setAplusModules((prev) =>
          prev.map((m, i) => {
            if (i !== moduleIndex) return m;
            const newVersion: ImageVersion = {
              imageUrl: result.image_url,
              imagePath: result.image_path,
              timestamp: Date.now(),
            };
            const newMobileVersions = [...m.mobileVersions, newVersion];
            return {
              ...m,
              mobileStatus: 'complete' as SlotStatus,
              mobileVersions: newMobileVersions,
              mobileActiveVersionIndex: newMobileVersions.length - 1,
            };
          })
        );
      } catch (err: any) {
        console.error('Mobile A+ generation failed:', err);
        setAplusModules((prev) =>
          prev.map((m, i) =>
            i === moduleIndex
              ? { ...m, mobileStatus: 'error' as SlotStatus, errorMessage: extractErrorMessage(err, 'Mobile generation failed') }
              : m
          )
        );
      }
    },
    []
  );

  // Handle generate ALL mobile A+ modules (sequential)
  const handleGenerateAllMobile = useCallback(async () => {
    const currentSessionId = sessionIdRef.current;
    if (!currentSessionId) return;

    for (let i = 0; i < aplusModules.length; i++) {
      const m = aplusModules[i];
      // Only generate mobile for modules that have desktop images but no mobile
      if (m.status !== 'complete' || m.versions.length === 0) continue;
      if (m.mobileVersions.length > 0) continue;
      if (i === 1) continue; // Hero mobile lives on module 0

      // Set generating
      setAplusModules((prev) =>
        prev.map((mod, idx) => (idx === i ? { ...mod, mobileStatus: 'generating' as SlotStatus } : mod))
      );

      try {
        const result = await apiClient.generateAplusMobile(currentSessionId, i);

        setAplusModules((prev) =>
          prev.map((mod, idx) => {
            if (idx !== i) return mod;
            const newVersion: ImageVersion = {
              imageUrl: result.image_url,
              imagePath: result.image_path,
              timestamp: Date.now(),
            };
            const newMobileVersions = [...mod.mobileVersions, newVersion];
            return {
              ...mod,
              mobileStatus: 'complete' as SlotStatus,
              mobileVersions: newMobileVersions,
              mobileActiveVersionIndex: newMobileVersions.length - 1,
            };
          })
        );
      } catch (err: any) {
        console.error(`Mobile A+ module ${i} generation failed:`, err);
        setAplusModules((prev) =>
          prev.map((mod, idx) =>
            idx === i
              ? { ...mod, mobileStatus: 'error' as SlotStatus, errorMessage: extractErrorMessage(err, 'Mobile generation failed') }
              : mod
          )
        );
        // Continue to next module on error (don't break chain)
      }
    }
  }, [aplusModules]);

  // Handle regenerate mobile A+ module
  const handleRegenerateMobileModule = useCallback(
    async (moduleIndex: number, note?: string, _referenceImagePaths?: string[]) => {
      // TODO: pass referenceImagePaths through mobile A+ generation pipeline
      const currentSessionId = sessionIdRef.current;
      if (!currentSessionId) return;

      setAplusModules((prev) =>
        prev.map((m, i) => (i === moduleIndex ? { ...m, mobileStatus: 'generating' as SlotStatus } : m))
      );

      try {
        const result = await apiClient.generateAplusMobile(currentSessionId, moduleIndex, note);

        setAplusModules((prev) =>
          prev.map((m, i) => {
            if (i !== moduleIndex) return m;
            const newVersion: ImageVersion = {
              imageUrl: result.image_url,
              imagePath: result.image_path,
              timestamp: Date.now(),
            };
            const newMobileVersions = [...m.mobileVersions, newVersion];
            return {
              ...m,
              mobileStatus: 'complete' as SlotStatus,
              mobileVersions: newMobileVersions,
              mobileActiveVersionIndex: newMobileVersions.length - 1,
            };
          })
        );
      } catch (err: any) {
        console.error('Mobile A+ regen failed:', err);
        setAplusModules((prev) =>
          prev.map((m, i) =>
            i === moduleIndex
              ? { ...m, mobileStatus: 'error' as SlotStatus, errorMessage: extractErrorMessage(err, 'Mobile regen failed') }
              : m
          )
        );
      }
    },
    []
  );

  // Handle edit mobile A+ module
  const handleEditMobileModule = useCallback(
    async (moduleIndex: number, editInstructions: string, referenceImagePaths?: string[]) => {
      const currentSessionId = sessionIdRef.current;
      if (!currentSessionId) return;

      setAplusModules((prev) =>
        prev.map((m, i) => (i === moduleIndex ? { ...m, mobileStatus: 'generating' as SlotStatus } : m))
      );

      try {
        const result = await apiClient.editAplusMobile(currentSessionId, moduleIndex, editInstructions, referenceImagePaths);

        setAplusModules((prev) =>
          prev.map((m, i) => {
            if (i !== moduleIndex) return m;
            const newVersion: ImageVersion = {
              imageUrl: result.image_url,
              imagePath: result.image_path,
              timestamp: Date.now(),
            };
            const newMobileVersions = [...m.mobileVersions, newVersion];
            return {
              ...m,
              mobileStatus: 'complete' as SlotStatus,
              mobileVersions: newMobileVersions,
              mobileActiveVersionIndex: newMobileVersions.length - 1,
            };
          })
        );
      } catch (err: any) {
        console.error('Mobile A+ edit failed:', err);
        setAplusModules((prev) =>
          prev.map((m, i) =>
            i === moduleIndex
              ? { ...m, mobileStatus: 'error' as SlotStatus, errorMessage: extractErrorMessage(err, 'Mobile edit failed') }
              : m
          )
        );
      }
    },
    []
  );

  // Handle cancel A+ module generation (client-side, viewport-aware)
  const handleCancelAplusModule = useCallback((moduleIndex: number, viewport: 'desktop' | 'mobile') => {
    setAplusModules((prev) =>
      prev.map((m, idx) => {
        if (idx !== moduleIndex) return m;
        if (viewport === 'mobile' && m.mobileStatus === 'generating') {
          return { ...m, mobileStatus: 'error' as SlotStatus, errorMessage: 'Cancelled by user' };
        }
        if (viewport === 'desktop' && m.status === 'generating') {
          return { ...m, status: 'error' as SlotStatus, errorMessage: 'Cancelled by user' };
        }
        return m;
      })
    );
  }, []);

  // Handle A+ viewport-aware version change
  const handleAplusViewportVersionChange = useCallback(
    (moduleIndex: number, versionIndex: number) => {
      if (aplusViewportMode === 'mobile') {
        setAplusModules((prev) =>
          prev.map((m, idx) =>
            idx === moduleIndex ? { ...m, mobileActiveVersionIndex: versionIndex } : m
          )
        );
      } else {
        handleAplusVersionChange(moduleIndex, versionIndex);
      }
    },
    [aplusViewportMode, handleAplusVersionChange]
  );

  // Handle listing version navigation
  const handleListingVersionChange = useCallback((imageType: string, index: number) => {
    setListingVersions(prev => ({
      ...prev, [imageType]: { ...prev[imageType], activeIndex: index }
    }));
  }, []);

  // Handle start over
  const handleStartOver = useCallback(() => {
    setUploads([]);
    setFormData(initialFormData);
    setFrameworks([]);
    setSelectedFramework(null);
    setProductAnalysis('');
    setProductAnalysisRaw(null);
    updateSessionId(null);
    setGenerationStatus('pending');
    setImages([]);
    setIsAnalyzing(false);
    setIsGenerating(false);
    setLogoPath(null);
    setOriginalStyleRefPath(null);
    setUseOriginalStyleRef(false);
    setError(null);
    setExpandedSections(['photos', 'product']);
    // Clear session from URL
    setSearchParams({}, { replace: true });
    // Reset listing versions
    setListingVersions({});
    // Reset A+ modules and visual script
    setAplusVisualScript(null);
    setIsGeneratingScript(false);
    setAplusModules(
      Array.from({ length: 6 }, (_, i) => ({
        id: `aplus-${i + 1}`,
        type: 'full_image' as const,
        index: i,
        status: 'ready' as SlotStatus,
        versions: [],
        activeVersionIndex: 0,
        mobileVersions: [],
        mobileActiveVersionIndex: 0,
        mobileStatus: 'ready' as SlotStatus,
      }))
    );
    setAplusViewportMode('desktop');
  }, []);

  const isGeminiConfigured = health?.dependencies?.gemini === 'configured';

  // Build available reference images for focus-image picker in edit panels
  const availableReferenceImages = useMemo<ReferenceImage[]>(() => {
    const refs: ReferenceImage[] = [];
    uploads.forEach((u, i) => {
      refs.push({
        path: u.file_path,
        url: u.preview_url,
        label: i === 0 ? 'Product' : `Photo ${i + 1}`,
      });
    });
    if (originalStyleRefPath) {
      refs.push({
        path: originalStyleRefPath,
        url: apiClient.getFileUrl(originalStyleRefPath),
        label: 'Style Ref',
      });
    } else if (formData.styleReferencePreview) {
      // Style ref uploaded but path not yet stored — use preview as placeholder
      // (the path gets set after framework analysis)
    }
    if (logoPath) {
      refs.push({
        path: logoPath,
        url: apiClient.getFileUrl(logoPath),
        label: 'Logo',
      });
    }
    return refs;
  }, [uploads, originalStyleRefPath, formData.styleReferencePreview, logoPath]);

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
            useOriginalStyleRef={useOriginalStyleRef}
            onToggleOriginalStyleRef={setUseOriginalStyleRef}
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
            isAnalyzing={isAnalyzing}
            sessionId={sessionId || undefined}
            images={images}
            aplusModules={aplusModules}
            aplusVisualScript={aplusVisualScript}
            isGeneratingScript={isGeneratingScript}
            onGenerateAplusModule={handleGenerateAplusModule}
            onRegenerateAplusModule={handleRegenerateAplusModule}
            onGenerateAllAplus={handleGenerateAllAplus}
            onRegenerateScript={regenerateVisualScript}
            onAplusVersionChange={handleAplusViewportVersionChange}
            onEditAplusModule={handleEditAplusModule}
            aplusViewportMode={aplusViewportMode}
            onAplusViewportChange={setAplusViewportMode}
            onGenerateMobileModule={handleGenerateMobileModule}
            onGenerateAllMobile={handleGenerateAllMobile}
            onRegenerateMobileModule={handleRegenerateMobileModule}
            onEditMobileModule={handleEditMobileModule}
            onCancelAplusModule={handleCancelAplusModule}
            listingVersions={listingVersions}
            onListingVersionChange={handleListingVersionChange}
            onGenerateSingle={handleGenerateSingle}
            onGenerateAll={handleGenerate}
            onRegenerateSingle={handleRegenerateSingle}
            onEditSingle={handleEditSingle}
            onCancelGeneration={handleCancelGeneration}
            availableReferenceImages={availableReferenceImages}
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
