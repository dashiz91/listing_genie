import React from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
  horizontalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';
import type { SessionImage } from '@/api/types';

interface ThumbnailGalleryProps {
  images: SessionImage[];
  selectedType: string;
  onSelect: (imageType: string) => void;
  getImageUrl: (imageType: string) => string;
  onReorder?: (newOrder: string[]) => void;
  className?: string;
}

// Image type order for Amazon listing (1-6)
const IMAGE_ORDER = ['main', 'infographic_1', 'infographic_2', 'lifestyle', 'transformation', 'comparison'];

// Sortable Thumbnail Item
interface SortableThumbnailProps {
  image: SessionImage;
  index: number;
  isSelected: boolean;
  isComplete: boolean;
  isProcessing: boolean;
  onSelect: () => void;
  getImageUrl: (imageType: string) => string;
  isDraggingEnabled: boolean;
}

const SortableThumbnail: React.FC<SortableThumbnailProps> = ({
  image,
  index,
  isSelected,
  isComplete,
  isProcessing,
  onSelect,
  getImageUrl,
  isDraggingEnabled,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: image.type,
    disabled: !isDraggingEnabled || !isComplete,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 10 : 'auto',
    opacity: isDragging ? 0.8 : 1,
  };

  // Extract role from attributes to avoid duplicate property
  const { role: _role, ...restAttributes } = attributes;

  return (
    <button
      ref={setNodeRef}
      style={style}
      onClick={() => onSelect()}
      role="option"
      aria-selected={isSelected}
      aria-label={`${image.label || `Image ${index + 1}`}${isSelected ? ' (selected)' : ''}${isProcessing ? ' (loading)' : ''}${isDraggingEnabled && isComplete ? ' - drag to reorder' : ''}`}
      className={cn(
        'relative w-14 h-14 md:w-16 md:h-16 flex-shrink-0 rounded-lg overflow-hidden border-2 transition-all duration-200 cursor-pointer',
        'focus:outline-none focus:ring-2 focus:ring-redd-500 focus:ring-offset-2 focus:ring-offset-slate-50',
        isSelected
          ? 'border-redd-500 ring-2 ring-redd-500/30 scale-105'
          : 'border-slate-300 hover:border-slate-400 hover:scale-102',
        !isComplete && !isProcessing && 'opacity-70',
        isDragging && 'shadow-lg scale-110 cursor-grabbing',
        isDraggingEnabled && isComplete && !isDragging && 'cursor-grab'
      )}
      {...(isDraggingEnabled && isComplete ? { ...restAttributes, ...listeners } : {})}
    >
      {/* Image number badge */}
      <span
        className={cn(
          'absolute top-0.5 left-0.5 z-10 w-5 h-5 rounded text-xs font-medium',
          'flex items-center justify-center',
          isSelected
            ? 'bg-redd-500 text-white'
            : 'bg-slate-800/80 text-slate-300'
        )}
      >
        {index + 1}
      </span>

      {/* Thumbnail image or status indicator */}
      {isComplete ? (
        <img
          src={getImageUrl(image.type)}
          alt={image.label}
          className="w-full h-full object-cover"
          draggable={false}
          onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
        />
      ) : isProcessing ? (
        <div className="w-full h-full bg-slate-800 flex items-center justify-center">
          <Spinner size="md" className="text-redd-500" />
        </div>
      ) : (
        <div className="w-full h-full bg-slate-800 flex items-center justify-center">
          <span className="text-slate-500 text-lg">
            {image.status === 'failed' ? '!' : '-'}
          </span>
        </div>
      )}

      {/* Selected indicator bar */}
      {isSelected && (
        <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-redd-500" />
      )}

      {/* Drag handle indicator (only for complete images when dragging enabled) */}
      {isDraggingEnabled && isComplete && !isDragging && (
        <div className="absolute bottom-0.5 right-0.5 w-4 h-4 bg-slate-800/80 rounded flex items-center justify-center">
          <svg className="w-3 h-3 text-slate-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 6h2v2H8V6zm6 0h2v2h-2V6zM8 11h2v2H8v-2zm6 0h2v2h-2v-2zm-6 5h2v2H8v-2zm6 0h2v2h-2v-2z" />
          </svg>
        </div>
      )}
    </button>
  );
};

