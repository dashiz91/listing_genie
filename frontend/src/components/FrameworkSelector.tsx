import React, { useState, useEffect } from 'react';
import type { DesignFramework } from '../api/types';

interface FrameworkSelectorProps {
  frameworks: DesignFramework[];
  productAnalysis: string;
  selectedFramework: DesignFramework | null;
  onSelect: (framework: DesignFramework) => void;
  onConfirm: () => void;
  isLoading: boolean;
}

export const FrameworkSelector: React.FC<FrameworkSelectorProps> = ({
  frameworks,
  productAnalysis,
  selectedFramework,
  onSelect,
  onConfirm,
  isLoading,
}) => {
  const [expandedFramework, setExpandedFramework] = useState<string | null>(null);

  const frameworkTypeLabels: Record<string, { label: string; color: string; description: string }> = {
    safe_excellence: {
      label: 'Safe Excellence',
      color: 'bg-blue-500',
      description: 'Most likely to convert - Professional & proven',
    },
    bold_creative: {
      label: 'Bold Creative',
      color: 'bg-purple-500',
      description: 'Unexpected but compelling - Stand out risk',
    },
    emotional_story: {
      label: 'Emotional Story',
      color: 'bg-pink-500',
      description: 'Feelings & lifestyle focus - Heart-first',
    },
    premium_elevation: {
      label: 'Premium Elevation',
      color: 'bg-amber-500',
      description: 'Luxurious & aspirational - High-end feel',
    },
    style_reference: {
      label: 'Style Match',
      color: 'bg-emerald-500',
      description: 'Matched to your style reference image',
    },
  };

  // Check if this is single-framework mode (style reference provided)
  const isSingleFrameworkMode = frameworks.length === 1 && frameworks[0]?.framework_type === 'style_reference';

  // Auto-select the single framework in style reference mode
  useEffect(() => {
    if (isSingleFrameworkMode && frameworks[0] && !selectedFramework) {
      onSelect(frameworks[0]);
    }
  }, [isSingleFrameworkMode, frameworks, selectedFramework, onSelect]);

  const getFrameworkMeta = (framework: DesignFramework) => {
    const type = framework.framework_type?.toLowerCase().replace(/\s+/g, '_') || 'safe_excellence';
    return frameworkTypeLabels[type] || frameworkTypeLabels.safe_excellence;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {isSingleFrameworkMode ? 'Style Reference Match' : 'Principal Designer AI Analysis'}
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          {isSingleFrameworkMode
            ? 'AI has analyzed your product and style reference to create a framework that matches your desired aesthetic. Colors, typography, and mood have been extracted from your style reference.'
            : `AI has analyzed your product and created ${frameworks.length} unique design framework${frameworks.length !== 1 ? 's' : ''}. Each framework is tailored specifically to YOUR product.`}
        </p>
      </div>

      {/* Product Analysis Card */}
      <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl p-4 border border-primary-100">
        <h3 className="font-semibold text-primary-900 mb-2 flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          What the AI Sees
        </h3>
        <p className="text-gray-700 text-sm">{productAnalysis}</p>
      </div>

      {/* Framework Cards */}
      <div className={`grid gap-4 ${isSingleFrameworkMode ? 'grid-cols-1 max-w-2xl mx-auto' : 'grid-cols-1 lg:grid-cols-2'}`}>
        {frameworks.map((framework, index) => {
          const isSelected = selectedFramework?.framework_id === framework.framework_id;
          const isExpanded = expandedFramework === framework.framework_id;
          const meta = getFrameworkMeta(framework);

          return (
            <div
              key={framework.framework_id}
              className={`
                relative rounded-xl border-2 overflow-hidden transition-all cursor-pointer
                ${isSelected
                  ? 'border-primary-500 ring-4 ring-primary-100 shadow-lg'
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-md'}
              `}
              onClick={() => onSelect(framework)}
            >
              {/* Framework Header */}
              <div className={`${meta.color} px-4 py-2 flex items-center justify-between`}>
                <div className="flex items-center gap-2">
                  <span className="text-white font-bold text-lg">#{index + 1}</span>
                  <span className="text-white font-semibold">{framework.framework_name}</span>
                </div>
                <span className="text-white/80 text-xs">{meta.label}</span>
              </div>

              {/* Preview Image - THE KEY VISUAL */}
              <div className="aspect-square bg-gray-100 relative">
                {framework.preview_url ? (
                  <img
                    src={`http://localhost:8000${framework.preview_url}`}
                    alt={framework.framework_name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
                      <span className="text-sm text-gray-500">Generating preview...</span>
                    </div>
                  </div>
                )}

                {/* Selected Checkmark */}
                {isSelected && (
                  <div className="absolute top-2 right-2 w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-lg">
                    <svg className="w-6 h-6 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-4 bg-white">
                {/* Design Philosophy */}
                <p className="text-gray-700 text-sm mb-3 italic line-clamp-2">
                  "{framework.design_philosophy}"
                </p>

                {/* Color Palette - Compact */}
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xs text-gray-500">Colors:</span>
                  <div className="flex gap-1">
                    {framework.colors.slice(0, 5).map((color, i) => (
                      <div
                        key={i}
                        className="w-6 h-6 rounded-full shadow-inner border border-gray-200"
                        style={{ backgroundColor: color.hex }}
                        title={`${color.name} - ${color.role}`}
                      />
                    ))}
                  </div>
                </div>

                {/* Typography - Compact */}
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xs text-gray-500">Font:</span>
                  <span className="text-xs font-medium">{framework.typography.headline_font}</span>
                </div>

                {/* Expand/Collapse */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setExpandedFramework(isExpanded ? null : framework.framework_id);
                  }}
                  className="text-primary-600 text-sm font-medium hover:text-primary-700 flex items-center gap-1"
                >
                  {isExpanded ? 'Show Less' : 'Show Full Details'}
                  <svg
                    className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
                    {/* Image Headlines */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Headlines for Each Image</h4>
                      <div className="space-y-2">
                        {framework.image_copy.map((copy, i) => (
                          <div key={i} className="text-sm">
                            <span className="font-medium text-gray-700">
                              {copy.image_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                            </span>{' '}
                            <span className="text-gray-600">{copy.headline}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Visual Treatment */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Visual Treatment</h4>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="font-medium text-gray-600">Lighting:</span>{' '}
                          <span className="text-gray-500">{framework.visual_treatment.lighting_style}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-600">Background:</span>{' '}
                          <span className="text-gray-500">{framework.visual_treatment.background_treatment}</span>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {framework.visual_treatment.mood_keywords.map((keyword, i) => (
                          <span key={i} className="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Layout */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Layout Philosophy</h4>
                      <p className="text-xs text-gray-600">{framework.layout.whitespace_philosophy}</p>
                    </div>

                    {/* Rationale */}
                    <div className="bg-gradient-to-r from-gray-50 to-white p-3 rounded-lg">
                      <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Why This Works</h4>
                      <p className="text-xs text-gray-600">{framework.rationale}</p>
                    </div>

                    {/* Target Appeal */}
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Target Appeal</h4>
                      <p className="text-xs text-gray-600">{framework.target_appeal}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Confirm Button */}
      <button
        onClick={onConfirm}
        disabled={!selectedFramework || isLoading}
        className={`
          w-full py-4 px-6 rounded-xl font-bold text-white text-lg transition-all duration-200
          ${!selectedFramework || isLoading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-700 hover:to-primary-600 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
          }
        `}
      >
        {isLoading ? (
          <span className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            <span>Generating All 5 Images...</span>
          </span>
        ) : !selectedFramework ? (
          'Select a Design Framework'
        ) : (
          <span className="flex items-center justify-center gap-2">
            <span>Generate All 5 Images with "{selectedFramework.framework_name}"</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </span>
        )}
      </button>

      {/* Selection hint */}
      {selectedFramework && (
        <p className="text-center text-sm text-gray-500">
          Click "Show Full Details" on any framework to see complete specifications
        </p>
      )}
    </div>
  );
};
