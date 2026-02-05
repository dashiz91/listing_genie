import React, { useState, useCallback, useMemo } from 'react';
import { cn, normalizeColors } from '@/lib/utils';
import { apiClient, ASINImportResponse } from '@/api/client';
import type { DesignFramework } from '@/api/types';
import type { UploadWithPreview } from '../ImageUploader';
import { useCredits } from '@/contexts/CreditContext';
import { StyleLibrary } from '@/components/StyleLibrary';

// Collapsible section component
interface CollapsibleSectionProps {
  title: string;
  icon?: React.ReactNode;
  isOpen: boolean;
  onToggle: () => void;
  children: React.ReactNode;
  badge?: React.ReactNode;
  required?: boolean;
}

const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  icon,
  isOpen,
  onToggle,
  children,
  badge,
  required,
}) => (
  <div className="border border-slate-700 rounded-lg overflow-hidden">
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between p-4 bg-slate-800/50 hover:bg-slate-800 transition-colors"
    >
      <div className="flex items-center gap-3">
        {icon && <span className="text-slate-400">{icon}</span>}
        <span className="font-medium text-white">{title}</span>
        {required && <span className="text-redd-500 text-sm">*</span>}
        {badge}
      </div>
      <svg
        className={cn(
          'w-5 h-5 text-slate-400 transition-transform',
          isOpen ? 'rotate-180' : ''
        )}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    <div
      className={cn(
        'overflow-hidden transition-all duration-300',
        isOpen ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
      )}
    >
      <div className="p-4 bg-slate-800/30 border-t border-slate-700">
        {children}
      </div>
    </div>
  </div>
);

// Form data interface (mirrors ProductFormData but with real-time updates)
export interface WorkshopFormData {
  productTitle: string;
  feature1: string;
  feature2: string;
  feature3: string;
  targetAudience: string;
  keywords: string;
  brandName: string;
  brandColors: string[];
  logoFile: File | null;
  logoPreview: string | null;
  styleReferenceFile: File | null;
  styleReferencePreview: string | null;
  colorCount: number | null;
  colorPalette: string[];
  globalNote: string;
  styleCount: number; // Number of style frameworks to generate (1-4)
  imageModel: string; // Gemini model for image generation
}

interface WorkshopPanelProps {
  // Uploads
  uploads: UploadWithPreview[];
  onUploadsChange: (uploads: UploadWithPreview[]) => void;
  maxImages?: number;

  // Form data (real-time updates)
  formData: WorkshopFormData;
  onFormChange: (data: Partial<WorkshopFormData>) => void;

  // Frameworks
  frameworks: DesignFramework[];
  selectedFramework: DesignFramework | null;
  onSelectFramework: (framework: DesignFramework) => void;
  isAnalyzing?: boolean;
  productAnalysis?: string;

  // Actions
  onAnalyze: () => void;
  onGenerate: () => void;
  onStartOver: () => void;

  // State
  isGenerating?: boolean;
  canAnalyze?: boolean;
  canGenerate?: boolean;

  // Style reference toggle
  useOriginalStyleRef?: boolean;
  onToggleOriginalStyleRef?: (value: boolean) => void;

  // UI Control
  expandedSections?: string[];
  onSectionToggle?: (section: string) => void;

  className?: string;
}

// Default colors for quick picks
const DEFAULT_COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0'];

