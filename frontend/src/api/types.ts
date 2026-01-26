export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment?: string;
  dependencies: {
    database: string;
    storage: string;
    gemini: string;
  };
}

export interface ProductInfo {
  title: string;
  features: [string, string, string];
  targetAudience: string;
}

export type ImageType = 'main' | 'infographic_1' | 'infographic_2' | 'lifestyle' | 'comparison';
export type GenerationStatus = 'pending' | 'processing' | 'complete' | 'partial' | 'failed';

export interface KeywordInput {
  keyword: string;
  intents: string[];
}

// ============================================================================
// MASTER LEVEL: Design Framework Types
// ============================================================================

export interface ColorSpec {
  hex: string;
  name: string;
  role: 'primary' | 'secondary' | 'accent' | 'text_dark' | 'text_light';
  usage: string;
}

export interface TypographySpec {
  headline_font: string;
  headline_weight: string;
  headline_size: string;
  subhead_font: string;
  subhead_weight: string;
  subhead_size: string;
  body_font: string;
  body_weight: string;
  body_size: string;
  letter_spacing: string;
}

export interface StoryArc {
  theme: string;
  hook: string;
  reveal: string;
  proof: string;
  dream: string;
  close: string;
}

export interface ImageCopy {
  image_number: number;
  image_type: string;
  headline: string;
  subhead?: string;
  feature_callouts: string[];
  cta?: string;
}

export interface LayoutSpec {
  composition_style: string;
  whitespace_philosophy: string;
  product_prominence: string;
  text_placement: string;
  visual_flow: string;
}

export interface VisualTreatment {
  lighting_style: string;
  shadow_spec: string;
  background_treatment: string;
  texture: string;
  mood_keywords: string[];
}

export interface DesignFramework {
  framework_id: string;
  framework_name: string;
  framework_type?: string;
  design_philosophy: string;
  colors: ColorSpec[];
  typography: TypographySpec;
  story_arc: StoryArc;
  image_copy: ImageCopy[];
  brand_voice: string;
  layout: LayoutSpec;
  visual_treatment: VisualTreatment;
  rationale: string;
  target_appeal: string;
  // Preview image generated for this framework
  preview_url?: string;
  preview_path?: string;
}

// Color Mode - controls how AI Designer handles colors
export type ColorMode = 'ai_decides' | 'suggest_primary' | 'locked_palette';

export interface FrameworkGenerationRequest {
  product_title: string;
  upload_path: string;
  // Additional product images for better AI context
  additional_upload_paths?: string[];
  brand_name?: string;
  features?: string[];
  target_audience?: string;
  primary_color?: string;
  // Color mode - how AI should handle colors
  color_mode?: ColorMode;
  // Locked colors (when color_mode is 'locked_palette')
  locked_colors?: string[];
  // Style reference image - AI extracts colors/style from this
  style_reference_path?: string;
}

export interface FrameworkGenerationResponse {
  session_id: string;
  product_analysis: string;  // Summary text for display
  product_analysis_raw?: Record<string, unknown>;  // Full analysis dict for regeneration context
  frameworks: DesignFramework[];
  generation_notes: string;
}

// Legacy brand vibes (kept for backwards compatibility)
export type BrandVibe =
  | 'premium_luxury'    // Elegant, exclusive, aspirational
  | 'clean_modern'      // Minimal, tech, sophisticated
  | 'bold_energetic'    // Dynamic, confident, action
  | 'natural_organic'   // Earthy, authentic, wholesome
  | 'playful_fun'       // Vibrant, youthful, joyful
  | 'clinical_trust';   // Professional, scientific, reliable

export interface GenerationRequest {
  product_title: string;
  feature_1?: string;
  feature_2?: string;
  feature_3?: string;
  target_audience?: string;
  keywords: KeywordInput[];
  upload_path: string;
  // Additional product images for better AI context
  additional_upload_paths?: string[];
  brand_name?: string;
  brand_colors?: string[];
  logo_path?: string;
  style_id?: string;  // Legacy
  // MASTER Level: Brand vibe - drives the entire creative brief
  brand_vibe?: BrandVibe;
  primary_color?: string;
  // Style reference image - AI matches this visual style
  style_reference_path?: string;
  // Color palette options
  color_count?: number;
  color_palette?: string[];
  // Global note/instructions applied to all image generations
  global_note?: string;
}

export interface RegenerateSingleRequest {
  session_id: string;
  image_type: ImageType;
  note?: string;  // Optional note/instructions for this specific regeneration
}

