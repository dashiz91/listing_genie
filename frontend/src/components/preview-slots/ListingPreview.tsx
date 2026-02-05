import React, { useMemo } from 'react';
import { cn, normalizeColors } from '@/lib/utils';
import { ComponentsPanel } from './ComponentsPanel';
import { ImageSlot, SlotStatus } from './ImageSlot';
import { AplusSection, AplusModule } from './AplusSection';
import type { UploadWithPreview } from '../ImageUploader';
import type { SessionImage, DesignFramework, ImageType } from '@/api/types';

// Listing image slot configuration
const LISTING_SLOTS: { id: ImageType; label: string; description: string }[] = [
  { id: 'main', label: 'Main Image', description: 'Hero product shot' },
  { id: 'infographic_1', label: 'Infographic 1', description: 'Features callout' },
  { id: 'infographic_2', label: 'Infographic 2', description: 'Benefits grid' },
  { id: 'lifestyle', label: 'Lifestyle', description: 'Product in use' },
  { id: 'transformation', label: 'Transformation', description: 'Before/After life' },
  { id: 'comparison', label: 'Comparison', description: 'FOMO closing' },
];

interface ListingPreviewProps {
  /** Product images uploaded by user */
  productImages: UploadWithPreview[];
  /** Logo preview URL */
  logoPreview?: string | null;
  /** Style reference preview URL */
  styleReferencePreview?: string | null;
  /** Selected design framework */
  framework?: DesignFramework;
  /** Session ID for generation */
  sessionId?: string;
  /** Generated images from session */
  images: SessionImage[];
  /** A+ modules */
  aplusModules: AplusModule[];
  /** Get image URL for a type */
  getImageUrl: (imageType: string) => string;
  /** Currently generating image types */
  generatingTypes?: string[];
  /** Called when user clicks to generate a listing image */
  onGenerateImage?: (imageType: ImageType) => void;
  /** Called when user clicks to regenerate */
  onRegenerateImage?: (imageType: ImageType) => void;
  /** Called when user clicks to edit */
  onEditImage?: (imageType: ImageType) => void;
  /** Called to generate all listing images at once */
  onGenerateAll?: () => void;
  /** Called when user clicks to generate an A+ module */
  onGenerateAplusModule?: (moduleIndex: number) => void;
  /** Called when user clicks to regenerate an A+ module */
  onRegenerateAplusModule?: (moduleIndex: number, note?: string) => void;
  /** Whether we can start generating (has uploads + framework) */
  canGenerate?: boolean;
  /** Whether any generation is in progress */
  isGenerating?: boolean;
  className?: string;
}

/**
 * ListingPreview - Main preview component with components panel, listing slots, and A+ section
 */
export const ListingPreview: React.FC<ListingPreviewProps> = ({
  productImages,
  logoPreview,
  styleReferencePreview,
  framework,
  sessionId,
  images,
  aplusModules,
  getImageUrl,
  generatingTypes = [],
  onGenerateImage,
  onRegenerateImage,
  onEditImage,
  onGenerateAll,
  onGenerateAplusModule,
  onRegenerateAplusModule,
  canGenerate = false,
  isGenerating = false,
  className,
}) => {
  const frameworkColors = framework ? normalizeColors(framework.colors) : [];
  const accentColor = frameworkColors[0]?.hex || '#C85A35';

  // Map session images to slot statuses
  const slotStatuses = useMemo(() => {
    const statuses: Record<string, { status: SlotStatus; imageUrl?: string; error?: string }> = {};

    LISTING_SLOTS.forEach(slot => {
      const sessionImage = images.find(img => img.type === slot.id);
      const isGeneratingThis = generatingTypes.includes(slot.id);

      if (isGeneratingThis) {
        statuses[slot.id] = { status: 'generating' };
      } else if (sessionImage?.status === 'complete') {
        statuses[slot.id] = {
          status: 'complete',
          imageUrl: getImageUrl(slot.id),
        };
      } else if (sessionImage?.status === 'failed') {
        statuses[slot.id] = {
          status: 'error',
          error: sessionImage.error || 'Generation failed',
        };
      } else if (canGenerate) {
        // Ready to generate - session may or may not exist yet
        statuses[slot.id] = { status: 'ready' };
      } else {
        statuses[slot.id] = { status: 'empty' };
      }
    });

    return statuses;
  }, [images, generatingTypes, canGenerate, sessionId, getImageUrl]);

  // Count completed images
  const completedCount = useMemo(() => {
    return Object.values(slotStatuses).filter(s => s.status === 'complete').length;
  }, [slotStatuses]);

  return (
    <div className={cn('flex flex-col gap-6', className)}>
      {/* Components Panel */}
      <ComponentsPanel
        productImages={productImages}
        logoPreview={logoPreview}
        styleReferencePreview={styleReferencePreview}
        framework={framework}
        isGenerating={isGenerating}
      />

      {/* Listing Images Section */}
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🖼️</span>
            <h3 className="text-sm font-medium text-white">Listing Images</h3>
            <span className="text-xs text-slate-500">
              {completedCount}/{LISTING_SLOTS.length}
            </span>
          </div>

          {/* Generate All button */}
          {canGenerate && completedCount === 0 && !isGenerating && (
            <button
              onClick={onGenerateAll}
              className="px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2"
              style={{
                backgroundColor: accentColor,
                color: 'white',
              }}
            >
              <span>✨</span>
              <span>Generate All 6</span>
            </button>
          )}
        </div>

        {/* Slots Grid */}
        <div className="grid grid-cols-6 gap-3">
          {LISTING_SLOTS.map((slot, idx) => {
            const slotState = slotStatuses[slot.id];
            return (
              <ImageSlot
                key={slot.id}
                slotId={slot.id}
                label={slot.label}
                status={slotState.status}
                imageUrl={slotState.imageUrl}
                errorMessage={slotState.error}
                aspectRatio="1:1"
                accentColor={accentColor}
                canGenerate={canGenerate}
                onGenerate={() => {
                  // If no session yet, generate all to create session
                  // Otherwise generate this specific image
                  if (!sessionId) {
                    onGenerateAll?.();
                  } else {
                    onGenerateImage?.(slot.id);
                  }
                }}
                onRegenerate={() => onRegenerateImage?.(slot.id)}
                onEdit={() => onEditImage?.(slot.id)}
                slotNumber={idx + 1}
                size="md"
              />
            );
          })}
        </div>

        {/* Empty state hint */}
        {!canGenerate && productImages.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            <p className="text-sm">Upload product photos and select a framework to start generating</p>
          </div>
        )}
      </div>

      {/* A+ Content Section */}
      {aplusModules.length > 0 && (
        <AplusSection
          modules={aplusModules}
          sessionId={sessionId}
          accentColor={accentColor}
          onGenerateModule={onGenerateAplusModule}
          onRegenerateModule={onRegenerateAplusModule}
          isEnabled={!!sessionId}
        />
      )}

      {/* A+ Teaser when listing is complete but no modules added */}
      {sessionId && aplusModules.length === 0 && (
        <div className="bg-gradient-to-r from-purple-900/20 to-slate-800/50 border border-purple-500/30 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">✨</span>
            <div className="flex-1">
              <h4 className="text-sm font-medium text-white mb-1">Ready for A+ Content</h4>
              <p className="text-xs text-slate-400 mb-3">
                Create premium A+ modules that flow together seamlessly. Each module continues
                the design from the previous one for a cohesive brand story.
              </p>
              <button
                className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 text-sm font-medium rounded-lg transition-colors"
                onClick={() => {/* TODO: Add module picker */}}
              >
                + Add A+ Module
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ListingPreview;
