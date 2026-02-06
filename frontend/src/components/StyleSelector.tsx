import React from 'react';
import type { GenerationStatus } from '../api/types';
import { Spinner } from '@/components/ui/spinner';

export interface StylePreview {
  style_id: string;
  style_name: string;
  status: GenerationStatus;
  image_url?: string;
  error_message?: string;
}

export interface Style {
  id: string;
  name: string;
  description: string;
  color_palette: string[];
  mood: string;
}

interface StyleSelectorProps {
  styles: Style[];
  previews: StylePreview[];
  selectedStyle: string | null;
  onSelect: (styleId: string) => void;
  onConfirm: () => void;
  isGenerating: boolean;
}

export const StyleSelector: React.FC<StyleSelectorProps> = ({
  styles,
  previews,
  selectedStyle,
  onSelect,
  onConfirm,
  isGenerating,
}) => {
  const getPreviewForStyle = (styleId: string) => {
    return previews.find((p) => p.style_id === styleId);
  };

  const allPreviewsReady = previews.length > 0 &&
    previews.every((p) => p.status === 'complete' || p.status === 'failed');

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Choose Your Style
        </h2>
        <p className="text-gray-600">
          Select a visual style for your listing images. All 5 images will follow this aesthetic.
        </p>
      </div>

      {/* Style Grid */}
      <div className="grid grid-cols-2 gap-4">
        {styles.map((style) => {
          const preview = getPreviewForStyle(style.id);
          const isSelected = selectedStyle === style.id;

          return (
            <div
              key={style.id}
              onClick={() => !isGenerating && onSelect(style.id)}
              className={`
                relative rounded-xl border-2 overflow-hidden cursor-pointer transition-all
                ${isSelected
                  ? 'border-primary-500 ring-4 ring-primary-100'
                  : 'border-gray-200 hover:border-gray-300'}
                ${isGenerating ? 'opacity-75 cursor-wait' : ''}
              `}
            >
              {/* Preview Image */}
              <div className="aspect-square bg-gray-100 relative">
                {preview?.status === 'complete' && preview.image_url ? (
                  <img
                    src={`http://localhost:8000${preview.image_url}`}
                    alt={style.name}
                    className="w-full h-full object-cover"
                  />
                ) : preview?.status === 'processing' || (!preview && isGenerating) ? (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <Spinner size="lg" className="text-redd-500 mx-auto mb-2" />
                      <span className="text-sm text-gray-500">Generating...</span>
                    </div>
                  </div>
                ) : preview?.status === 'failed' ? (
                  <div className="absolute inset-0 flex items-center justify-center bg-red-50">
                    <div className="text-center text-red-500">
                      <span className="text-2xl">!</span>
                      <p className="text-xs mt-1">Failed</p>
                    </div>
                  </div>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center text-gray-400">
                      <div className="w-12 h-12 rounded-lg bg-gray-200 mx-auto mb-2"></div>
                      <span className="text-xs">Preview</span>
                    </div>
                  </div>
                )}

                {/* Selected Checkmark */}
                {isSelected && (
                  <div className="absolute top-2 right-2 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>

              {/* Style Info */}
              <div className="p-3 bg-white">
                <h3 className="font-semibold text-gray-900">{style.name}</h3>
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">{style.description}</p>

                {/* Color Palette */}
                <div className="flex gap-1 mt-2">
                  {style.color_palette.slice(0, 4).map((color, i) => (
                    <div
                      key={i}
                      className="w-4 h-4 rounded-full border border-gray-200"
                      style={{
                        backgroundColor: color.startsWith('#') ? color : undefined,
                      }}
                      title={color}
                    >
                      {!color.startsWith('#') && (
                        <span className="sr-only">{color}</span>
                      )}
                    </div>
                  ))}
                </div>

                {/* Mood */}
                <p className="text-xs text-primary-600 mt-2">{style.mood}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Confirm Button */}
      <button
        onClick={onConfirm}
        disabled={!selectedStyle || !allPreviewsReady || isGenerating}
        className={`
          w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-200
          ${!selectedStyle || !allPreviewsReady || isGenerating
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-primary-600 hover:bg-primary-700 shadow-lg hover:shadow-xl'
          }
        `}
      >
        {isGenerating ? (
          <span className="flex items-center justify-center space-x-2">
            <Spinner size="sm" className="text-white" />
            <span>Generating Previews...</span>
          </span>
        ) : !allPreviewsReady ? (
          'Waiting for previews...'
        ) : !selectedStyle ? (
          'Select a Style'
        ) : (
          'Generate All 5 Images with This Style'
        )}
      </button>
    </div>
  );
};