export interface StylePreset {
  id: string;
  name: string;
  description: string;
  color_palette: string[];
  mood: string;
}

export interface StylePreviewRequest {
  product_title: string;
  feature_1?: string;
  upload_path: string;
  logo_path?: string;
  brand_colors?: string[];
  style_ids?: string[];
  // Style reference image - AI matches this visual style
  style_reference_path?: string;
  // Color palette options
  color_count?: number;
  color_palette?: string[];
}

export interface StylePreviewResult {
  style_id: string;
  style_name: string;
  status: GenerationStatus;
  image_url?: string;
  error_message?: string;
}

export interface StylePreviewResponse {
  session_id: string;
  previews: StylePreviewResult[];
}

export interface ImageResult {
  image_type: ImageType;
  status: GenerationStatus;
  storage_path?: string;
  error_message?: string;
}

export interface GenerationResponse {
  session_id: string;
  status: GenerationStatus;
  images: ImageResult[];
}

export interface SessionStatusResponse {
  session_id: string;
  status: GenerationStatus;
  product_title: string;
  created_at: string;
  completed_at?: string;
  images: ImageResult[];
}

export interface UploadResponse {
  upload_id: string;
  file_path: string;
  filename: string;
  size: number;
}

export interface SessionImage {
  type: ImageType;
  status: GenerationStatus;
  label: string;
  url?: string;
  error?: string;
}

export interface SessionImagesResponse {
  session_id: string;
  status: GenerationStatus;
  images: SessionImage[];
}

export interface GenerationSession {
  id: string;
  status: GenerationStatus;
  created_at: string;
  completed_at?: string;
}

export interface ImageRecord {
  id: number;
  image_type: ImageType;
  status: GenerationStatus;
  storage_path?: string;
}

// Prompt History - for viewing prompts sent to AI
export interface PromptHistory {
  image_type: string;
  version: number;
  prompt_text: string;
  user_feedback?: string;
  change_summary?: string;
  created_at: string;
  // Reference images used for generation
  reference_images: Array<{
    type: string;  // "primary", "additional_1", "style_reference", "logo"
    path: string;
  }>;
  // Full context injected into AI Designer (for transparency)
  designer_context?: {
    product_info: {
      title: string;
      brand_name?: string;
      features: string[];
      target_audience?: string;
    };
    framework?: Record<string, unknown>;
    framework_summary?: {
      name: string;
      philosophy: string;
      brand_voice: string;
      colors: Array<{ hex: string; name: string; role: string; usage: string }>;
      typography: Record<string, string>;
      story_arc: Record<string, string>;
      visual_treatment: Record<string, unknown>;
    };
    image_copy?: {
      headline: string;
      subhead?: string;
      feature_callouts?: string[];
    };
    global_note?: string;
    product_analysis?: Record<string, unknown>;
  };
}

// ============================================================================
// Projects - User's generation session history
// ============================================================================

export interface ProjectListItem {
  session_id: string;
  product_title: string;
  status: GenerationStatus;
  created_at: string;
  image_count: number;
  complete_count: number;
  thumbnail_url?: string;
}

export interface ProjectListResponse {
  projects: ProjectListItem[];
  total: number;
  page: number;
  total_pages: number;
}

export interface ProjectImageDetail {
  image_type: ImageType;
  status: GenerationStatus;
  storage_path?: string;
  image_url?: string;
  error_message?: string;
}

export interface ProjectDetailResponse {
  session_id: string;
  product_title: string;
  status: GenerationStatus;
  created_at: string;
  completed_at?: string;
  brand_name?: string;
  images: ProjectImageDetail[];
}

// ============================================================================
// A+ Content Module Types
// ============================================================================

export type AplusModuleType = 'full_image' | 'dual_image' | 'four_image' | 'comparison';

export interface AplusModuleRequest {
  session_id: string;
  module_type: AplusModuleType;
  module_index: number;  // Position in A+ section (0 = first/top)
  previous_module_path?: string;  // For visual continuity chaining
  custom_instructions?: string;
}

export interface AplusModuleResponse {
  session_id: string;
  module_type: string;
  module_index: number;
  image_path: string;
  image_url: string;
  width: number;
  height: number;
  is_chained: boolean;
  generation_time_ms: number;
}

// A+ Module dimensions (for UI reference)
export const APLUS_DIMENSIONS: Record<AplusModuleType, { width: number; height: number }> = {
  full_image: { width: 1464, height: 600 },
  dual_image: { width: 650, height: 350 },
  four_image: { width: 300, height: 225 },
  comparison: { width: 200, height: 225 },
};
