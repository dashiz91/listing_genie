import React, { useState, useCallback, useMemo } from 'react';
import { cn, normalizeColors } from '@/lib/utils';
import { apiClient, ASINImportResponse } from '@/api/client';
import type { DesignFramework } from '@/api/types';
import type { UploadWithPreview } from '../ImageUploader';
import { useCredits } from '@/contexts/CreditContext';
import { StyleLibrary } from '@/components/StyleLibrary';
import { Spinner } from '@/components/ui/spinner';
import { WorkflowStepper, type WorkflowStep } from '@/components/ui/workflow-stepper';
import type { WorkshopFormData } from '../split-layout/WorkshopPanel';

interface CreatorViewProps {
  // Upload
  uploads: UploadWithPreview[];
  onUploadsChange: (uploads: UploadWithPreview[]) => void;
  maxImages?: number;

  // Form data
  formData: WorkshopFormData;
  onFormChange: (data: Partial<WorkshopFormData>) => void;

  // Framework
  frameworks: DesignFramework[];
  selectedFramework: DesignFramework | null;
  onSelectFramework: (framework: DesignFramework) => void;
  productAnalysis: string;

  // Actions
  onAnalyze: () => void;
  onGenerate: () => void;
  canAnalyze: boolean;
  canGenerate: boolean;
  isAnalyzing: boolean;
  isGenerating: boolean;

  // Style ref
  useOriginalStyleRef: boolean;
  onToggleOriginalStyleRef: (value: boolean) => void;

  // Sheet
  onOpenAdvancedSettings: () => void;

  // Start over
  onStartOver: () => void;

  // Workflow stepper
  workflowSteps?: WorkflowStep[];
  onImportStart?: () => void;
  onImportEnd?: () => void;
}

