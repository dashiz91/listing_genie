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
  ReplanResponse,
  HeroPairResponse,
  AmazonAuthStatus,
  AmazonAuthUrlResponse,
  AmazonDisconnectResponse,
  AmazonPushResponse,
  AmazonPushStatusResponse,
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

  /**
   * Re-plan all prompts (listing images + A+ visual script) without regenerating
   * the framework itself. Keeps the same style/colors but creates fresh prompts.
   */
  async replanAll(
    sessionId: string,
    moduleCount: number = 6
  ): Promise<ReplanResponse> {
    const response = await this.client.post<ReplanResponse>(
      '/generate/replan',
      { session_id: sessionId, module_count: moduleCount },
      { timeout: 120000 } // 2 minute timeout for both prompts
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

  // ============================================================================
  // Assets - User's uploaded and generated assets
  // ============================================================================

  /**
   * List user's assets by category (logos, style-refs, products, generated, or all)
   */
  async listAssets(
    assetType: 'logos' | 'style-refs' | 'products' | 'generated' | 'all' = 'all'
  ): Promise<{ assets: AssetItem[]; total: number }> {
    const response = await this.client.get<{ assets: AssetItem[]; total: number }>(
      `/assets/?asset_type=${assetType}`
    );
    return response.data;
  }

  // ============================================================================
  // Settings - User preferences and brand presets
  // ============================================================================

  /**
   * Get all user settings including brand presets and usage stats
   */
  async getSettings(): Promise<UserSettings> {
    const response = await this.client.get<UserSettings>('/settings/');
    return response.data;
  }

  /**
   * Get just the brand presets for auto-filling new projects
   */
  async getBrandPresets(): Promise<BrandPresets> {
    const response = await this.client.get<BrandPresets>('/settings/brand-presets');
    return response.data;
  }

  /**
   * Update brand presets
   */
  async updateBrandPresets(updates: Partial<{
    default_brand_name: string | null;
    default_brand_colors: string[];
    default_logo_path: string | null;
    default_style_reference_path: string | null;
  }>): Promise<BrandPresets> {
    const response = await this.client.patch<BrandPresets>('/settings/brand-presets', updates);
    return response.data;
  }

  /**
   * Get usage stats
   */
  async getUsageStats(): Promise<UsageStats> {
    const response = await this.client.get<UsageStats>('/settings/usage');
    return response.data;
  }

  /**
   * Get current credits balance and plan info
   */
  async getCredits(): Promise<CreditsInfo> {
    const response = await this.client.get<CreditsInfo>('/settings/credits');
    return response.data;
  }

  /**
   * Get all available plans
   */
  async getPlans(): Promise<PlansResponse> {
    const response = await this.client.get<PlansResponse>('/settings/plans');
    return response.data;
  }

  /**
   * Estimate credit cost for an operation
   */
  async estimateCost(
    operation: string,
    model: string = 'gemini-3-pro-image-preview',
    count: number = 1
  ): Promise<CostEstimate> {
    const response = await this.client.post<CostEstimate>('/settings/credits/estimate', {
      operation,
      model,
      count,
    });
    return response.data;
  }

  /**
   * Get model credit costs
   */
  async getModelCosts(): Promise<ModelCosts> {
    const response = await this.client.get<ModelCosts>('/settings/credits/model-costs');
    return response.data;
  }

  // ============================================================================
  // ASIN Import - Auto-fill form from Amazon product
  // ============================================================================

  /**
   * Import product data from Amazon by ASIN
   */
  async importFromAsin(
    asin: string,
    options: {
      marketplace?: string;
      downloadImages?: boolean;
      maxImages?: number;
    } = {}
  ): Promise<ASINImportResponse> {
    const response = await this.client.post<ASINImportResponse>('/asin/import', {
      asin,
      marketplace: options.marketplace || 'com',
      download_images: options.downloadImages ?? true,
      max_images: options.maxImages || 3,
    });
    return response.data;
  }

  /**
   * Validate ASIN format
   */
  async validateAsin(asin: string): Promise<{ valid: boolean; asin?: string; error?: string }> {
    const response = await this.client.get(`/asin/validate/${encodeURIComponent(asin)}`);
    return response.data;
  }

  // ============================================================================
  // Admin - Credit management (admin only)
  // ============================================================================

  /**
   * Adjust a user's credits by email (admin only)
   */
  async adjustUserCredits(
    email: string,
    amount: number,
    reason: string = ''
  ): Promise<CreditAdjustmentResponse> {
    const response = await this.client.post<CreditAdjustmentResponse>('/admin/credits/adjust', {
      email,
      amount,
      reason,
    });
    return response.data;
  }

  /**
   * Search users by email (admin only)
   */
  async searchUsers(email?: string): Promise<UserSearchResponse> {
    const params = email ? `?email=${encodeURIComponent(email)}` : '';
    const response = await this.client.get<UserSearchResponse>(`/admin/users/search${params}`);
    return response.data;
  }

  /**
   * Get a specific user's credits by user_id (admin only)
   */
  async getUserCredits(userId: string): Promise<AdminUserCredits> {
    const response = await this.client.get<AdminUserCredits>(`/admin/users/${userId}/credits`);
    return response.data;
  }

  // ============================================================================
  // Amazon Seller Central Push
  // ============================================================================

  /**
   * Check if the current user has connected their Amazon Seller Central account.
   */
  async getAmazonAuthStatus(): Promise<AmazonAuthStatus> {
    const response = await this.client.get<AmazonAuthStatus>('/amazon/auth/status');
    return response.data;
  }

  /**
   * Get the Amazon OAuth authorization URL to redirect the seller to.
   */
  async getAmazonAuthUrl(marketplaceId?: string): Promise<AmazonAuthUrlResponse> {
    const response = await this.client.post<AmazonAuthUrlResponse>('/amazon/auth/url', {
      marketplace_id: marketplaceId,
    });
    return response.data;
  }

  /**
   * Disconnect the user's Amazon Seller Central account.
   */
  async disconnectAmazon(): Promise<AmazonDisconnectResponse> {
    const response = await this.client.delete<AmazonDisconnectResponse>('/amazon/auth/disconnect');
    return response.data;
  }

  /**
   * Push listing images to Amazon Seller Central for a given ASIN/SKU.
   */
  async pushListingImages(
    sessionId: string,
    asin: string,
    sku: string,
    options?: { marketplaceId?: string; imagePaths?: string[] }
  ): Promise<AmazonPushResponse> {
    const response = await this.client.post<AmazonPushResponse>('/amazon/push/listing-images', {
      session_id: sessionId,
      asin,
      sku,
      marketplace_id: options?.marketplaceId,
      image_paths: options?.imagePaths,
    });
    return response.data;
  }

  /**
   * Get the status of an Amazon push job.
   */
  async getAmazonPushStatus(jobId: string): Promise<AmazonPushStatusResponse> {
    const response = await this.client.get<AmazonPushStatusResponse>(
      `/amazon/push/status/${jobId}`
    );
    return response.data;
  }

  // Alt text generation
  async generateAltText(sessionId: string, imageType: string): Promise<AltTextResponse> {
    const response = await this.client.post<AltTextResponse>('/generate/alt-text', {
      session_id: sessionId,
      image_type: imageType,
    });
    return response.data;
  }

  async generateAltTextBatch(sessionId: string): Promise<AltTextBatchResponse> {
    const response = await this.client.post<AltTextBatchResponse>(
      `/generate/alt-text/batch?session_id=${sessionId}`
    );
    return response.data;
  }
}

// ASIN Import types
export interface ASINImportResponse {
  asin: string;
  title: string | null;
  brand_name: string | null;
  feature_1: string | null;
  feature_2: string | null;
  feature_3: string | null;
  category: string | null;
  image_uploads: Array<{ upload_id: string; file_path: string }>;
  source_image_urls: string[];
}

// Asset item type
export interface AssetItem {
  id: string;
  name: string;
  url: string;
  type: 'logos' | 'style-refs' | 'products' | 'generated';
  created_at: string;
  session_id?: string;
  image_type?: string;
}

// Settings types
export interface BrandPresets {
  default_brand_name: string | null;
  default_brand_colors: string[];
  default_logo_path: string | null;
  default_logo_url: string | null;
  default_style_reference_path: string | null;
  default_style_reference_url: string | null;
}

export interface UsageStats {
  images_generated_total: number;
  images_generated_this_month: number;
  projects_count: number;
  last_generation_at: string | null;
  credits_balance: number;
  plan_tier: string;
}

export interface UserSettings {
  brand_presets: BrandPresets;
  usage: UsageStats;
  email: string;
}

// Credits types
export interface CreditsInfo {
  balance: number;
  plan_tier: string;
  plan_name: string;
  credits_per_period: number;
  period: string;
  is_admin: boolean;  // Admin users have unlimited credits
}

export interface PlanInfo {
  id: string;
  name: string;
  price: number;
  credits_per_period: number;
  period: string;
  features: string[];
}

export interface PlansResponse {
  plans: PlanInfo[];
  current_plan: string;
}

export interface CostEstimate {
  total: number;
  breakdown: Record<string, number>;
  can_afford: boolean;
  current_balance: number;
}

export interface ModelCosts {
  models: Record<string, { name: string; cost: number; description: string }>;
  operations: Record<string, { cost: number; description: string }>;
}

// Admin types
export interface CreditAdjustmentResponse {
  success: boolean;
  email: string;
  previous_balance: number;
  new_balance: number;
  amount_adjusted: number;
  reason: string;
}

export interface AdminUserSearchResult {
  email: string;
  user_id: string;
  credits_balance: number;
  plan_tier: string;
}

export interface UserSearchResponse {
  users: AdminUserSearchResult[];
  total: number;
}

export interface AdminUserCredits {
  user_id: string;
  email: string | null;
  credits_balance: number;
  plan_tier: string;
}

// Alt text types
export interface AltTextResponse {
  image_type: string;
  alt_text: string;
  character_count: number;
}

export interface AltTextBatchResponse {
  session_id: string;
  alt_texts: Record<string, { alt_text: string; character_count: number }>;
}

export const apiClient = new ApiClient();
