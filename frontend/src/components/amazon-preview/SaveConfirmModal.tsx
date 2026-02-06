import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';

interface SaveConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  productTitle: string;
  imageCount: number;
  isLoading?: boolean;
}

export const SaveConfirmModal: React.FC<SaveConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  productTitle,
  imageCount,
  isLoading = false,
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 text-white sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white text-xl">Save to Projects?</DialogTitle>
          <DialogDescription className="text-slate-400">
            This will save your listing images for easy access later.
          </DialogDescription>
        </DialogHeader>

        {/* Summary */}
        <div className="py-4 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Product</span>
            <span className="text-white font-medium truncate max-w-[200px]">
              {productTitle}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Images</span>
            <span className="text-white font-medium">{imageCount} complete</span>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-slate-700" />

        {/* Info */}
        <div className="py-2">
          <p className="text-xs text-slate-500">
            You can access saved projects from the Projects page anytime.
          </p>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 bg-slate-700 text-slate-300 font-medium rounded-lg hover:bg-slate-600 border border-slate-600 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className={cn(
              'px-6 py-2 bg-redd-500 text-white font-medium rounded-lg hover:bg-redd-600 transition-colors',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'flex items-center gap-2'
            )}
          >
            {isLoading ? (
              <>
                <Spinner size="sm" className="text-white" />
                <span>Saving...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span>Save Project</span>
              </>
            )}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
