import React, { useState } from 'react';
import type { BrandVibe } from '../api/types';

// Brand vibe options with descriptions
const VIBE_OPTIONS: { value: BrandVibe; label: string; description: string; icon: string }[] = [
  {
    value: 'clean_modern',
    label: 'Clean & Modern',
    description: 'Minimal, tech-forward, sophisticated',
    icon: '✨',
  },
  {
    value: 'premium_luxury',
    label: 'Premium Luxury',
    description: 'Elegant, exclusive, aspirational',
    icon: '💎',
  },
  {
    value: 'bold_energetic',
    label: 'Bold & Energetic',
    description: 'Dynamic, confident, action-oriented',
    icon: '⚡',
  },
  {
    value: 'natural_organic',
    label: 'Natural & Organic',
    description: 'Earthy, authentic, wholesome',
    icon: '🌿',
  },
  {
    value: 'playful_fun',
    label: 'Playful & Fun',
    description: 'Vibrant, youthful, joyful',
    icon: '🎨',
  },
  {
    value: 'clinical_trust',
    label: 'Clinical & Trustworthy',
    description: 'Professional, scientific, reliable',
    icon: '🔬',
  },
];

export interface ProductFormData {
  productTitle: string;
  feature1: string;
  feature2: string;
  feature3: string;
  targetAudience: string;
  keywords: string;
  brandName: string;
  brandColors: string[];
  logoFile: File | null;
  // MASTER Level: Brand vibe - drives the entire creative brief
  brandVibe: BrandVibe | null;
  primaryColor: string;
  // Style reference image - AI matches this visual style
  styleReferenceFile: File | null;
  // Color palette options
  colorCount: number | null;  // 2-6 or null for AI to decide
  colorPalette: string[];  // Specific colors, empty = AI generates
  // Global note/instructions for all image generations
  globalNote: string;
}

interface ProductFormProps {
  onSubmit: (data: ProductFormData) => void;
  disabled?: boolean;
  isGenerating?: boolean;
}

const DEFAULT_COLORS = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0'];

