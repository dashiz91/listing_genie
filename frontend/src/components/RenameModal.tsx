import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Spinner } from '@/components/ui/spinner';

interface RenameModalProps {
  isOpen: boolean;
  currentTitle: string;
  onClose: () => void;
  onConfirm: (newTitle: string) => Promise<void>;
}

export const RenameModal: React.FC<RenameModalProps> = ({
  isOpen,
  currentTitle,
  onClose,
  onConfirm,
}) => {
  const [title, setTitle] = useState(currentTitle);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setTitle(currentTitle);
      setError(null);
    }
  }, [isOpen, currentTitle]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      setError('Title cannot be empty');
      return;
    }

    if (trimmedTitle.length > 200) {
      setError('Title must be 200 characters or less');
      return;
    }

    if (trimmedTitle === currentTitle) {
      onClose();
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await onConfirm(trimmedTitle);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to rename project');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 text-white sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white">Rename Project</DialogTitle>
          <DialogDescription className="text-slate-400">
            Enter a new name for your project.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-slate-300">
                Project Title
              </Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter project title..."
                className="bg-slate-900 border-slate-600 text-white placeholder:text-slate-500 focus:border-redd-500 focus:ring-redd-500"
                autoFocus
              />
              {error && (
                <p className="text-sm text-red-400">{error}</p>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-redd-500 hover:bg-redd-600 text-white"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <Spinner size="sm" className="text-current" />
                  Saving...
                </span>
              ) : (
                'Save'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