export const ThumbnailGallery: React.FC<ThumbnailGalleryProps> = ({
  images,
  selectedType,
  onSelect,
  getImageUrl,
  onReorder,
  className,
}) => {
  // Sort images by Amazon listing order
  const sortedImages = [...images].sort(
    (a, b) => IMAGE_ORDER.indexOf(a.type) - IMAGE_ORDER.indexOf(b.type)
  );

  // Determine if layout is horizontal (for responsive class handling)
  const isHorizontal = className?.includes('flex-row');

  // DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Handle drag end
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = sortedImages.findIndex((img) => img.type === active.id);
      const newIndex = sortedImages.findIndex((img) => img.type === over.id);
      const newOrder = arrayMove(
        sortedImages.map((img) => img.type),
        oldIndex,
        newIndex
      );
      onReorder?.(newOrder);
    }
  };

  const isDraggingEnabled = Boolean(onReorder);

  // If drag is enabled, wrap in DnD context
  if (isDraggingEnabled) {
    return (
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={sortedImages.map((img) => img.type)}
          strategy={isHorizontal ? horizontalListSortingStrategy : verticalListSortingStrategy}
        >
          <div
            className={cn('flex flex-col gap-2', className)}
            role="listbox"
            aria-label="Product images (drag to reorder)"
          >
            {sortedImages.map((image, index) => {
              const isSelected = image.type === selectedType;
              const isComplete = image.status === 'complete';
              const isProcessing = image.status === 'processing';

              return (
                <SortableThumbnail
                  key={image.type}
                  image={image}
                  index={index}
                  isSelected={isSelected}
                  isComplete={isComplete}
                  isProcessing={isProcessing}
                  onSelect={() => onSelect(image.type)}
                  getImageUrl={getImageUrl}
                  isDraggingEnabled={isDraggingEnabled}
                />
              );
            })}
          </div>
        </SortableContext>
      </DndContext>
    );
  }

  // Non-draggable version (simpler)
  return (
    <div
      className={cn('flex flex-col gap-2', className)}
      role="listbox"
      aria-label="Product images"
    >
      {sortedImages.map((image, index) => {
        const isSelected = image.type === selectedType;
        const isComplete = image.status === 'complete';
        const isProcessing = image.status === 'processing';

        return (
          <button
            key={image.type}
            onClick={() => onSelect(image.type)}
            role="option"
            aria-selected={isSelected}
            aria-label={`${image.label || `Image ${index + 1}`}${isSelected ? ' (selected)' : ''}${isProcessing ? ' (loading)' : ''}`}
            className={cn(
              'relative w-14 h-14 md:w-16 md:h-16 flex-shrink-0 rounded-lg overflow-hidden border-2 transition-all duration-200 cursor-pointer',
              'focus:outline-none focus:ring-2 focus:ring-redd-500 focus:ring-offset-2 focus:ring-offset-slate-50',
              isSelected
                ? 'border-redd-500 ring-2 ring-redd-500/30 scale-105'
                : 'border-slate-300 hover:border-slate-400 hover:scale-102',
              !isComplete && !isProcessing && 'opacity-70'
            )}
          >
            {/* Image number badge */}
            <span
              className={cn(
                'absolute top-0.5 left-0.5 z-10 w-5 h-5 rounded text-xs font-medium',
                'flex items-center justify-center',
                isSelected
                  ? 'bg-redd-500 text-white'
                  : 'bg-slate-800/80 text-slate-300'
              )}
            >
              {index + 1}
            </span>

            {/* Thumbnail image or status indicator */}
            {isComplete ? (
              <img
                src={getImageUrl(image.type)}
                alt={image.label}
                className="w-full h-full object-cover"
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
              />
            ) : isProcessing ? (
              <div className="w-full h-full bg-slate-800 flex items-center justify-center">
                <Spinner size="md" className="text-redd-500" />
              </div>
            ) : (
              <div className="w-full h-full bg-slate-800 flex items-center justify-center">
                <span className="text-slate-500 text-lg">
                  {image.status === 'failed' ? '!' : '-'}
                </span>
              </div>
            )}

            {/* Selected indicator bar */}
            {isSelected && (
              <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-redd-500" />
            )}
          </button>
        );
      })}
    </div>
  );
};