export const CreatorView: React.FC<CreatorViewProps> = ({
  uploads,
  onUploadsChange,
  maxImages = 5,
  formData,
  onFormChange,
  frameworks,
  selectedFramework,
  onSelectFramework,
  productAnalysis,
  onAnalyze,
  onGenerate,
  canAnalyze,
  canGenerate,
  isAnalyzing,
  isGenerating,
  useOriginalStyleRef,
  onToggleOriginalStyleRef,
  onOpenAdvancedSettings,
  onStartOver,
  workflowSteps,
  onImportStart,
  onImportEnd,
}) => {
  const { balance, isAdmin } = useCredits();

  // ASIN Import state
  const [asinInput, setAsinInput] = useState('');
  const [isImportingAsin, setIsImportingAsin] = useState(false);
  const [asinError, setAsinError] = useState<string | null>(null);
  const [showAsinImport, setShowAsinImport] = useState(false);

  // Style Library
  const [isStyleLibraryOpen, setIsStyleLibraryOpen] = useState(false);
  const [selectedStyleId, setSelectedStyleId] = useState<string | undefined>(undefined);

  // Framework detail modal
  const [frameworkDetailIndex, setFrameworkDetailIndex] = useState<number | null>(null);

  // Credit cost calculations
  const analyzeCost = useMemo(() => {
    const numPreviews = formData.styleCount;
    return 1 + numPreviews;
  }, [formData.styleCount]);

  const generateCost = useMemo(() => {
    const model = formData.imageModel;
    const modelCost = model.includes('flash') ? 1 : 3;
    return 6 * modelCost;
  }, [formData.imageModel]);

  const canAffordAnalyze = isAdmin || balance >= analyzeCost;
  const canAffordGenerate = isAdmin || balance >= generateCost;

  // Handle ASIN import
  const handleAsinImport = async () => {
    if (!asinInput.trim()) {
      setAsinError('Please enter an ASIN');
      return;
    }

    setIsImportingAsin(true);
    setAsinError(null);
    onImportStart?.();

    try {
      const result: ASINImportResponse = await apiClient.importFromAsin(asinInput.trim(), {
        downloadImages: true,
        maxImages: 3,
      });

      setAsinInput('');

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

      if (result.title) await typeText('productTitle', result.title, 6);
      if (result.brand_name) await typeText('brandName', result.brand_name, 10);
      if (result.feature_1) await typeText('feature1', result.feature_1, 4);
      if (result.feature_2) await typeText('feature2', result.feature_2, 4);
      if (result.feature_3) await typeText('feature3', result.feature_3, 4);
    } catch (error: unknown) {
      const errMsg = error instanceof Error ? error.message : 'Failed to import product';
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setAsinError(axiosError.response?.data?.detail || errMsg);
    } finally {
      setIsImportingAsin(false);
      onImportEnd?.();
    }
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

  // Count of advanced settings that have been filled in
  const advancedSettingsCount = useMemo(() => {
    let count = 0;
    if (formData.feature1 || formData.feature2 || formData.feature3) count++;
    if (formData.targetAudience) count++;
    if (formData.brandName) count++;
    if (formData.logoPreview) count++;
    if (formData.styleReferencePreview) count++;
    if (formData.brandColors.length > 0) count++;
    if (formData.colorPalette.length > 0) count++;
    if (formData.globalNote) count++;
    return count;
  }, [formData]);

  return (
    <div className="flex-1 overflow-auto">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 pb-24">
        {/* Workflow stepper */}
        {workflowSteps && <WorkflowStepper steps={workflowSteps} className="mb-4" />}

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Create your Amazon listing
          </h1>
          <p className="text-slate-400">
            Upload product photos, enter a title, and let AI design your complete listing
          </p>
        </div>

        {/* Upload Zone */}
        <div className="mb-6">
          {uploads.length > 0 ? (
            <div className="space-y-3">
              <div className="grid grid-cols-3 sm:grid-cols-5 gap-3">
                {uploads.map((upload, index) => (
                  <div
                    key={upload.upload_id}
                    className="relative group rounded-xl overflow-hidden border-2 border-slate-600 bg-slate-800/50 aspect-square"
                  >
                    <img
                      src={upload.preview_url}
                      alt={`Product ${index + 1}`}
                      className="w-full h-full object-contain"
                    />
                    {index === 0 && (
                      <div className="absolute top-1.5 left-1.5 bg-redd-500 text-white text-[9px] px-1.5 py-0.5 rounded-md font-medium">
                        Primary
                      </div>
                    )}
                    <button
                      onClick={() => removeUpload(upload.upload_id)}
                      className="absolute top-1.5 right-1.5 bg-red-600/90 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
                {/* Add more button */}
                {uploads.length < maxImages && (
                  <label className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-600 cursor-pointer hover:border-redd-500/50 transition-colors bg-slate-800/30 aspect-square">
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/jpg"
                      multiple
                      onChange={(e) => handleImageFiles(e.target.files)}
                      className="hidden"
                    />
                    <svg className="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span className="text-[10px] text-slate-500 mt-1">Add more</span>
                  </label>
                )}
              </div>
            </div>
          ) : (
            <label className="flex flex-col items-center justify-center py-12 px-6 border-2 border-dashed border-slate-600 rounded-2xl cursor-pointer hover:border-redd-500/50 transition-all bg-slate-800/30 hover:bg-slate-800/50">
              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                multiple
                onChange={(e) => handleImageFiles(e.target.files)}
                className="hidden"
              />
              <div className="w-16 h-16 rounded-full bg-slate-700/50 flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <span className="text-base text-slate-300 font-medium mb-1">
                Upload Product Photos
              </span>
              <span className="text-sm text-slate-500">
                Drag & drop or <span className="text-redd-400">browse</span> (up to {maxImages} images)
              </span>
            </label>
          )}
        </div>

        {/* ASIN Import - collapsible */}
        <div className="mb-6 text-center">
          <button
            type="button"
            onClick={() => setShowAsinImport(!showAsinImport)}
            className="text-sm text-slate-500 hover:text-slate-300 transition-colors inline-flex items-center gap-1.5"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            or import from ASIN
          </button>
          {showAsinImport && (
            <div className="mt-3 max-w-md mx-auto">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={asinInput}
                  onChange={(e) => {
                    setAsinInput(e.target.value);
                    setAsinError(null);
                  }}
                  placeholder="Enter ASIN (e.g., B09V3K6QFP)"
                  className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 text-sm focus:ring-2 focus:ring-redd-500 focus:border-transparent"
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
                  className="px-4 py-2 bg-redd-500 hover:bg-redd-600 disabled:bg-slate-600 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
                >
                  {isImportingAsin ? 'Importing...' : 'Import'}
                </button>
              </div>
              {asinError && (
                <p className="mt-2 text-xs text-red-400">{asinError}</p>
              )}
            </div>
          )}
        </div>

        {/* Product Title */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Product Title <span className="text-redd-500">*</span>
          </label>
          <input
            type="text"
            value={formData.productTitle}
            onChange={(e) => onFormChange({ productTitle: e.target.value })}
            placeholder="e.g., Organic Vitamin D3 Gummies - Natural Immune Support"
            className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-xl text-white placeholder-slate-500 text-base focus:ring-2 focus:ring-redd-500 focus:border-transparent transition-all"
            maxLength={200}
          />
        </div>

        {/* Quick Settings Row */}
        <div className="flex items-center justify-between mb-6 gap-4 flex-wrap">
          {/* Advanced Settings button */}
          <button
            type="button"
            onClick={onOpenAdvancedSettings}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm text-slate-300 hover:text-white bg-slate-800 border border-slate-600 hover:border-slate-500 transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Advanced Settings
            {advancedSettingsCount > 0 && (
              <span className="px-1.5 py-0.5 bg-redd-500/20 text-redd-400 text-[10px] rounded-full font-medium">
                {advancedSettingsCount}
              </span>
            )}
          </button>

          {/* Model + Style Count selectors */}
          <div className="flex items-center gap-3">
            {/* Model toggle */}
            <div className={cn(
              "flex items-center bg-slate-800 border border-slate-600 rounded-lg p-1 gap-0.5",
              isGenerating && "opacity-50 pointer-events-none"
            )}>
              {([
                { value: 'gemini-2.5-flash-image', label: 'Flash', icon: '\u26A1', cost: '1' },
                { value: 'gemini-3-pro-image-preview', label: 'Pro', icon: '\u2728', cost: '3' },
              ] as const).map((opt) => {
                const isActive = formData.imageModel === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => onFormChange({ imageModel: opt.value })}
                    disabled={isGenerating}
                    className={cn(
                      'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all',
                      isActive
                        ? opt.value.includes('pro')
                          ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-sm'
                          : 'bg-slate-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-white hover:bg-slate-700'
                    )}
                    title={`${opt.label} — ${opt.cost} credit${opt.cost !== '1' ? 's' : ''}/image`}
                  >
                    <span className="text-[11px]">{opt.icon}</span>
                    {opt.label}
                    <span className={cn(
                      'text-[10px] tabular-nums',
                      isActive ? 'text-white/70' : 'text-slate-500'
                    )}>{opt.cost}cr</span>
                  </button>
                );
              })}
            </div>

            {/* Style count */}
            {frameworks.length === 0 && (
              <div className="flex items-center gap-1 bg-slate-800 border border-slate-600 rounded-lg p-1">
                {[1, 2, 3, 4].map((count) => (
                  <button
                    key={count}
                    onClick={() => onFormChange({ styleCount: count })}
                    className={cn(
                      'w-7 h-7 rounded text-xs font-medium transition-all',
                      formData.styleCount === count
                        ? 'bg-redd-500 text-white'
                        : 'text-slate-400 hover:text-white hover:bg-slate-700'
                    )}
                    title={`${count} style${count > 1 ? 's' : ''}`}
                  >
                    {count}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Style Reference Preview (if set via advanced settings) */}
        {formData.styleReferencePreview && (
          <div className="mb-6 flex items-center gap-3 bg-slate-800/50 border border-slate-600 rounded-xl p-3">
            <img
              src={formData.styleReferencePreview}
              alt="Style reference"
              className="w-12 h-12 object-cover rounded-lg"
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-white">Style Reference</p>
              <p className="text-[10px] text-slate-400 truncate">
                {formData.styleReferenceFile?.name || 'Pre-made style'}
              </p>
            </div>
            <button
              onClick={() => {
                onFormChange({ styleReferenceFile: null, styleReferencePreview: null });
                setSelectedStyleId(undefined);
              }}
              className="text-slate-400 hover:text-red-400 text-xs shrink-0"
            >
              Remove
            </button>
          </div>
        )}

        {/* Use exact style toggle */}
        {formData.styleReferencePreview && (
          <div className="mb-6">
            <button
              onClick={() => onToggleOriginalStyleRef(!useOriginalStyleRef)}
              className={cn(
                'w-full flex items-center gap-3 p-3 rounded-xl border transition-all text-left',
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
                    ? '0 preview credits — your image is used directly as reference'
                    : '1-4 preview credits — AI generates styled previews first'}
                </p>
              </div>
            </button>
          </div>
        )}

        {/* Primary CTA - Analyze */}
        {frameworks.length === 0 ? (
          <div className="mb-8">
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
                  <Spinner size="sm" className="text-white" />
                  Analyzing Product...
                </span>
              ) : (
                useOriginalStyleRef
                  ? 'Analyze & Create Framework'
                  : `Preview ${formData.styleCount} Design Style${formData.styleCount > 1 ? 's' : ''}`
              )}
            </button>

            {/* Cost preview */}
            {!isAnalyzing && canAnalyze && (
              <div className="text-center mt-2">
                {isAdmin ? (
                  <p className="text-xs text-amber-400/80">No credits used (Admin)</p>
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

            {/* Helper text */}
            {!canAnalyze && !isAnalyzing && (
              <p className="text-center text-xs text-slate-500 mt-2">
                Upload photos and add a title to continue
              </p>
            )}
          </div>
        ) : null}

        {/* Analysis skeleton during analyzing */}
        {isAnalyzing && frameworks.length === 0 && (
          <div className="mb-8 space-y-4">
            {/* AI Analysis skeleton */}
            <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700 animate-pulse">
              <div className="h-3 w-20 bg-slate-700 rounded mb-2" />
              <div className="h-4 w-full bg-slate-700 rounded mb-1" />
              <div className="h-4 w-3/4 bg-slate-700 rounded" />
            </div>

            {/* Framework cards skeleton */}
            <div className="grid grid-cols-2 gap-4">
              {Array.from({ length: formData.styleCount }, (_, i) => (
                <div key={i} className="rounded-xl border-2 border-slate-700 overflow-hidden">
                  <div className="aspect-square bg-slate-800 relative overflow-hidden">
                    <div
                      className="absolute inset-0 animate-shimmer"
                      style={{
                        background: 'linear-gradient(90deg, transparent 0%, rgba(200,90,53,0.2) 50%, transparent 100%)',
                        backgroundSize: '200% 100%',
                      }}
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <Spinner size="lg" className="text-redd-500 mx-auto mb-2" />
                        <span className="text-xs text-slate-400">Creating style {i + 1}...</span>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-slate-800">
                    <div className="h-3 w-2/3 bg-slate-700 rounded animate-pulse" />
                    <div className="flex gap-1 mt-2">
                      {[1, 2, 3, 4].map((j) => (
                        <div key={j} className="w-4 h-4 rounded-full bg-slate-700 animate-pulse" />
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Frameworks section */}
        {!isAnalyzing && frameworks.length > 0 && (
          <div className="mb-8">
            {/* Product Analysis */}
            {productAnalysis && (
              <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700 mb-4">
                <p className="text-xs font-medium text-redd-400 mb-1">AI Analysis</p>
                <p className="text-sm text-slate-300">{productAnalysis}</p>
              </div>
            )}

            {/* Framework Cards */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              {frameworks.map((framework, fwIndex) => {
                const isSelected = selectedFramework?.framework_id === framework.framework_id;
                return (
                  <div
                    key={framework.framework_id}
                    className={cn(
                      'group relative rounded-xl border-2 overflow-hidden transition-all cursor-pointer',
                      isSelected
                        ? 'border-redd-500 ring-2 ring-redd-500/30'
                        : 'border-slate-600 hover:border-slate-500'
                    )}
                    onClick={() => onSelectFramework(framework)}
                  >
                    <div className="aspect-square bg-slate-800 relative">
                      {framework.preview_url ? (
                        <img
                          src={framework.preview_url.startsWith('http') ? framework.preview_url : `${import.meta.env.VITE_API_URL || ''}${framework.preview_url}`}
                          alt={framework.framework_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Spinner size="md" className="text-redd-500" />
                        </div>
                      )}
                      {isSelected && (
                        <div className="absolute top-2 right-2 w-7 h-7 bg-redd-500 rounded-full flex items-center justify-center shadow-lg">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                      {/* Hover overlay */}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        <button
                          onClick={(e) => { e.stopPropagation(); setFrameworkDetailIndex(fwIndex); }}
                          className="px-3 py-1.5 bg-white/90 hover:bg-white rounded-lg text-xs font-medium text-slate-800 transition-colors"
                        >
                          Details
                        </button>
                      </div>
                    </div>
                    <div className="p-3 bg-slate-800">
                      <p className="text-sm font-medium text-white truncate">{framework.framework_name}</p>
                      <div className="flex gap-1.5 mt-1.5">
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
                  <Spinner size="sm" className="text-white" />
                  Generating Images...
                </span>
              ) : selectedFramework ? (
                'Generate All 6 Images'
              ) : (
                'Select a Framework'
              )}
            </button>

            {/* Cost preview */}
            {!isGenerating && selectedFramework && (
              <div className="text-center mt-2 space-y-1">
                {isAdmin ? (
                  <p className="text-xs text-amber-400/80">No credits used (Admin)</p>
                ) : canAffordGenerate ? (
                  <p className="text-xs text-slate-400">
                    <span className="text-redd-400 font-medium">{generateCost}</span> credits
                    <span className="text-slate-500"> ({balance - generateCost} remaining)</span>
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
                        Switch to Flash (6 credits)
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Re-plan styles */}
            <div className="flex items-center justify-center gap-3 mt-3">
              <button
                onClick={onAnalyze}
                disabled={isAnalyzing || isGenerating}
                className="text-sm text-slate-400 hover:text-white transition-colors inline-flex items-center gap-1.5"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Re-plan styles
              </button>
              <span className="text-slate-700">|</span>
              <button
                onClick={onStartOver}
                className="text-sm text-slate-400 hover:text-white transition-colors"
              >
                Start over
              </button>
            </div>
          </div>
        )}

        {/* Divider */}
        <div className="border-t border-slate-700/50 my-6" />

        {/* Browse Styles Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Browse Styles</h3>
            <button
              type="button"
              onClick={() => setIsStyleLibraryOpen(true)}
              className="text-sm text-redd-400 hover:text-redd-300 transition-colors"
            >
              View all
            </button>
          </div>
          <p className="text-sm text-slate-400 mb-4">
            Free pre-made styles — select one to set your visual direction
          </p>
          <button
            type="button"
            onClick={() => setIsStyleLibraryOpen(true)}
            className="w-full flex items-center justify-center gap-3 p-6 bg-gradient-to-r from-redd-500/10 to-redd-600/10 border-2 border-dashed border-redd-500/30 rounded-xl hover:border-redd-500/50 hover:from-redd-500/15 hover:to-redd-600/15 transition-all"
          >
            <span className="text-2xl">🎨</span>
            <div className="text-left">
              <span className="text-sm font-medium text-white block">Open Style Library</span>
              <span className="text-xs text-slate-400">11 curated styles across 6 categories</span>
            </div>
          </button>
        </div>

        {/* Framework Detail Modal */}
        {frameworkDetailIndex !== null && frameworks[frameworkDetailIndex] && (() => {
          const fw = frameworks[frameworkDetailIndex];
          return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm" onClick={() => setFrameworkDetailIndex(null)}>
              <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-lg w-full mx-4 max-h-[85vh] overflow-y-auto shadow-2xl" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between p-4 border-b border-slate-700 sticky top-0 bg-slate-800 z-10">
                  <h3 className="text-lg font-semibold text-white">{fw.framework_name}</h3>
                  <button onClick={() => setFrameworkDetailIndex(null)} className="p-1 text-slate-400 hover:text-white transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div className="p-4 space-y-4">
                  {fw.design_philosophy && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase mb-1">Design Philosophy</h4>
                      <p className="text-sm text-slate-300 italic">"{fw.design_philosophy}"</p>
                    </div>
                  )}
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
                  {fw.typography && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase mb-1">Typography</h4>
                      <p className="text-sm text-slate-300">Headline: {fw.typography.headline_font}</p>
                      {fw.typography.body_font && <p className="text-sm text-slate-300">Body: {fw.typography.body_font}</p>}
                    </div>
                  )}
                  {fw.visual_treatment && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2">Visual Treatment</h4>
                      <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                        <div><span className="text-slate-300 font-medium">Lighting:</span> <span className="text-slate-400">{fw.visual_treatment.lighting_style}</span></div>
                        <div><span className="text-slate-300 font-medium">Background:</span> <span className="text-slate-400">{fw.visual_treatment.background_treatment}</span></div>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {fw.visual_treatment.mood_keywords.map((kw, i) => (
                          <span key={i} className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300">{kw}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {fw.rationale && (
                    <div className="bg-slate-700/50 p-3 rounded-lg border border-slate-600">
                      <h4 className="text-xs font-semibold text-slate-400 uppercase mb-1">Why This Works</h4>
                      <p className="text-xs text-slate-300">{fw.rationale}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })()}
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