export const ProductForm: React.FC<ProductFormProps> = ({
  onSubmit,
  disabled = false,
  isGenerating = false,
}) => {
  const [formData, setFormData] = useState<ProductFormData>({
    productTitle: '',
    feature1: '',
    feature2: '',
    feature3: '',
    targetAudience: '',
    keywords: '',
    brandName: '',
    brandColors: [],
    logoFile: null,
    // MASTER Level defaults
    brandVibe: 'clean_modern',
    primaryColor: '#2196F3',
    styleReferenceFile: null,
    colorCount: null,
    colorPalette: [],
    globalNote: '',
  });

  const [colorInput, setColorInput] = useState('#4CAF50');
  const [paletteColorInput, setPaletteColorInput] = useState('#2196F3');
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [styleRefPreview, setStyleRefPreview] = useState<string | null>(null);

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('Logo file must be under 5MB');
        return;
      }
      setFormData((prev) => ({ ...prev, logoFile: file }));
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeLogo = () => {
    setFormData((prev) => ({ ...prev, logoFile: null }));
    setLogoPreview(null);
  };

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
      setFormData((prev) => ({ ...prev, styleReferenceFile: file }));
      const reader = new FileReader();
      reader.onloadend = () => {
        setStyleRefPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeStyleRef = () => {
    setFormData((prev) => ({ ...prev, styleReferenceFile: null }));
    setStyleRefPreview(null);
  };

  const addPaletteColor = () => {
    if (formData.colorPalette.length < 6 && !formData.colorPalette.includes(paletteColorInput)) {
      setFormData((prev) => ({
        ...prev,
        colorPalette: [...prev.colorPalette, paletteColorInput],
      }));
    }
  };

  const removePaletteColor = (color: string) => {
    setFormData((prev) => ({
      ...prev,
      colorPalette: prev.colorPalette.filter((c) => c !== color),
    }));
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const addColor = () => {
    if (formData.brandColors.length < 5 && !formData.brandColors.includes(colorInput)) {
      setFormData((prev) => ({
        ...prev,
        brandColors: [...prev.brandColors, colorInput],
      }));
    }
  };

  const removeColor = (color: string) => {
    setFormData((prev) => ({
      ...prev,
      brandColors: prev.brandColors.filter((c) => c !== color),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  // Only product title is required now
  const isFormValid = formData.productTitle.trim().length > 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Product Title */}
      <div>
        <label
          htmlFor="productTitle"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Product Title *
        </label>
        <input
          type="text"
          id="productTitle"
          name="productTitle"
          value={formData.productTitle}
          onChange={handleChange}
          disabled={disabled}
          placeholder="e.g., Organic Vitamin D3 Gummies - Natural Immune Support"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          maxLength={200}
        />
      </div>

      {/* Brand Section */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-4">
        <h3 className="text-sm font-medium text-gray-700">
          Brand Identity (Optional)
        </h3>

        {/* Brand Name */}
        <div>
          <label
            htmlFor="brandName"
            className="block text-xs text-gray-500 mb-1"
          >
            Brand Name
          </label>
          <input
            type="text"
            id="brandName"
            name="brandName"
            value={formData.brandName}
            onChange={handleChange}
            disabled={disabled}
            placeholder="e.g., VitaGlow"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
            maxLength={100}
          />
        </div>

        {/* Brand Logo */}
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            Brand Logo
          </label>
          {logoPreview ? (
            <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-lg p-3">
              <img
                src={logoPreview}
                alt="Logo preview"
                className="w-16 h-16 object-contain rounded"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">
                  {formData.logoFile?.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formData.logoFile && (formData.logoFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button
                type="button"
                onClick={removeLogo}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                Remove
              </button>
            </div>
          ) : (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-primary-400 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleLogoChange}
                disabled={disabled}
                className="hidden"
                id="logo-upload"
              />
              <label
                htmlFor="logo-upload"
                className="cursor-pointer block"
              >
                <div className="text-gray-400 mb-1">
                  <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <span className="text-sm text-gray-500">Click to upload logo</span>
                <p className="text-xs text-gray-400 mt-1">PNG, JPG up to 5MB</p>
              </label>
            </div>
          )}
          <p className="text-xs text-gray-400 mt-1">
            Logo will be incorporated into all generated images
          </p>
        </div>

        {/* Brand Colors */}
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            Brand Colors (up to 5)
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {formData.brandColors.map((color) => (
              <div
                key={color}
                className="flex items-center gap-1 bg-white border rounded-full px-2 py-1"
              >
                <div
                  className="w-4 h-4 rounded-full border"
                  style={{ backgroundColor: color }}
                />
                <span className="text-xs">{color}</span>
                <button
                  type="button"
                  onClick={() => removeColor(color)}
                  className="text-gray-400 hover:text-red-500 ml-1"
                >
                  x
                </button>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="color"
              value={colorInput}
              onChange={(e) => setColorInput(e.target.value)}
              className="w-10 h-10 rounded cursor-pointer"
            />
            <input
              type="text"
              value={colorInput}
              onChange={(e) => setColorInput(e.target.value)}
              placeholder="#RRGGBB"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
              maxLength={7}
            />
            <button
              type="button"
              onClick={addColor}
              disabled={formData.brandColors.length >= 5}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              Add
            </button>
          </div>
          <div className="flex gap-1 mt-2">
            <span className="text-xs text-gray-400">Quick picks:</span>
            {DEFAULT_COLORS.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setColorInput(c)}
                className="w-5 h-5 rounded-full border border-gray-300 hover:scale-110 transition-transform"
                style={{ backgroundColor: c }}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Style & Color Section */}
      <div className="bg-blue-50 rounded-lg p-4 space-y-4">
        <h3 className="text-sm font-medium text-gray-700">
          Style & Color Options (Optional)
        </h3>

        {/* Style Reference Image */}
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            Style Reference Image
          </label>
          {styleRefPreview ? (
            <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-lg p-3">
              <img
                src={styleRefPreview}
                alt="Style reference preview"
                className="w-20 h-20 object-cover rounded"
              />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">
                  {formData.styleReferenceFile?.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formData.styleReferenceFile && (formData.styleReferenceFile.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <button
                type="button"
                onClick={removeStyleRef}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                Remove
              </button>
            </div>
          ) : (
            <div className="border-2 border-dashed border-blue-300 rounded-lg p-4 text-center hover:border-blue-400 transition-colors bg-white">
              <input
                type="file"
                accept="image/*"
                onChange={handleStyleRefChange}
                disabled={disabled}
                className="hidden"
                id="style-ref-upload"
              />
              <label
                htmlFor="style-ref-upload"
                className="cursor-pointer block"
              >
                <div className="text-blue-400 mb-1">
                  <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                  </svg>
                </div>
                <span className="text-sm text-gray-600">Upload style reference</span>
                <p className="text-xs text-gray-400 mt-1">AI will match this visual style</p>
              </label>
            </div>
          )}
        </div>

        {/* Color Count Selector */}
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            Number of Colors in Palette
          </label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setFormData(prev => ({ ...prev, colorCount: null }))}
              className={`px-3 py-2 rounded-lg text-sm ${
                formData.colorCount === null
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              AI Decides
            </button>
            {[2, 3, 4, 5, 6].map((count) => (
              <button
                key={count}
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, colorCount: count }))}
                className={`w-10 h-10 rounded-lg text-sm font-medium ${
                  formData.colorCount === count
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {count}
              </button>
            ))}
          </div>
        </div>

        {/* Color Palette Picker */}
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            Color Palette (leave empty for AI to generate)
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {formData.colorPalette.map((color) => (
              <div
                key={color}
                className="flex items-center gap-1 bg-white border rounded-full px-2 py-1"
              >
                <div
                  className="w-4 h-4 rounded-full border"
                  style={{ backgroundColor: color }}
                />
                <span className="text-xs">{color}</span>
                <button
                  type="button"
                  onClick={() => removePaletteColor(color)}
                  className="text-gray-400 hover:text-red-500 ml-1"
                >
                  x
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
                className="w-10 h-10 rounded cursor-pointer"
              />
              <input
                type="text"
                value={paletteColorInput}
                onChange={(e) => setPaletteColorInput(e.target.value)}
                placeholder="#RRGGBB"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                maxLength={7}
              />
              <button
                type="button"
                onClick={addPaletteColor}
                className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 text-sm"
              >
                Add Color
              </button>
            </div>
          )}
          <p className="text-xs text-gray-400 mt-2">
            These colors will be used for all generated images. First color = primary, second = secondary, rest = accents.
          </p>
        </div>
      </div>

      {/* Key Features */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-gray-700">
          Key Features (Optional - leave blank if unsure)
        </h3>

        <div>
          <label
            htmlFor="feature1"
            className="block text-xs text-gray-500 mb-1"
          >
            Feature 1 - Primary benefit
          </label>
          <input
            type="text"
            id="feature1"
            name="feature1"
            value={formData.feature1}
            onChange={handleChange}
            disabled={disabled}
            placeholder="e.g., 5000 IU Vitamin D3 per serving"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
            maxLength={100}
          />
        </div>

        <div>
          <label
            htmlFor="feature2"
            className="block text-xs text-gray-500 mb-1"
          >
            Feature 2 - Secondary benefit
          </label>
          <input
            type="text"
            id="feature2"
            name="feature2"
            value={formData.feature2}
            onChange={handleChange}
            disabled={disabled}
            placeholder="e.g., Organic, non-GMO ingredients"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
            maxLength={100}
          />
        </div>

        <div>
          <label
            htmlFor="feature3"
            className="block text-xs text-gray-500 mb-1"
          >
            Feature 3 - Additional benefit
          </label>
          <input
            type="text"
            id="feature3"
            name="feature3"
            value={formData.feature3}
            onChange={handleChange}
            disabled={disabled}
            placeholder="e.g., Great-tasting natural berry flavor"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
            maxLength={100}
          />
        </div>
      </div>

      {/* Target Audience */}
      <div>
        <label
          htmlFor="targetAudience"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Target Audience (Optional)
        </label>
        <input
          type="text"
          id="targetAudience"
          name="targetAudience"
          value={formData.targetAudience}
          onChange={handleChange}
          disabled={disabled}
          placeholder="e.g., Health-conscious adults 30-55"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
          maxLength={150}
        />
      </div>

      {/* Keywords */}
      <div>
        <label
          htmlFor="keywords"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Target Keywords (Optional)
        </label>
        <textarea
          id="keywords"
          name="keywords"
          value={formData.keywords}
          onChange={handleChange}
          disabled={disabled}
          placeholder="Enter keywords separated by commas (e.g., vitamin d gummies, immune support, organic vitamins)"
          rows={2}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100"
        />
        <p className="text-xs text-gray-400 mt-1">
          Keywords help optimize images for Amazon search intent
        </p>
      </div>

      {/* Global Note for All Images */}
      <div className="bg-purple-50 rounded-lg p-4">
        <div className="flex justify-between items-center mb-1">
          <label
            htmlFor="globalNote"
            className="block text-sm font-medium text-gray-700"
          >
            Global Instructions for All Images (Optional)
          </label>
          <span className={`text-xs ${formData.globalNote.length > 1800 ? 'text-orange-600' : 'text-gray-400'}`}>
            {formData.globalNote.length}/2000
          </span>
        </div>
        <textarea
          id="globalNote"
          name="globalNote"
          value={formData.globalNote}
          onChange={handleChange}
          disabled={disabled}
          maxLength={2000}
          placeholder="e.g., Use warm lighting, avoid text overlays, keep backgrounds minimal, emphasize the golden color of the product..."
          rows={3}
          className="w-full px-4 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:bg-gray-100"
        />
        <p className="text-xs text-gray-500 mt-1">
          These instructions will be applied to ALL 5 generated images. Use this for style preferences, things to avoid, or specific requirements.
        </p>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={disabled || !isFormValid || isGenerating}
        className={`
          w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-200
          ${
            disabled || !isFormValid || isGenerating
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700 shadow-lg hover:shadow-xl'
          }
        `}
      >
        {isGenerating ? (
          <span className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            <span>Generating Previews...</span>
          </span>
        ) : (
          'Preview Styles'
        )}
      </button>
    </form>
  );
};
