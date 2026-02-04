import axios, { AxiosInstance } from 'axios';
import { supabase } from '../lib/supabase';
import type {
  HealthResponse,
  UploadResponse,
  GenerationRequest,
  GenerationResponse,
  SessionStatusResponse,
  SessionImagesResponse,
  StylePreset,
  StylePreviewRequest,
  StylePreviewResponse,
  FrameworkGenerationRequest,
  FrameworkGenerationResponse,
  DesignFramework,
  PromptHistory,
  ProjectListResponse,
  ProjectDetailResponse,
  AplusModuleRequest,
  AplusModuleResponse,
  AplusVisualScriptResponse,
  HeroPairResponse,
} from './types';

// In production, use VITE_API_URL; in development, use relative /api (proxied by Vite)
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: 120000, // 2 minute timeout for generation
      headers: {
        'Content-Type': 'application/json',
      }
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      async (config) => {
        try {
          const { data: { session } } = await supabase.auth.getSession();
          if (session?.access_token) {
            config.headers.Authorization = `Bearer ${session.access_token}`;
          }
        } catch (error) {
          console.warn('Failed to get auth session:', error);
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          console.error('Unauthorized - redirecting to login');
          window.location.href = '/login';
        }
        if (error.response?.status === 500) {
          console.error('Server error:', error.response.data);
        }
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async health(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  // Upload product image
  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<UploadResponse>('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Delete uploaded image
  async deleteUpload(uploadId: string): Promise<void> {
    await this.client.delete(`/upload/${uploadId}`);
  }

  // Start image generation
  async startGeneration(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await this.client.post<GenerationResponse>('/generate/', request);
    return response.data;
  }

  // Start async generation (returns immediately)
  async startGenerationAsync(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await this.client.post<GenerationResponse>('/generate/async', request);
    return response.data;
  }

  // Get generation session status
  async getGenerationStatus(sessionId: string): Promise<SessionStatusResponse> {
    const response = await this.client.get<SessionStatusResponse>(`/generate/${sessionId}`);
    return response.data;
  }

  // Get session images
  async getSessionImages(sessionId: string): Promise<SessionImagesResponse> {
    const response = await this.client.get<SessionImagesResponse>(`/images/${sessionId}`, {
      timeout: 30000, // 30 second timeout for status polling (quick call)
    });
    return response.data;
  }

  // Retry failed images
  async retryFailedImages(sessionId: string): Promise<GenerationResponse> {
    const response = await this.client.post<GenerationResponse>(`/generate/${sessionId}/retry`);
    return response.data;
  }

  // Regenerate a single image with optional note
  async regenerateSingleImage(
    sessionId: string,
    imageType: string,
    note?: string,
    referenceImagePaths?: string[],
    imageModel?: string
  ): Promise<{ status: string; image_type: string; storage_path?: string; error_message?: string }> {
    const response = await this.client.post(
      '/generate/single',
      {
        session_id: sessionId,
        image_type: imageType,
        note: note,
        reference_image_paths: referenceImagePaths || null,
        image_model: imageModel || null,
      },
      { timeout: 180000 } // 3 minute timeout for single image
    );
    return response.data;
  }

  // Edit an existing generated image (modifies in place instead of regenerating from scratch)
  async editSingleImage(
    sessionId: string,
    imageType: string,
    editInstructions: string,
    referenceImagePaths?: string[],
    imageModel?: string
  ): Promise<{ status: string; image_type: string; storage_path?: string; error_message?: string }> {
    const response = await this.client.post(
      '/generate/edit',
      {
        session_id: sessionId,
        image_type: imageType,
        edit_instructions: editInstructions,
        reference_image_paths: referenceImagePaths || null,
        image_model: imageModel || null,
      },
      { timeout: 180000 } // 3 minute timeout for edit
    );
    return response.data;
  }

  // Get all prompts for a session
  async getSessionPrompts(sessionId: string): Promise<PromptHistory[]> {
    const response = await this.client.get<PromptHistory[]>(
      `/generate/${sessionId}/prompts`
    );
    return response.data;
  }

  // Get a prompt for a specific image type, optionally by version number (1-based)
  async getImagePrompt(sessionId: string, imageType: string, version?: number): Promise<PromptHistory> {
    const params = version != null ? { version } : {};
    const response = await this.client.get<PromptHistory>(
      `/generate/${sessionId}/prompts/${imageType}`,
      { params }
    );
    return response.data;
  }

  // Get image URL
  getImageUrl(sessionId: string, imageType: string): string {
    return `${API_BASE}/images/${sessionId}/${imageType}`;
  }

  // Get upload preview URL
  getUploadPreviewUrl(uploadId: string): string {
    return `${API_BASE}/images/upload/${uploadId}`;
  }

  // Get signed URL for a storage path (supabase:// or upload path)
  getFileUrl(storagePath: string): string {
    return `${API_BASE}/images/file?path=${encodeURIComponent(storagePath)}`;
  }

  // Get available style presets
  async getStyles(): Promise<StylePreset[]> {
    const response = await this.client.get<StylePreset[]>('/generate/styles/list');
    return response.data;
  }

  // Generate style previews
  async generateStylePreviews(request: StylePreviewRequest): Promise<StylePreviewResponse> {
    const response = await this.client.post<StylePreviewResponse>(
      '/generate/styles/preview',
      request,
      { timeout: 300000 } // 5 minute timeout for style previews
    );
    return response.data;
  }

  // Select a style for the session
  async selectStyle(sessionId: string, styleId: string): Promise<void> {
    await this.client.post('/generate/styles/select', {
      session_id: sessionId,
      style_id: styleId,
    });
  }

  // Generate all images with selected style
  async generateWithStyle(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await this.client.post<GenerationResponse>(
      '/generate/styles/generate-all',
      request,
      { timeout: 600000 } // 10 minute timeout for full generation
    );
    return response.data;
  }

  // ============================================================================
  // MASTER LEVEL: Principal Designer AI - Framework Generation
  // ============================================================================

  // Analyze product image and generate 4 dynamic design frameworks
  async analyzeFrameworks(request: FrameworkGenerationRequest): Promise<FrameworkGenerationResponse> {
    // Ensure arrays are never undefined
    const payload = {
      ...request,
      additional_upload_paths: request.additional_upload_paths || [],
      features: request.features || [],
      // Ensure color_mode defaults to 'ai_decides' if not provided
      color_mode: request.color_mode || 'ai_decides',
      locked_colors: request.locked_colors || [],
      // Include style reference if provided (for color extraction)
      style_reference_path: request.style_reference_path || null,
    };

    // Debug logging for color mode
    console.log('[API Client] analyzeFrameworks payload:');
    console.log('[API Client]   color_mode:', payload.color_mode);
    console.log('[API Client]   locked_colors:', payload.locked_colors);
    console.log('[API Client]   primary_color:', payload.primary_color);
    console.log('[API Client]   style_reference_path:', payload.style_reference_path);
    console.log('[API Client]   skip_preview_generation:', payload.skip_preview_generation);

    const response = await this.client.post<FrameworkGenerationResponse>(
      '/generate/frameworks/analyze',
      payload,
      { timeout: 180000 } // 3 minute timeout for GPT-4o Vision analysis
    );
    return response.data;
  }

  // Generate all images using a selected framework
  // This is a TWO-STEP process:
  // 1. First generates 5 detailed image prompts via GPT-4o (for radically different image types)
  // 2. Then generates all 5 images using those prompts
  async generateWithFramework(
    request: GenerationRequest,
    framework: DesignFramework,
    productAnalysis?: Record<string, unknown>,  // AI's analysis for regeneration context
    singleImageType?: string,  // Optional: generate only this image type (for clicking individual slots)
    createOnly?: boolean,  // Optional: just create session, no generation
    imageModel?: string  // Optional: override AI model
  ): Promise<GenerationResponse> {
    // Build request payload, ensuring arrays are never undefined
    const payload: Record<string, unknown> = {
      product_title: request.product_title,
      upload_path: request.upload_path,
      additional_upload_paths: request.additional_upload_paths || [],
      framework: framework,
      brand_name: request.brand_name || null,
      features: [request.feature_1, request.feature_2, request.feature_3].filter(Boolean),
      target_audience: request.target_audience || null,
      logo_path: request.logo_path || null,
      style_reference_path: request.style_reference_path || null,
      // Track original style ref separately so it can be restored on project load
      original_style_reference_path: request.original_style_reference_path || null,
      global_note: request.global_note || null,
      // Include product_analysis for regeneration context
      product_analysis: productAnalysis || null,
      // AI model override
      image_model: imageModel || null,
    };

    // If single_image_type is provided, only generate that one image
    if (singleImageType) {
      payload.single_image_type = singleImageType;
    }

    // If create_only, just create session without generating
    if (createOnly) {
      payload.create_only = true;
    }

    const response = await this.client.post<GenerationResponse>(
      '/generate/frameworks/generate',  // New endpoint that generates prompts first
      payload,
      { timeout: 600000 } // 10 minute timeout for prompt generation + image generation
    );
    return response.data;
  }

  // ============================================================================
  // Projects - User's generation session history
  // ============================================================================

  // List user's projects with pagination
  async listProjects(
    page: number = 1,
    pageSize: number = 12,
    statusFilter?: string
  ): Promise<ProjectListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (statusFilter && statusFilter !== 'all') {
      params.append('status_filter', statusFilter);
    }
    const response = await this.client.get<ProjectListResponse>(
      `/projects/?${params.toString()}`
    );
    return response.data;
  }

  // Get project detail with all images
  async getProjectDetail(sessionId: string): Promise<ProjectDetailResponse> {
    const response = await this.client.get<ProjectDetailResponse>(
      `/projects/${sessionId}`
    );
    return response.data;
  }

  // Rename a project
  async renameProject(sessionId: string, newTitle: string): Promise<void> {
    await this.client.patch(`/projects/${sessionId}`, {
      new_title: newTitle,
    });
  }

  // Delete a project
  async deleteProject(sessionId: string): Promise<void> {
    await this.client.delete(`/projects/${sessionId}`);
  }

  // ============================================================================
  // A+ Content Module Generation
  // ============================================================================

  /**
   * Generate a single A+ Content module image.
   * For sequential/chained generation, pass the previous module's image_path
   * to maintain visual design continuity.
   */
  async generateAplusModule(request: AplusModuleRequest): Promise<AplusModuleResponse> {
    const response = await this.client.post<AplusModuleResponse>(
      '/generate/aplus/generate',
      request,
      { timeout: 300000 } // 5 minute timeout per module (canvas continuity is slow)
    );
    return response.data;
  }

  /**
   * Generate the A+ hero pair (modules 0+1) as a single tall image split in half.
   * Both halves come from the same image — guaranteed perfect alignment.
   */
  async generateAplusHeroPair(
    sessionId: string,
    customInstructions?: string,
    referenceImagePaths?: string[],
    imageModel?: string,
  ): Promise<HeroPairResponse> {
    const response = await this.client.post<HeroPairResponse>(
      '/generate/aplus/hero-pair',
      {
        session_id: sessionId,
        custom_instructions: customInstructions,
        reference_image_paths: referenceImagePaths || null,
        image_model: imageModel || null,
      },
      { timeout: 300000 } // 5 minute timeout for hero pair (tall image + split)
    );
    return response.data;
  }

  /**
   * Generate Art Director visual script that plans the entire A+ section
   * as one unified visual narrative.
   */
  async generateAplusVisualScript(
    sessionId: string,
    moduleCount: number = 6
  ): Promise<AplusVisualScriptResponse> {
    const response = await this.client.post<AplusVisualScriptResponse>(
      '/generate/aplus/visual-script',
      { session_id: sessionId, module_count: moduleCount },
      { timeout: 60000 } // 1 minute timeout for text generation
    );
    return response.data;
  }

  /**
   * Get stored visual script for a session.
   */
  async getAplusVisualScript(sessionId: string): Promise<AplusVisualScriptResponse> {
    const response = await this.client.get<AplusVisualScriptResponse>(
      `/generate/aplus/${sessionId}/visual-script`
    );
    return response.data;
  }

  // A+ prompts use the same system as listing images.
  // Use getImagePrompt(sessionId, 'aplus_0') through 'aplus_4' to retrieve them.

  /**
   * Generate a mobile-optimized version of an A+ module using Gemini edit API.
   * Recomposes the desktop image (1464x600) into mobile format (600x450, 4:3).
   */
  async generateAplusMobile(
    sessionId: string,
    moduleIndex: number,
    customInstructions?: string
  ): Promise<{ image_path: string; image_url: string; module_index: number }> {
    const response = await this.client.post(
      '/generate/aplus/generate-mobile',
      {
        session_id: sessionId,
        module_index: moduleIndex,
        custom_instructions: customInstructions,
      },
      { timeout: 300000 } // 5 minute timeout for mobile transform
    );
    return response.data;
  }

  /**
   * Generate mobile versions for all A+ modules that have desktop images.
   */
  async generateAllAplusMobile(
    sessionId: string
  ): Promise<Array<{ module_index: number; image_path: string; image_url: string; status: string }>> {
    const response = await this.client.post(
      '/generate/aplus/generate-all-mobile',
      { session_id: sessionId },
      { timeout: 600000 }
    );
    return response.data;
  }

  /**
   * Edit a mobile A+ module image with specific instructions.
   */
  async editAplusMobile(
    sessionId: string,
    moduleIndex: number,
    editInstructions: string,
    referenceImagePaths?: string[]
  ): Promise<{ image_path: string; image_url: string; module_index: number }> {
    const response = await this.client.post(
      '/generate/edit',
      {
        session_id: sessionId,
        image_type: `aplus_${moduleIndex}`,
        edit_instructions: editInstructions,
        mobile: true,
        reference_image_paths: referenceImagePaths || null,
      },
      { timeout: 180000 }
    );
    // Normalize response to match mobile format
    return {
      image_path: response.data.storage_path,
      image_url: response.data.storage_path
        ? `/api/images/file?path=${encodeURIComponent(response.data.storage_path)}`
        : '',
      module_index: moduleIndex,
    };
  }
}

export const apiClient = new ApiClient();
