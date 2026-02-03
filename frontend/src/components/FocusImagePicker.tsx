/**
 * FocusImagePicker — "Focus images" row for edit panels.
 * Shows thumbnail chips from user's references (uploads + style ref + logo).
 * All off by default. User taps to toggle (blue border + checkmark).
 * "+" button at end opens file picker for an ad-hoc reference image.
 */
import React, { useRef, useState } from 'react';
import type { ReferenceImage } from '@/api/types';

interface FocusImagePickerProps {
  /** Available reference images from the session */
  availableImages: ReferenceImage[];
  /** Currently selected paths */
  selectedPaths: Set<string>;
  /** Toggle a path on/off */
  onToggle: (path: string) => void;
  /** Ad-hoc extra image picked by user (local file) */
  extraFile: { file: File; preview: string } | null;
  /** Called when user picks a file via "+" */
  onExtraFile: (file: File) => void;
  /** Remove the extra file */
  onRemoveExtra: () => void;
  /** Variant for light or dark backgrounds */
  variant?: 'light' | 'dark';
}

const FocusImagePicker: React.FC<FocusImagePickerProps> = ({
  availableImages,
  selectedPaths,
  onToggle,
  extraFile,
  onExtraFile,
  onRemoveExtra,
  variant = 'light',
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [extraSelected, setExtraSelected] = useState(true);

  if (availableImages.length === 0 && !extraFile) return null;

  const isDark = variant === 'dark';
  const helperColor = isDark ? 'text-slate-500' : 'text-gray-400';
  const labelColor = isDark ? 'text-slate-400' : 'text-gray-500';
  const chipLabelColor = isDark ? 'text-slate-300' : 'text-gray-600';

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className={`block text-xs font-medium ${labelColor}`}>
          Focus images
        </label>
        <span className={`text-[10px] ${helperColor}`}>
          Only selected images are sent to AI
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {availableImages.map((img) => {
          const isOn = selectedPaths.has(img.path);
          return (
            <button
              key={img.path}
              type="button"
              onClick={() => onToggle(img.path)}
              className={`
                relative flex flex-col items-center gap-0.5 p-1 rounded-lg border-2 transition-all
                ${isOn
                  ? 'border-blue-500 bg-blue-50/80 dark:bg-blue-900/30'
                  : isDark
                    ? 'border-slate-700 bg-slate-800 hover:border-slate-500'
                    : 'border-gray-200 bg-gray-50 hover:border-gray-300'
                }
              `}
            >
              <img
                src={img.url}
                alt={img.label}
                className="w-10 h-10 rounded object-cover"
              />
              <span className={`text-[9px] leading-tight truncate max-w-[48px] ${isOn ? 'text-blue-600 font-semibold dark:text-blue-400' : chipLabelColor}`}>
                {img.label}
              </span>
              {isOn && (
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              )}
            </button>
          );
        })}

        {/* Extra ad-hoc file */}
        {extraFile && (
          <button
            type="button"
            onClick={() => setExtraSelected((p) => !p)}
            className={`
              relative flex flex-col items-center gap-0.5 p-1 rounded-lg border-2 transition-all
              ${extraSelected
                ? 'border-blue-500 bg-blue-50/80 dark:bg-blue-900/30'
                : isDark
                  ? 'border-slate-700 bg-slate-800'
                  : 'border-gray-200 bg-gray-50'
              }
            `}
          >
            <img
              src={extraFile.preview}
              alt="Extra"
              className="w-10 h-10 rounded object-cover"
            />
            <span className={`text-[9px] leading-tight ${extraSelected ? 'text-blue-600 font-semibold dark:text-blue-400' : chipLabelColor}`}>Extra</span>
            {extraSelected && (
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); onRemoveExtra(); }}
              className="absolute -top-1.5 -left-1.5 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center hover:bg-red-600"
            >
              <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </button>
        )}

        {/* "+" button to add ad-hoc reference image */}
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className={`
            flex flex-col items-center justify-center w-[52px] h-[52px] rounded-lg border-2 border-dashed transition-colors
            ${isDark
              ? 'border-slate-600 hover:border-slate-400 text-slate-400 hover:text-slate-300'
              : 'border-gray-300 hover:border-gray-400 text-gray-400 hover:text-gray-500'
            }
          `}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) {
              onExtraFile(file);
              setExtraSelected(true);
            }
            e.target.value = '';
          }}
        />
      </div>
    </div>
  );
};

/** Hook to manage focus image state for an edit panel */
export function useFocusImages() {
  const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set());
  const [extraFile, setExtraFile] = useState<{ file: File; preview: string } | null>(null);

  const toggle = (path: string) => {
    console.log('[FOCUS DEBUG] toggle called with path:', path);
    setSelectedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
        console.log('[FOCUS DEBUG] Removed path, new size:', next.size);
      } else {
        next.add(path);
        console.log('[FOCUS DEBUG] Added path, new size:', next.size);
      }
      return next;
    });
  };

  const addExtra = (file: File) => {
    if (extraFile) URL.revokeObjectURL(extraFile.preview);
    setExtraFile({ file, preview: URL.createObjectURL(file) });
  };

  const removeExtra = () => {
    if (extraFile) URL.revokeObjectURL(extraFile.preview);
    setExtraFile(null);
  };

  const reset = () => {
    setSelectedPaths(new Set());
    removeExtra();
  };

  /** Get selected paths array (extra file not included — must be uploaded first) */
  const getSelectedPaths = () => Array.from(selectedPaths);

  /** Whether the extra file is toggled on */
  const isExtraSelected = true; // Extra is always selected once added

  return {
    selectedPaths,
    extraFile,
    toggle,
    addExtra,
    removeExtra,
    reset,
    getSelectedPaths,
    isExtraSelected,
  };
}

export default FocusImagePicker;
