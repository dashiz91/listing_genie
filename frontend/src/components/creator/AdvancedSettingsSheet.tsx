import React, { useState, useCallback, useRef } from 'react';
import { cn } from '@/lib/utils';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';
import { StyleLibrary } from '@/components/StyleLibrary';
import type { WorkshopFormData } from '../split-layout/WorkshopPanel';

// Default colors for quick picks
const DEFAULT_COLORS = ['#4CAF50', '#2196F3', '#FF9800'];

interface AdvancedSettingsSheetProps {
  open: boolean;
  onClose: () => void;
  formData: WorkshopFormData;
  onFormChange: (data: Partial<WorkshopFormData>) => void;
  useOriginalStyleRef: boolean;
  onToggleOriginalStyleRef: (value: boolean) => void;
}

export const AdvancedSettingsSheet: React.FC<AdvancedSettingsSheetProps> = ({
  open,
  onClose,
  formData,
  onFormChange,
  useOriginalStyleRef,
  onToggleOriginalStyleRef,
}) => {
  // Color input state
  const [brandColorInput, setBrandColorInput] = useState('#4CAF50');
  const [paletteColorInput, setPaletteColorInput] = useState('#2196F3');

  // File input refs (explicit click needed inside Radix Sheet portal)
  const logoInputRef = useRef<HTMLInputElement>(null);
  const styleInputRef = useRef<HTMLInputElement>(null);

  // Style Library
  const [isStyleLibraryOpen, setIsStyleLibraryOpen] = useState(false);
  const [selectedStyleId, setSelectedStyleId] = useState<string | undefined>(undefined);

  // Handle logo change
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

  // Handle style reference change
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

  // Brand colors
  const addBrandColor = () => {
    if (formData.brandColors.length < 3 && !formData.brandColors.includes(brandColorInput)) {
      onFormChange({ brandColors: [...formData.brandColors, brandColorInput] });
    }
  };

  const removeBrandColor = (color: string) => {
    onFormChange({ brandColors: formData.brandColors.filter((c) => c !== color) });
  };

  // Palette colors
  const addPaletteColor = () => {
    if (formData.colorPalette.length < 3 && !formData.colorPalette.includes(paletteColorInput)) {
      onFormChange({ colorPalette: [...formData.colorPalette, paletteColorInput] });
    }
  };

  const removePaletteColor = (color: string) => {
    onFormChange({ colorPalette: formData.colorPalette.filter((c) => c !== color) });
  };

  // Handle style library selection
  const handleStyleLibrarySelect = useCallback(async (style: { id: string; name: string; preview_image: string; colors: string[] }) => {
    setSelectedStyleId(style.id);
    setIsStyleLibraryOpen(false);

    try {
      const response = await fetch(style.preview_image);
      if (!response.ok) throw new Error('Failed to load style image');

      const blob = await response.blob();
      const file = new File([blob], `style-${style.id}.png`, { type: 'image/png' });

      const reader = new FileReader();
      reader.onloadend = () => {
        onFormChange({
          styleReferenceFile: file,
          styleReferencePreview: reader.result as string,
          colorPalette: style.colors.slice(0, 3),
        });
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error('Failed to load style:', err);
      onFormChange({
        styleReferencePreview: style.preview_image,
        colorPalette: style.colors.slice(0, 3),
      });
    }
  }, [onFormChange]);

  return (
    <>
      <Sheet open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
        <SheetContent side="right" className="sm:max-w-lg w-full bg-slate-900 border-slate-700 overflow-y-auto">
          <SheetHeader className="mb-6">
            <SheetTitle className="text-white">Advanced Settings</SheetTitle>
            <SheetDescription className="text-slate-400">
              Fine-tune your listing generation with additional details
            </SheetDescription>
          </SheetHeader>

          <div className="space-y-8 pb-8">
            {/* PRODUCT DETAILS */}
            <section>
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
                Product Details
              </h3>
              <div className="space-y-3">
                <div className="space-y-2">
                  <label className="block text-sm text-slate-300">Key Features</label>
                  <input
                    type="text"
                    value={formData.feature1}
                    onChange={(e) => onFormChange({ feature1: e.target.value })}
                    placeholder="Feature 1 - Primary benefit"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:ring-2 focus:ring-redd-500 focus:border-transparent"
                    maxLength={100}
                  />
                  <input
                    type="text"
                    value={formData.feature2}
                    onChange={(e) => onFormChange({ feature2: e.target.value })}
                    placeholder="Feature 2 - Secondary benefit"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:ring-2 focus:ring-redd-500 focus:border-transparent"
                    maxLength={100}
                  />
                  <input
                    type="text"
                    value={formData.feature3}
                    onChange={(e) => onFormChange({ feature3: e.target.value })}
                    placeholder="Feature 3 - Additional benefit"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:ring-2 focus:ring-redd-500 focus:border-transparent"
                    maxLength={100}
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-300 mb-1">Target Audience</label>
                  <input
                    type="text"
                    value={formData.targetAudience}
                    onChange={(e) => onFormChange({ targetAudience: e.target.value })}
                    placeholder="e.g., Health-conscious adults 30-55"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:ring-2 focus:ring-redd-500 focus:border-transparent"
                    maxLength={150}
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-300 mb-1">Keywords</label>
                  <input
                    type="text"
                    value={formData.keywords}
                    onChange={(e) => onFormChange({ keywords: e.target.value })}
                    placeholder="e.g., organic, natural, immune support"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:ring-2 focus:ring-redd-500 focus:border-transparent"
                  />
                  <p className="text-[10px] text-slate-500 mt-1">Comma-separated keywords</p>
                </div>
              </div>
            </section>

            <div className="border-t border-slate-700/50" />

            {/* BRAND IDENTITY */}
            <section>
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
                Brand Identity
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Brand Name</label>
                  <input
                    type="text"
                    value={formData.brandName}
                    onChange={(e) => onFormChange({ brandName: e.target.value })}
                    placeholder="e.g., VitaGlow"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:ring-2 focus:ring-redd-500 focus:border-transparent"
                    maxLength={100}
                  />
                </div>

                {/* Logo */}
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Brand Logo</label>
                  {formData.logoPreview ? (
                    <div className="flex items-center gap-3 bg-slate-800 border border-slate-600 rounded-lg p-3">
                      <img
                        src={formData.logoPreview}
                        alt="Logo preview"
                        className="w-12 h-12 object-contain rounded"
                      />
                      <div className="flex-1 text-sm text-white truncate">
                        {formData.logoFile?.name || 'Logo'}
                      </div>
                      <button
                        onClick={() => onFormChange({ logoFile: null, logoPreview: null })}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                  ) : (
                    <div
                      onClick={() => logoInputRef.current?.click()}
                      className="flex items-center justify-center p-4 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-slate-500 transition-colors"
                    >
                      <input
                        ref={logoInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleLogoChange}
                        className="hidden"
                      />
                      <span className="text-sm text-slate-400">Click to upload logo</span>
                    </div>
                  )}
                </div>

                {/* Brand Colors */}
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Brand Colors (up to 3)</label>
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
                          x
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
                      className="flex-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-sm text-white placeholder-slate-500"
                      maxLength={7}
                    />
                    <button
                      onClick={addBrandColor}
                      disabled={formData.brandColors.length >= 3}
                      className="px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
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
            </section>

            <div className="border-t border-slate-700/50" />

            {/* STYLE & COLORS */}
            <section>
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
                Style & Colors
              </h3>
              <div className="space-y-4">
                {/* Style Reference */}
                <div>
                  <label className="block text-sm text-slate-300 mb-2">Style Reference Image</label>
                  {formData.styleReferencePreview ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-3 bg-slate-800 border border-slate-600 rounded-lg p-3">
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
                      <button
                        type="button"
                        onClick={() => setIsStyleLibraryOpen(true)}
                        className="w-full flex items-center justify-center gap-1.5 py-2 text-xs text-slate-400 hover:text-redd-400 transition-colors"
                      >
                        Browse more styles
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <button
                        type="button"
                        onClick={() => setIsStyleLibraryOpen(true)}
                        className="w-full flex items-center justify-center gap-2 p-4 bg-gradient-to-r from-redd-500/20 to-redd-600/20 border-2 border-redd-500/40 rounded-lg hover:border-redd-500/60 transition-all"
                      >
                        <span className="text-xl">🎨</span>
                        <div className="text-left">
                          <span className="text-sm font-medium text-white block">Browse Style Library</span>
                          <span className="text-xs text-slate-400">Free pre-made styles</span>
                        </div>
                      </button>

                      <div className="relative flex items-center">
                        <div className="flex-grow border-t border-slate-700"></div>
                        <span className="px-3 text-xs text-slate-500">or upload your own</span>
                        <div className="flex-grow border-t border-slate-700"></div>
                      </div>

                      <div
                        onClick={() => styleInputRef.current?.click()}
                        className="flex flex-col items-center justify-center p-3 border-2 border-dashed border-slate-600 rounded-lg cursor-pointer hover:border-slate-500 transition-colors bg-slate-800/30"
                      >
                        <input
                          ref={styleInputRef}
                          type="file"
                          accept="image/*"
                          onChange={handleStyleRefChange}
                          className="hidden"
                        />
                        <svg className="w-5 h-5 text-slate-400 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                        </svg>
                        <span className="text-xs text-slate-400">Upload custom style image</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Use exact style toggle */}
                {formData.styleReferencePreview && (
                  <button
                    onClick={() => onToggleOriginalStyleRef(!useOriginalStyleRef)}
                    className={cn(
                      'w-full flex items-center gap-3 p-3 rounded-lg border transition-all text-left',
                      useOriginalStyleRef
                        ? 'bg-redd-500/10 border-redd-500/40'
                        : 'bg-slate-800/50 border-slate-600 hover:border-slate-500'
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
                          ? '0 preview credits — your image is used directly'
                          : '1-4 preview credits — AI generates styled previews'}
                      </p>
                    </div>
                  </button>
                )}

                {/* Color Count */}
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Number of Colors</label>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => onFormChange({ colorCount: null })}
                      className={cn(
                        'px-3 py-2 rounded-lg text-sm',
                        formData.colorCount === null
                          ? 'bg-redd-500 text-white'
                          : 'bg-slate-800 border border-slate-600 text-slate-300 hover:bg-slate-700'
                      )}
                    >
                      AI Decides
                    </button>
                    {[2, 3].map((count) => (
                      <button
                        key={count}
                        onClick={() => onFormChange({ colorCount: count })}
                        className={cn(
                          'w-10 h-10 rounded-lg text-sm font-medium',
                          formData.colorCount === count
                            ? 'bg-redd-500 text-white'
                            : 'bg-slate-800 border border-slate-600 text-slate-300 hover:bg-slate-700'
                        )}
                      >
                        {count}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Color Palette */}
                <div>
                  <label className="block text-sm text-slate-300 mb-1">
                    Color Palette (leave empty for AI)
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
                          x
                        </button>
                      </div>
                    ))}
                  </div>
                  {formData.colorPalette.length < 3 && (
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
                        className="flex-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-sm text-white placeholder-slate-500"
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
            </section>

            <div className="border-t border-slate-700/50" />

            {/* GLOBAL INSTRUCTIONS */}
            <section>
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
                Global Instructions
              </h3>
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-sm text-slate-300">
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
                  rows={4}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-redd-500 focus:border-transparent resize-none text-sm"
                />
              </div>
            </section>
          </div>

          {/* Apply button at bottom */}
          <div className="sticky bottom-0 pt-4 pb-2 bg-slate-900 border-t border-slate-700">
            <button
              onClick={onClose}
              className="w-full py-3 px-4 bg-redd-500 hover:bg-redd-600 text-white font-medium rounded-lg transition-colors"
            >
              Apply Settings
            </button>
          </div>
        </SheetContent>
      </Sheet>

      {/* Style Library Sheet (nested) */}
      <StyleLibrary
        open={isStyleLibraryOpen}
        onClose={() => setIsStyleLibraryOpen(false)}
        onSelectStyle={handleStyleLibrarySelect}
        selectedStyleId={selectedStyleId}
      />
    </>
  );
};
