import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { apiClient } from '@/api/client';
import type { DesignFramework } from '@/api/types';
import type { UploadWithPreview } from '../ImageUploader';

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
  expandedSections: controlledExpandedSections,
  onSectionToggle,
  className,
}) => {
  // Internal expanded sections state (if not controlled)
  const [internalExpandedSections, setInternalExpandedSections] = useState<string[]>(['photos', 'product']);

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
            <label className="block text-sm text-slate-400 mb-1">Style Reference Image</label>
            {formData.styleReferencePreview ? (
              <div className="flex items-center gap-3 bg-slate-700 border border-slate-600 rounded-lg p-3">
                <img
                  src={formData.styleReferencePreview}
                  alt="Style reference"
                  className="w-16 h-16 object-cover rounded"
                />
                <div className="flex-1 text-sm text-white truncate">
                  {formData.styleReferenceFile?.name}
                </div>
                <button
                  onClick={() => onFormChange({ styleReferenceFile: null, styleReferencePreview: null })}
                  className="text-red-400 hover:text-red-300 text-sm"
                >
                  Remove
                </button>
              </div>
            ) : (
              <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-redd-500/30 rounded-lg cursor-pointer hover:border-redd-500/50 transition-colors bg-redd-500/5">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleStyleRefChange}
                  className="hidden"
                />
                <svg className="w-6 h-6 text-redd-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
                <span className="text-sm text-slate-300">Upload style reference</span>
                <span className="text-xs text-slate-500">AI will match this visual style</span>
              </label>
            )}
          </div>

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
              {frameworks.map((framework) => {
                const isSelected = selectedFramework?.framework_id === framework.framework_id;
                return (
                  <button
                    key={framework.framework_id}
                    onClick={() => onSelectFramework(framework)}
                    className={cn(
                      'relative rounded-lg border-2 overflow-hidden transition-all text-left',
                      isSelected
                        ? 'border-redd-500 ring-2 ring-redd-500/30'
                        : 'border-slate-600 hover:border-slate-500'
                    )}
                  >
                    {/* Preview image */}
                    <div className="aspect-square bg-slate-700 relative">
                      {framework.preview_url ? (
                        <img
                          src={`http://localhost:8000${framework.preview_url}`}
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
                    </div>
                    {/* Framework name */}
                    <div className="p-2 bg-slate-800">
                      <p className="text-xs font-medium text-white truncate">{framework.framework_name}</p>
                      {/* Color palette preview */}
                      <div className="flex gap-1 mt-1">
                        {framework.colors.slice(0, 4).map((color, i) => (
                          <div
                            key={i}
                            className="w-4 h-4 rounded-full border border-slate-600"
                            style={{ backgroundColor: color.hex }}
                          />
                        ))}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
            )}
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
                `Preview ${formData.styleCount} Design Style${formData.styleCount > 1 ? 's' : ''}`
              )}
            </button>
          </div>
        ) : (
          // Generate button
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
              `Generate All 5 Images`
            ) : (
              'Select a Framework'
            )}
          </button>
        )}

        {/* Helper text */}
        <p className="text-center text-xs text-slate-500 mt-3">
          {frameworks.length === 0
            ? 'Upload photos and add a title to continue'
            : selectedFramework
            ? 'Click to generate all 5 Amazon listing images'
            : 'Select a design framework above'}
        </p>
      </div>
    </div>
  );
};

export default WorkshopPanel;
