import React from 'react';
import { cn, normalizeColors } from '@/lib/utils';
import type { UploadWithPreview } from '../ImageUploader';
import type { DesignFramework } from '@/api/types';

interface ComponentsPanelProps {
  /** Product images uploaded by user */
  productImages: UploadWithPreview[];
  /** Logo image (optional) */
  logoPreview?: string | null;
  /** Style reference image (optional) */
  styleReferencePreview?: string | null;
  /** Selected design framework */
  framework?: DesignFramework;
  /** Whether generation has started (dims unused components) */
  isGenerating?: boolean;
  className?: string;
}

/**
 * ComponentsPanel - Shows input assets that will be used for generation
 * These are the "ingredients" that flow into the generated images
 */
export const ComponentsPanel: React.FC<ComponentsPanelProps> = ({
  productImages,
  logoPreview,
  styleReferencePreview,
  framework,
  isGenerating = false,
  className,
}) => {
  const frameworkColors = framework ? normalizeColors(framework.colors) : [];
  const primaryColor = frameworkColors[0]?.hex || '#C85A35';

  return (
    <div className={cn('bg-slate-800/50 rounded-xl p-4 border border-slate-700', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-slate-300 flex items-center gap-2">
          <span className="text-lg">🧩</span>
          Components
        </h3>
        {framework && (
          <div className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded-full border-2 border-white/20"
              style={{ backgroundColor: primaryColor }}
              title={`Framework: ${framework.framework_name}`}
            />
            <span className="text-xs text-slate-400 truncate max-w-[120px]">
              {framework.framework_name}
            </span>
          </div>
        )}
      </div>

      {/* Components Grid */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Product Images */}
        {productImages.map((img, index) => (
          <div
            key={img.upload_id}
            className={cn(
              'relative group',
              isGenerating && 'opacity-60'
            )}
          >
            <div className="w-14 h-14 rounded-lg overflow-hidden border-2 border-slate-600 bg-slate-700">
              <img
                src={img.preview_url}
                alt={`Product ${index + 1}`}
                className="w-full h-full object-cover"
              />
            </div>
            <span className="absolute -bottom-1 -right-1 w-5 h-5 bg-slate-900 rounded-full text-[10px] font-bold text-white flex items-center justify-center border border-slate-600">
              {index + 1}
            </span>
            {/* Particle effect indicator when generating */}
            {isGenerating && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full animate-ping opacity-75" />
              </div>
            )}
          </div>
        ))}

        {/* Separator if we have additional components */}
        {(logoPreview || styleReferencePreview || framework) && productImages.length > 0 && (
          <div className="w-px h-10 bg-slate-600 mx-1" />
        )}

        {/* Logo */}
        {logoPreview && (
          <div className={cn('relative', isGenerating && 'opacity-60')}>
            <div className="w-14 h-14 rounded-lg overflow-hidden border-2 border-slate-600 bg-white p-1">
              <img
                src={logoPreview}
                alt="Logo"
                className="w-full h-full object-contain"
              />
            </div>
            <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 px-1.5 py-0.5 bg-slate-900 rounded text-[8px] font-medium text-slate-400 border border-slate-600">
              LOGO
            </span>
          </div>
        )}

        {/* Style Reference */}
        {styleReferencePreview && (
          <div className={cn('relative', isGenerating && 'opacity-60')}>
            <div className="w-14 h-14 rounded-lg overflow-hidden border-2 border-purple-500/50 bg-slate-700">
              <img
                src={styleReferencePreview}
                alt="Style Reference"
                className="w-full h-full object-cover"
              />
            </div>
            <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 px-1.5 py-0.5 bg-purple-900 rounded text-[8px] font-medium text-purple-300 border border-purple-500/50">
              STYLE
            </span>
          </div>
        )}

        {/* Framework Color Palette */}
        {framework && frameworkColors.length > 0 && (
          <div className={cn('flex flex-col gap-1', isGenerating && 'opacity-60')}>
            <div className="flex gap-0.5">
              {frameworkColors.slice(0, 5).map((color, idx) => (
                <div
                  key={idx}
                  className="w-6 h-6 rounded first:rounded-l-lg last:rounded-r-lg border border-white/10"
                  style={{ backgroundColor: color.hex }}
                  title={`${color.name || 'Color'}: ${color.hex}`}
                />
              ))}
            </div>
            <span className="text-[8px] text-slate-500 text-center">PALETTE</span>
          </div>
        )}

        {/* Empty state */}
        {productImages.length === 0 && !logoPreview && !styleReferencePreview && (
          <div className="flex items-center gap-2 text-slate-500 text-sm py-2">
            <span>📷</span>
            <span>Upload product photos to get started</span>
          </div>
        )}
      </div>

      {/* Generation hint */}
      {isGenerating && (
        <div className="mt-3 flex items-center gap-2 text-xs text-slate-400">
          <div className="flex gap-1">
            <span className="w-1.5 h-1.5 bg-redd-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 bg-redd-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-1.5 bg-redd-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span>Components flowing into generation...</span>
        </div>
      )}
    </div>
  );
};

export default ComponentsPanel;
