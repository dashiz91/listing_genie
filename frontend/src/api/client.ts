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
} from './types';

const API_BASE = '/api';

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
    note?: string
  ): Promise<{ status: string; image_type: string; storage_path?: string; error_message?: string }> {
    const response = await this.client.post(
      '/generate/single',
      {
        session_id: sessionId,
        image_type: imageType,
        note: note,
      },
      { timeout: 180000 } // 3 minute timeout for single image
    );
    return response.data;
  }

  // Edit an existing generated image (modifies in place instead of regenerating from scratch)
  async editSingleImage(
    sessionId: string,
    imageType: string,
    editInstructions: string
  ): Promise<{ status: string; image_type: string; storage_path?: string; error_message?: string }> {
    const response = await this.client.post(
      '/generate/edit',
      {
        session_id: sessionId,
        image_type: imageType,
        edit_instructions: editInstructions,
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

  // Get the latest prompt for a specific image type
  async getImagePrompt(sessionId: string, imageType: string): Promise<PromptHistory> {
    const response = await this.client.get<PromptHistory>(
      `/generate/${sessionId}/prompts/${imageType}`
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
    productAnalysis?: Record<string, unknown>  // AI's analysis for regeneration context
  ): Promise<GenerationResponse> {
    // Build request payload, ensuring arrays are never undefined
    const payload = {
      product_title: request.product_title,
      upload_path: request.upload_path,
      additional_upload_paths: request.additional_upload_paths || [],
      framework: framework,
      brand_name: request.brand_name || null,
      features: [request.feature_1, request.feature_2, request.feature_3].filter(Boolean),
      target_audience: request.target_audience || null,
      logo_path: request.logo_path || null,
      style_reference_path: request.style_reference_path || null,
      global_note: request.global_note || null,
      // Include product_analysis for regeneration context
      product_analysis: productAnalysis || null,
    };

    const response = await this.client.post<GenerationResponse>(
      '/generate/frameworks/generate',  // New endpoint that generates prompts first
      payload,
      { timeout: 600000 } // 10 minute timeout for prompt generation + image generation
    );
    return response.data;
  }
}

export const apiClient = new ApiClient();