export const WorkshopPanel: React.FC<WorkshopPanelProps> = ({
  uploads,
  onUploadsChange,
  maxImages = 5,
  formData,
  onFormChange,
  frameworks,
  selectedFramework,
  onSelectFramework,
  isAnalyzing = false,
  productAnalysis,
  onAnalyze,
  onGenerate,
  onStartOver,
  isGenerating = false,
  canAnalyze = false,
  canGenerate = false,
  useOriginalStyleRef = false,
  onToggleOriginalStyleRef,
  expandedSections: controlledExpandedSections,
  onSectionToggle,
  className,
}) => {
  // Credits
  const { balance, isAdmin } = useCredits();

  // Calculate costs for current operations
  const analyzeCost = useMemo(() => {
    const numPreviews = formData.styleCount;
    return 1 + numPreviews; // 1 for analysis + previews
  }, [formData.styleCount]);

  const generateCost = useMemo(() => {
    const model = formData.imageModel;
    const modelCost = model.includes('flash') ? 1 : 3;
    return 6 * modelCost; // 6 listing images
  }, [formData.imageModel]);

  const canAffordAnalyze = isAdmin || balance >= analyzeCost;
  const canAffordGenerate = isAdmin || balance >= generateCost;

  // Internal expanded sections state (if not controlled)
  const [internalExpandedSections, setInternalExpandedSections] = useState<string[]>(['photos', 'product']);

  // Framework prompt/details modal state
  const [frameworkDetailIndex, setFrameworkDetailIndex] = useState<number | null>(null);

  // Use controlled or internal state
  const expandedSections = controlledExpandedSections || internalExpandedSections;

  const toggleSection = useCallback(
    (section: string) => {
      if (onSectionToggle) {
        onSectionToggle(section);
      } else {
        setInternalExpandedSections((prev) =>
          prev.includes(section) ? prev.filter((s) => s !== section) : [...prev, section]
        );
      }
    },
    [onSectionToggle]
  );

  const isSectionOpen = (section: string) => expandedSections.includes(section);

  // Color input state
  const [brandColorInput, setBrandColorInput] = useState('#4CAF50');
  const [paletteColorInput, setPaletteColorInput] = useState('#2196F3');

  // ASIN Import state
  const [asinInput, setAsinInput] = useState('');
  const [isImportingAsin, setIsImportingAsin] = useState(false);
  const [asinError, setAsinError] = useState<string | null>(null);

  // Style Library state
  const [isStyleLibraryOpen, setIsStyleLibraryOpen] = useState(false);
  const [selectedStyleId, setSelectedStyleId] = useState<string | undefined>(undefined);

  // Handle style library selection
  const handleStyleLibrarySelect = useCallback(async (style: { id: string; name: string; preview_image: string; colors: string[] }) => {
    setSelectedStyleId(style.id);
    setIsStyleLibraryOpen(false);

    try {
      // Fetch the preview image and convert to File
      const response = await fetch(style.preview_image);
      if (!response.ok) throw new Error('Failed to load style image');

      const blob = await response.blob();
      const file = new File([blob], `style-${style.id}.png`, { type: 'image/png' });

      // Create preview URL
      const reader = new FileReader();
      reader.onloadend = () => {
        onFormChange({
          styleReferenceFile: file,
          styleReferencePreview: reader.result as string,
          // Also set the color palette from the style
          colorPalette: style.colors.slice(0, 6),
        });
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error('Failed to load style:', err);
      // Fallback: just set the preview URL directly
      onFormChange({
        styleReferencePreview: style.preview_image,
        colorPalette: style.colors.slice(0, 6),
      });
    }
  }, [onFormChange]);

  // Handle ASIN import
  const handleAsinImport = async () => {
    if (!asinInput.trim()) {
      setAsinError('Please enter an ASIN');
      return;
    }

    setIsImportingAsin(true);
    setAsinError(null);

    try {
      const result: ASINImportResponse = await apiClient.importFromAsin(asinInput.trim(), {
        downloadImages: true,
        maxImages: 3,
      });

      // Clear input on success
      setAsinInput('');

      // Add imported images to uploads first (instant)
      if (result.image_uploads.length > 0) {
        const newUploads: UploadWithPreview[] = result.image_uploads.map((img, idx) => ({
          upload_id: img.upload_id,
          file_path: img.file_path,
          filename: `amazon_${result.asin}_${idx + 1}.png`,
          size: 0,
          preview_url: apiClient.getFileUrl(img.file_path),
        }));
        onUploadsChange([...uploads, ...newUploads].slice(0, maxImages));
      }

      // Expand sections to show imported data
      if (!isSectionOpen('photos') && result.image_uploads.length > 0) {
        toggleSection('photos');
      }
      if (!isSectionOpen('product')) {
        toggleSection('product');
      }
      if (!isSectionOpen('brand') && result.brand_name) {
        toggleSection('brand');
      }

      // Typing animation for text fields
      const typeText = async (
        field: 'productTitle' | 'feature1' | 'feature2' | 'feature3' | 'brandName',
        text: string,
        delay: number = 8
      ) => {
        for (let i = 0; i <= text.length; i++) {
          onFormChange({ [field]: text.slice(0, i) });
          await new Promise(r => setTimeout(r, delay));
        }
      };

      // Animate fields sequentially with fast typing
      if (result.title) await typeText('productTitle', result.title, 6);
      if (result.brand_name) await typeText('brandName', result.brand_name, 10);
      if (result.feature_1) await typeText('feature1', result.feature_1, 4);
      if (result.feature_2) await typeText('feature2', result.feature_2, 4);
      if (result.feature_3) await typeText('feature3', result.feature_3, 4);

    } catch (error: unknown) {
      const errMsg = error instanceof Error ? error.message : 'Failed to import product';
      // Extract detail from axios error if available
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setAsinError(axiosError.response?.data?.detail || errMsg);
    } finally {
      setIsImportingAsin(false);
    }
  };

  // Handle file upload for logo
  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        alert('Logo file must be under 5MB');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        onFormChange({
          logoFile: file,
          logoPreview: reader.result as string,
        });
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle file upload for style reference
  const handleStyleRefChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        alert('Style reference must be under 10MB');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        onFormChange({
          styleReferenceFile: file,
          styleReferencePreview: reader.result as string,
        });
      };
      reader.readAsDataURL(file);
    }
  };

  // Add/remove brand colors
  const addBrandColor = () => {
    if (formData.brandColors.length < 5 && !formData.brandColors.includes(brandColorInput)) {
      onFormChange({ brandColors: [...formData.brandColors, brandColorInput] });
    }
  };

  const removeBrandColor = (color: string) => {
    onFormChange({ brandColors: formData.brandColors.filter((c) => c !== color) });
  };

  // Add/remove palette colors
  const addPaletteColor = () => {
    if (formData.colorPalette.length < 6 && !formData.colorPalette.includes(paletteColorInput)) {
      onFormChange({ colorPalette: [...formData.colorPalette, paletteColorInput] });
    }
  };

  const removePaletteColor = (color: string) => {
    onFormChange({ colorPalette: formData.colorPalette.filter((c) => c !== color) });
  };

  // Handle image upload
  const handleImageFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const fileArray = Array.from(files);
    const remaining = maxImages - uploads.length;

    if (fileArray.length > remaining) {
      alert(`Maximum ${maxImages} images allowed. You can add ${remaining} more.`);
      return;
    }

    for (const file of fileArray) {
      if (!file.type.startsWith('image/')) continue;
      if (file.size > 10 * 1024 * 1024) continue;

      try {
        const previewDataUrl = await new Promise<string>((resolve) => {
          const reader = new FileReader();
          reader.onload = (e) => resolve(e.target?.result as string);
          reader.readAsDataURL(file);
        });

        const uploadResponse = await apiClient.uploadImage(file);

        onUploadsChange([
          ...uploads,
          {
            ...uploadResponse,
            preview_url: previewDataUrl,
          },
        ]);
      } catch (err) {
        console.error('Upload failed:', err);
      }
    }
  };

  const removeUpload = (uploadId: string) => {
    onUploadsChange(uploads.filter((u) => u.upload_id !== uploadId));
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white">Create Your Listing</h2>
        {uploads.length > 0 && (
          <button
            onClick={onStartOver}
            className="text-sm text-slate-400 hover:text-white transition-colors"
          >
            Start Over
          </button>
        )}
      </div>

      {/* ASIN Import - Quick import from Amazon */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2 mb-2">
          <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          <span className="text-sm font-medium text-white">Import from Amazon</span>
          <span className="text-xs text-slate-400">(auto-fill form)</span>
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={asinInput}
            onChange={(e) => {
              setAsinInput(e.target.value);
              setAsinError(null);
            }}
            placeholder="Enter ASIN (e.g., B09V3K6QFP)"
            className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            disabled={isImportingAsin}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAsinImport();
              }
            }}
          />
          <button
            onClick={handleAsinImport}
            disabled={isImportingAsin || !asinInput.trim()}
            className="px-4 py-2 bg-orange-600 hover:bg-orange-500 disabled:bg-slate-600 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            {isImportingAsin ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Importing...
              </>
            ) : (
              'Import'
            )}
          </button>
        </div>
        {asinError && (
          <p className="mt-2 text-xs text-red-400">{asinError}</p>
        )}
      </div>

      {/* Section 1: Product Photos */}
      <CollapsibleSection
        title="Product Photos"
        icon={
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        }
        isOpen={isSectionOpen('photos')}
        onToggle={() => toggleSection('photos')}
        badge={
          uploads.length > 0 ? (
            <span className="ml-2 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
              {uploads.length}/{maxImages}
            </span>
          ) : null
        }
        required
      >
        {/* Uploaded images grid */}
        {uploads.length > 0 && (
          <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 mb-4">
            {uploads.map((upload, index) => (
              <div
                key={upload.upload_id}
                className="relative group rounded-lg overflow-hidden border-2 border-slate-600 bg-slate-700/50"
              >
                <img
                  src={upload.preview_url}
                  alt={`Product ${index + 1}`}
                  className="w-full aspect-square object-contain"
                />
                {index === 0 && (
                  <div className="absolute top-1 left-1 bg-redd-500 text-white text-[8px] px-1 rounded">
                    Primary
                  </div>
                )}
                <button
                  onClick={() => removeUpload(upload.upload_id)}
                  className="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Upload zone */}
        {uploads.length < maxImages && (
          <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-redd-500/50 transition-colors bg-slate-800/30">
            <input
              type="file"
              accept="image/png,image/jpeg,image/jpg"
              multiple
              onChange={(e) => handleImageFiles(e.target.files)}
              className="hidden"
            />
            <svg className="w-10 h-10 text-slate-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span className="text-sm text-slate-400">
              Drag & drop or <span className="text-redd-400">browse</span>
            </span>
            <span className="text-xs text-slate-500 mt-1">
              PNG, JPG up to {maxImages - uploads.length} more
            </span>
          </label>
        )}

        <p className="text-xs text-slate-500 mt-3">
          Upload multiple angles - front, back, close-ups, product in use
        </p>
      </CollapsibleSection>

      {/* Section 2: Product Info */}
      <CollapsibleSection
        title="Product Info"
        icon={
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        }
        isOpen={isSectionOpen('product')}
        onToggle={() => toggleSection('product')}
        badge={
          formData.productTitle.trim() ? (
            <span className="ml-2 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
              ✓
            </span>
          ) : null
        }
        required
      >
        <div className="space-y-4">
          {/* Product Title */}
          <div>
            <label className="block text-sm font-medium text-white mb-1">
              Product Title *
            </label>
            <input
              type="text"
              value={formData.productTitle}
              onChange={(e) => onFormChange({ productTitle: e.target.value })}
              placeholder="e.g., Organic Vitamin D3 Gummies - Natural Immune Support"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-redd-500 focus:border-transparent"
              maxLength={200}
            />
          </div>

          {/* Features */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-slate-300">
              Key Features (Optional)
            </label>
            <input
              type="text"
              value={formData.feature1}
              onChange={(e) => onFormChange({ feature1: e.target.value })}
              placeholder="Feature 1 - Primary benefit"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-redd-500 focus:border-transparent text-sm"
              maxLength={100}
            />
            <input
              type="text"
              value={formData.feature2}
              onChange={(e) => onFormChange({ feature2: e.target.value })}
              placeholder="Feature 2 - Secondary benefit"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-redd-500 focus:border-transparent text-sm"
              maxLength={100}
            />
            <input
              type="text"
              value={formData.feature3}
              onChange={(e) => onFormChange({ feature3: e.target.value })}
              placeholder="Feature 3 - Additional benefit"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-redd-500 focus:border-transparent text-sm"
              maxLength={100}
            />
          </div>

          {/* Target Audience */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">
              Target Audience (Optional)
            </label>
            <input
              type="text"
              value={formData.targetAudience}
              onChange={(e) => onFormChange({ targetAudience: e.target.value })}
              placeholder="e.g., Health-conscious adults 30-55"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-redd-500 focus:border-transparent text-sm"
              maxLength={150}
            />
          </div>
        </div>
      </CollapsibleSection>

      {/* Section 3: Brand Identity */}
      <CollapsibleSection
        title="Brand Identity"
        icon={
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        }
        isOpen={isSectionOpen('brand')}
        onToggle={() => toggleSection('brand')}
      >
        <div className="space-y-4">
          {/* Brand Name */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Brand Name</label>
            <input
              type="text"
              value={formData.brandName}
              onChange={(e) => onFormChange({ brandName: e.target.value })}
              placeholder="e.g., VitaGlow"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-redd-500 focus:border-transparent"
              maxLength={100}
            />
          </div>

          {/* Logo */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Brand Logo</label>
            {formData.logoPreview ? (
              <div className="flex items-center gap-3 bg-slate-700 border border-slate-600 rounded-lg p-3">
                <img
                  src={formData.logoPreview}
                  alt="Logo preview"
                  className="w-12 h-12 object-contain rounded"
                />
                <div className="flex-1 text-sm text-white truncate">
                  {formData.logoFile?.name}
                </div>
                <button
                  onClick={() => onFormChange({ logoFile: null, logoPreview: null })}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  Remove
                </button>
              </div>
            ) : (
              <label className="flex items-center justify-center p-4 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-redd-500/50 transition-colors">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleLogoChange}
                  className="hidden"
                />
                <span className="text-sm text-slate-400">Click to upload logo</span>
              </label>
            )}
          </div>

          {/* Brand Colors */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Brand Colors (up to 5)</label>
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.brandColors.map((color) => (
                <div
                  key={color}
                  className="flex items-center gap-1 bg-slate-700 border border-slate-600 rounded-full px-2 py-1"
                >
                  <div
                    className="w-4 h-4 rounded-full border border-slate-500"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-xs text-slate-300">{color}</span>
                  <button
                    onClick={() => removeBrandColor(color)}
                    className="text-slate-400 hover:text-red-400 ml-1"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="color"
                value={brandColorInput}
                onChange={(e) => setBrandColorInput(e.target.value)}
                className="w-10 h-10 rounded cursor-pointer bg-slate-700 border border-slate-600"
              />
              <input
                type="text"
                value={brandColorInput}
                onChange={(e) => setBrandColorInput(e.target.value)}
                placeholder="#RRGGBB"
                className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm text-white placeholder-slate-500"
                maxLength={7}
              />
              <button
                onClick={addBrandColor}
                disabled={formData.brandColors.length >= 5}
                className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                Add
              </button>
            </div>
            <div className="flex gap-1 mt-2">
              <span className="text-xs text-slate-500">Quick:</span>
              {DEFAULT_COLORS.map((c) => (
                <button
                  key={c}
                  onClick={() => setBrandColorInput(c)}
                  className="w-5 h-5 rounded-full border border-slate-500 hover:scale-110 transition-transform"
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Section 4: Style & Colors */}
      <CollapsibleSection
        title="Style & Colors"
        icon={
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
          </svg>
        }
        isOpen={isSectionOpen('style')}
        onToggle={() => toggleSection('style')}
      >
        <div className="space-y-4">
          {/* Style Reference */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">Style Reference Image</label>
            {formData.styleReferencePreview ? (
              <div className="space-y-2">
                <div className="flex items-center gap-3 bg-slate-700 border border-slate-600 rounded-lg p-3">
                  <img
                    src={formData.styleReferencePreview}
                    alt="Style reference"
                    className="w-16 h-16 object-cover rounded"
                  />
                  <div className="flex-1 text-sm text-white truncate">
                    {formData.styleReferenceFile?.name || 'Pre-made style'}
                  </div>
                  <button
                    onClick={() => {
                      onFormChange({ styleReferenceFile: null, styleReferencePreview: null });
                      setSelectedStyleId(undefined);
                    }}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    Remove
                  </button>
                </div>
                {/* Quick access to browse more styles */}
                <button
                  type="button"
                  onClick={() => setIsStyleLibraryOpen(true)}
                  className="w-full flex items-center justify-center gap-1.5 py-2 text-xs text-slate-400 hover:text-redd-400 transition-colors"
                >
                  <span>🎨</span>
                  <span>Browse more styles</span>
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Browse Pre-made Styles - Primary CTA */}
                <button
                  type="button"
                  onClick={() => setIsStyleLibraryOpen(true)}
                  className="w-full flex items-center justify-center gap-2 p-4 bg-gradient-to-r from-redd-500/20 to-redd-600/20 border-2 border-redd-500/40 rounded-lg hover:border-redd-500/60 hover:from-redd-500/30 hover:to-redd-600/30 transition-all"
                >
                  <span className="text-xl">🎨</span>
                  <div className="text-left">
                    <span className="text-sm font-medium text-white block">Browse Style Library</span>
                    <span className="text-xs text-slate-400">Free pre-made styles - no credits required</span>
                  </div>
                </button>

                {/* Or upload custom */}
                <div className="relative flex items-center">
                  <div className="flex-grow border-t border-slate-700"></div>
                  <span className="px-3 text-xs text-slate-500">or upload your own</span>
                  <div className="flex-grow border-t border-slate-700"></div>
                </div>

                <label className="flex flex-col items-center justify-center p-3 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-slate-500 transition-colors bg-slate-800/30">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleStyleRefChange}
                    className="hidden"
                  />
                  <svg className="w-5 h-5 text-slate-400 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  <span className="text-xs text-slate-400">Upload custom style image</span>
                </label>
              </div>
            )}
          </div>

          {/* Use Original Style toggle - only when style reference is uploaded */}
          {formData.styleReferencePreview && (
            <button
              onClick={() => onToggleOriginalStyleRef?.(!useOriginalStyleRef)}
              className={cn(
                'w-full flex items-center gap-3 p-3 rounded-lg border transition-all text-left',
                useOriginalStyleRef
                  ? 'bg-redd-500/10 border-redd-500/40'
                  : 'bg-slate-700/30 border-slate-600 hover:border-slate-500'
              )}
            >
              <div className={cn(
                'w-9 h-5 rounded-full flex items-center transition-colors shrink-0',
                useOriginalStyleRef ? 'bg-redd-500 justify-end' : 'bg-slate-600 justify-start'
              )}>
                <div className="w-4 h-4 bg-white rounded-full mx-0.5 shadow-sm" />
              </div>
              <div>
                <p className={cn('text-xs font-medium', useOriginalStyleRef ? 'text-redd-400' : 'text-slate-400')}>
                  Use exact style image
                </p>
                <p className="text-[10px] text-slate-500">
                  {useOriginalStyleRef
                    ? '0 preview credits — your image is used directly as reference'
                    : '1-4 preview credits — AI generates styled previews first'}
                </p>
              </div>
            </button>
          )}

          {/* Color Count */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">Number of Colors</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => onFormChange({ colorCount: null })}
                className={cn(
                  'px-3 py-2 rounded-lg text-sm',
                  formData.colorCount === null
                    ? 'bg-redd-500 text-white'
                    : 'bg-slate-700 border border-slate-600 text-slate-300 hover:bg-slate-600'
                )}
              >
                AI Decides
              </button>
              {[2, 3, 4, 5, 6].map((count) => (
                <button
                  key={count}
                  onClick={() => onFormChange({ colorCount: count })}
                  className={cn(
                    'w-10 h-10 rounded-lg text-sm font-medium',
                    formData.colorCount === count
                      ? 'bg-redd-500 text-white'
                      : 'bg-slate-700 border border-slate-600 text-slate-300 hover:bg-slate-600'
                  )}
                >
                  {count}
                </button>
              ))}
            </div>
          </div>

          {/* Color Palette */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">
              Color Palette (leave empty for AI to generate)
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.colorPalette.map((color) => (
                <div
                  key={color}
                  className="flex items-center gap-1 bg-slate-700 border border-slate-600 rounded-full px-2 py-1"
                >
                  <div
                    className="w-4 h-4 rounded-full border border-slate-500"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-xs text-slate-300">{color}</span>
                  <button
                    onClick={() => removePaletteColor(color)}
                    className="text-slate-400 hover:text-red-400 ml-1"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            {formData.colorPalette.length < 6 && (
              <div className="flex gap-2">
                <input
                  type="color"
                  value={paletteColorInput}
                  onChange={(e) => setPaletteColorInput(e.target.value)}
                  className="w-10 h-10 rounded cursor-pointer bg-slate-700 border border-slate-600"
                />
                <input
                  type="text"
                  value={paletteColorInput}
                  onChange={(e) => setPaletteColorInput(e.target.value)}
                  placeholder="#RRGGBB"
                  className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm text-white placeholder-slate-500"
                  maxLength={7}
                />
                <button
                  onClick={addPaletteColor}
                  className="px-4 py-2 bg-redd-500/20 text-redd-400 rounded-lg hover:bg-redd-500/30 text-sm border border-redd-500/30"
                >
                  Add
                </button>
              </div>
            )}
          </div>
        </div>
      </CollapsibleSection>

      {/* Section 5: Global Instructions */}
      <CollapsibleSection
        title="Global Instructions"
        icon={
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        }
        isOpen={isSectionOpen('instructions')}
        onToggle={() => toggleSection('instructions')}
      >
        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="text-sm text-slate-400">
              Instructions for all images
            </label>
            <span className={cn(
              'text-xs',
              formData.globalNote.length > 1800 ? 'text-orange-400' : 'text-slate-500'
            )}>
              {formData.globalNote.length}/2000
            </span>
          </div>
          <textarea
            value={formData.globalNote}
            onChange={(e) => onFormChange({ globalNote: e.target.value })}
            maxLength={2000}
            placeholder="e.g., Use warm lighting, avoid text overlays, keep backgrounds minimal..."
            rows={3}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-redd-500 focus:border-transparent resize-none"
          />
        </div>
      </CollapsibleSection>

      {/* Section 6: Design Framework - Show during analysis or when frameworks available */}
      {(isAnalyzing || frameworks.length > 0) && (
        <CollapsibleSection
          title="Design Framework"
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
          }
          isOpen={isSectionOpen('framework')}
          onToggle={() => toggleSection('framework')}
          badge={
            isAnalyzing ? (
              <span className="ml-2 px-2 py-0.5 bg-redd-500/20 text-redd-400 text-xs rounded-full animate-pulse">
                Analyzing...
              </span>
            ) : selectedFramework ? (
              <span className="ml-2 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
                Selected
              </span>
            ) : null
          }
        >
          <div className="space-y-4">
            {/* Loading Skeleton during analysis */}
            {isAnalyzing && frameworks.length === 0 && (
              <>
                {/* AI Analysis skeleton */}
                <div className="p-3 bg-slate-700/50 rounded-lg border border-slate-600 animate-pulse">
                  <div className="h-3 w-20 bg-slate-600 rounded mb-2" />
                  <div className="h-4 w-full bg-slate-600 rounded mb-1" />
                  <div className="h-4 w-3/4 bg-slate-600 rounded" />
                </div>

                {/* Framework cards skeleton with shimmer */}
                <div className="grid grid-cols-2 gap-3">
                  {[1, 2, 3, 4].slice(0, formData.styleCount).map((i) => (
                    <div
                      key={i}
                      className="relative rounded-lg border-2 border-slate-600 overflow-hidden"
                    >
                      {/* Shimmer overlay */}
                      <div className="aspect-square bg-slate-700 relative overflow-hidden">
                        <div
                          className="absolute inset-0 animate-shimmer"
                          style={{
                            background: 'linear-gradient(90deg, transparent 0%, rgba(200,90,53,0.2) 50%, transparent 100%)',
                            backgroundSize: '200% 100%',
                          }}
                        />
                        {/* Pulsing icon */}
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="text-center">
                            <div className="w-10 h-10 border-3 border-redd-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                            <span className="text-xs text-slate-400">Creating style {i}...</span>
                          </div>
                        </div>
                      </div>
                      {/* Name skeleton */}
                      <div className="p-2 bg-slate-800">
                        <div className="h-3 w-2/3 bg-slate-600 rounded animate-pulse" />
                        <div className="flex gap-1 mt-2">
                          {[1, 2, 3, 4].map((j) => (
                            <div key={j} className="w-4 h-4 rounded-full bg-slate-600 animate-pulse" />
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {/* Product Analysis */}
            {productAnalysis && !isAnalyzing && (
              <div className="p-3 bg-slate-700/50 rounded-lg border border-slate-600">
                <p className="text-xs font-medium text-redd-400 mb-1">AI Analysis</p>
                <p className="text-sm text-slate-300">{productAnalysis}</p>
              </div>
            )}

            {/* Framework Cards (mini) - only show when not analyzing */}
            {!isAnalyzing && frameworks.length > 0 && (
            <div className="grid grid-cols-2 gap-3">
              {frameworks.map((framework, fwIndex) => {
                const isSelected = selectedFramework?.framework_id === framework.framework_id;
                return (
                  <div
                    key={framework.framework_id}
                    className={cn(
                      'group relative rounded-lg border-2 overflow-hidden transition-all text-left cursor-pointer',
                      isSelected
                        ? 'border-redd-500 ring-2 ring-redd-500/30'
                        : 'border-slate-600 hover:border-slate-500'
                    )}
                    onClick={() => onSelectFramework(framework)}
                  >
                    {/* Preview image */}
                    <div className="aspect-square bg-slate-700 relative">
                      {framework.preview_url ? (
                        <img
                          src={framework.preview_url.startsWith('http') ? framework.preview_url : `${import.meta.env.VITE_API_URL || ''}${framework.preview_url}`}
                          alt={framework.framework_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-6 h-6 border-2 border-redd-500 border-t-transparent rounded-full animate-spin" />
                        </div>
                      )}
                      {/* Selected check */}
                      {isSelected && (
                        <div className="absolute top-2 right-2 w-6 h-6 bg-redd-500 rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                      {/* Hover overlay with action buttons */}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <button
                          onClick={(e) => { e.stopPropagation(); setFrameworkDetailIndex(fwIndex); }}
                          className="px-3 py-1.5 bg-white/90 hover:bg-white rounded-lg text-xs font-medium text-slate-800 flex items-center gap-1 transition-colors"
                          title="View Prompt"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                          </svg>
                          Prompt
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); onAnalyze(); }}
                          className="px-3 py-1.5 bg-white/90 hover:bg-white rounded-lg text-xs font-medium text-slate-800 flex items-center gap-1 transition-colors"
                          title="Regenerate Styles"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Regenerate
                        </button>
                      </div>
                    </div>
                    {/* Framework name */}
                    <div className="p-2 bg-slate-800">
                      <p className="text-xs font-medium text-white truncate">{framework.framework_name}</p>
                      {/* Color palette preview */}
                      <div className="flex gap-1 mt-1">
                        {normalizeColors(framework.colors).slice(0, 4).map((color, i) => (
                          <div
                            key={i}
                            className="w-4 h-4 rounded-full border border-slate-600"
                            style={{ backgroundColor: color.hex }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            )}

            {/* Framework Detail Modal */}
            {frameworkDetailIndex !== null && frameworks[frameworkDetailIndex] && (() => {
              const fw = frameworks[frameworkDetailIndex];
              return (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm" onClick={() => setFrameworkDetailIndex(null)}>
                  <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-lg w-full mx-4 max-h-[85vh] overflow-y-auto shadow-2xl" onClick={(e) => e.stopPropagation()}>
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b border-slate-700 sticky top-0 bg-slate-800 z-10">
                      <h3 className="text-lg font-semibold text-white">{fw.framework_name}</h3>
                      <button onClick={() => setFrameworkDetailIndex(null)} className="p-1 text-slate-400 hover:text-white transition-colors">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>

                    <div className="p-4 space-y-4">
                      {/* Design Philosophy */}
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase mb-1">Design Philosophy</h4>
                        <p className="text-sm text-slate-300 italic">"{fw.design_philosophy}"</p>
                      </div>

                      {/* Color Palette */}
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">Color Palette</h4>
                        <div className="flex flex-wrap gap-2">
                          {normalizeColors(fw.colors).map((color, i) => (
                            <div key={i} className="flex items-center gap-2 bg-slate-700/50 rounded-lg px-2 py-1">
                              <div className="w-5 h-5 rounded-full border border-slate-500" style={{ backgroundColor: color.hex }} />
                              <div>
                                <p className="text-xs text-white font-medium">{color.name || 'Color'}</p>
                                <p className="text-[10px] text-slate-400">{color.hex} — {color.role || 'color'}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Typography */}
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase mb-1">Typography</h4>
                        <p className="text-sm text-slate-300">Headline: {fw.typography.headline_font}</p>
                        {fw.typography.body_font && <p className="text-sm text-slate-300">Body: {fw.typography.body_font}</p>}
                      </div>

                      {/* Image Headlines */}
                      {fw.image_copy && fw.image_copy.length > 0 && (
                        <div>
                          <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">Headlines per Image</h4>
                          <div className="space-y-1">
                            {fw.image_copy.map((copy, i) => (
                              <div key={i} className="text-sm">
                                <span className="font-medium text-slate-200">
                                  {copy.image_type.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}:
                                </span>{' '}
                                <span className="text-slate-400">{copy.headline}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Visual Treatment */}
                      {fw.visual_treatment && (
                        <div>
                          <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">Visual Treatment</h4>
                          <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                            <div><span className="text-slate-300 font-medium">Lighting:</span>{' '}<span className="text-slate-400">{fw.visual_treatment.lighting_style}</span></div>
                            <div><span className="text-slate-300 font-medium">Background:</span>{' '}<span className="text-slate-400">{fw.visual_treatment.background_treatment}</span></div>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {fw.visual_treatment.mood_keywords.map((kw, i) => (
                              <span key={i} className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300">{kw}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Layout */}
                      {fw.layout?.whitespace_philosophy && (
                        <div>
                          <h4 className="text-xs font-semibold text-slate-400 uppercase mb-1">Layout Philosophy</h4>
                          <p className="text-xs text-slate-300">{fw.layout.whitespace_philosophy}</p>
                        </div>
                      )}

                      {/* Rationale */}
                      {fw.rationale && (
                        <div className="bg-slate-700/50 p-3 rounded-lg border border-slate-600">
                          <h4 className="text-xs font-semibold text-slate-400 uppercase mb-1">Why This Works</h4>
                          <p className="text-xs text-slate-300">{fw.rationale}</p>
                        </div>
                      )}

                      {/* Target Appeal */}
                      {fw.target_appeal && (
                        <div>
                          <h4 className="text-xs font-semibold text-slate-400 uppercase mb-1">Target Appeal</h4>
                          <p className="text-xs text-slate-300">{fw.target_appeal}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </CollapsibleSection>
      )}

      {/* Action Button */}
      <div className="pt-4 border-t border-slate-700">
        {frameworks.length === 0 ? (
          <div className="space-y-4">
            {/* Style count selector */}
            <div className="flex items-center justify-between bg-slate-800/50 rounded-lg p-3">
              <div>
                <label className="text-sm font-medium text-white">Style Options</label>
                <p className="text-xs text-slate-500 mt-0.5">How many design styles to preview</p>
              </div>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4].map((count) => (
                  <button
                    key={count}
                    onClick={() => onFormChange({ styleCount: count })}
                    className={cn(
                      'w-9 h-9 rounded-lg font-medium transition-all',
                      formData.styleCount === count
                        ? 'bg-redd-500 text-white'
                        : 'bg-slate-700 text-slate-400 hover:bg-slate-600 hover:text-white'
                    )}
                  >
                    {count}
                  </button>
                ))}
              </div>
            </div>

            {/* Analyze button */}
            <button
              onClick={onAnalyze}
              disabled={!canAnalyze || isAnalyzing}
              className={cn(
                'w-full py-4 px-6 rounded-xl font-bold text-white text-lg transition-all',
                canAnalyze && !isAnalyzing
                  ? 'bg-redd-500 hover:bg-redd-600 shadow-lg shadow-redd-500/20'
                  : 'bg-slate-700 cursor-not-allowed'
              )}
            >
              {isAnalyzing ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Analyzing Product...
                </span>
              ) : (
                useOriginalStyleRef
                  ? 'Analyze & Create Framework'
                  : `Preview ${formData.styleCount} Design Style${formData.styleCount > 1 ? 's' : ''}`
              )}
            </button>

            {/* Cost preview for Analyze */}
            {!isAnalyzing && canAnalyze && (
              <div className="text-center">
                {isAdmin ? (
                  <p className="text-xs text-amber-400/80 flex items-center justify-center gap-1">
                    <span>👑</span> No credits used (Admin)
                  </p>
                ) : canAffordAnalyze ? (
                  <p className="text-xs text-slate-400">
                    <span className="text-redd-400 font-medium">{analyzeCost}</span> credits
                  </p>
                ) : (
                  <p className="text-xs text-orange-400">
                    Need {analyzeCost} credits (you have {balance})
                  </p>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {/* AI Model Selector — shown when framework is selected, before generating */}
            <div className="flex items-center justify-between px-1">
              <span className="text-xs text-slate-400">AI Model</span>
              <select
                value={formData.imageModel}
                onChange={(e) => onFormChange({ imageModel: e.target.value })}
                disabled={isGenerating}
                className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-xs text-white focus:ring-1 focus:ring-redd-500 focus:border-transparent disabled:opacity-50"
              >
                <option value="gemini-2.5-flash-image">⚡ Flash — Fast (1 credit/img)</option>
                <option value="gemini-3-pro-image-preview">✨ Pro — Best quality (3 credits/img)</option>
              </select>
            </div>

            {/* Generate button */}
            <button
              onClick={onGenerate}
              disabled={!canGenerate || isGenerating}
              className={cn(
                'w-full py-4 px-6 rounded-xl font-bold text-white text-lg transition-all',
                canGenerate && !isGenerating
                  ? 'bg-redd-500 hover:bg-redd-600 shadow-lg shadow-redd-500/20'
                  : 'bg-slate-700 cursor-not-allowed'
              )}
            >
              {isGenerating ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Generating Images...
                </span>
              ) : selectedFramework ? (
                `Generate All 6 Images`
              ) : (
                'Select a Framework'
              )}
            </button>

            {/* Cost preview for Generate */}
            {!isGenerating && selectedFramework && (
              <div className="text-center space-y-1">
                {isAdmin ? (
                  <p className="text-xs text-amber-400/80 flex items-center justify-center gap-1">
                    <span>👑</span> No credits used (Admin)
                  </p>
                ) : canAffordGenerate ? (
                  <p className="text-xs text-slate-400">
                    <span className="text-redd-400 font-medium">{generateCost}</span> credits
                    <span className="text-slate-500"> • {balance - generateCost} remaining after</span>
                  </p>
                ) : (
                  <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-2">
                    <p className="text-xs text-orange-400 font-medium">
                      Need {generateCost} credits (you have {balance})
                    </p>
                    {formData.imageModel.includes('pro') && balance >= 6 && (
                      <button
                        onClick={() => onFormChange({ imageModel: 'gemini-2.5-flash-image' })}
                        className="text-xs text-redd-400 hover:text-redd-300 underline mt-1"
                      >
                        Switch to Flash (6 credits) →
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Re-plan Styles button */}
            <button
              onClick={onAnalyze}
              disabled={isAnalyzing || isGenerating}
              className={cn(
                'w-full py-2.5 px-4 rounded-xl font-medium text-sm transition-all flex items-center justify-center gap-2',
                isAnalyzing || isGenerating
                  ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600 hover:text-white border border-slate-600'
              )}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {isAnalyzing ? 'Re-planning...' : 'Re-plan Styles'}
            </button>
          </div>
        )}

        {/* Helper text */}
        <p className="text-center text-xs text-slate-500 mt-3">
          {frameworks.length === 0
            ? 'Upload photos and add a title to continue'
            : selectedFramework
            ? 'Click to generate all 6 Amazon listing images'
            : 'Select a design framework above'}
        </p>
      </div>

      {/* Style Library Sheet */}
      <StyleLibrary
        open={isStyleLibraryOpen}
        onClose={() => setIsStyleLibraryOpen(false)}
        onSelectStyle={handleStyleLibrarySelect}
        selectedStyleId={selectedStyleId}
      />
    </div>
  );
};

export default WorkshopPanel;
