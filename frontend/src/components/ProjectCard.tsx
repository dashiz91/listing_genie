import React from 'react';
import { Badge } from './ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import type { ProjectListItem, GenerationStatus } from '../api/types';

interface ProjectCardProps {
  project: ProjectListItem;
  onClick: () => void;
  onContinue: () => void;
  onRename: () => void;
  onDelete: () => void;
}

const statusConfig: Record<GenerationStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline'; className: string }> = {
  complete: { label: 'Complete', variant: 'default', className: 'bg-green-500/20 text-green-400 border-green-500/30' },
  partial: { label: 'Partial', variant: 'secondary', className: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  processing: { label: 'Processing', variant: 'secondary', className: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  pending: { label: 'Pending', variant: 'outline', className: 'bg-slate-500/20 text-slate-400 border-slate-500/30' },
  failed: { label: 'Failed', variant: 'destructive', className: 'bg-red-500/20 text-red-400 border-red-500/30' },
};

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onClick,
  onContinue,
  onRename,
  onDelete,
}) => {
  const status = statusConfig[project.status] || statusConfig.pending;
  const formattedDate = new Date(project.created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  const handleMenuClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div
      onClick={onClick}
      className="group relative bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden cursor-pointer
                 hover:border-redd-500/50 hover:bg-slate-800/80 transition-all duration-200"
    >
      {/* Thumbnail Area */}
      <div className="relative aspect-square bg-slate-900/50">
        {project.thumbnail_url ? (
          <img
            src={project.thumbnail_url}
            alt={project.product_title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <svg
              className="w-12 h-12 text-slate-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* Status Badge */}
        <div className="absolute top-2 right-2">
          <Badge className={`${status.className} text-xs`}>
            {status.label}
          </Badge>
        </div>

        {/* Image Count Badge */}
        <div className="absolute bottom-2 right-2">
          <Badge variant="outline" className="bg-slate-900/80 text-slate-300 border-slate-600 text-xs">
            {project.complete_count}/{project.image_count}
          </Badge>
        </div>

        {/* Dropdown Menu */}
        <div
          className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={handleMenuClick}
        >
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="p-1.5 rounded-md bg-slate-900/80 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                </svg>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="bg-slate-800 border-slate-700">
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onContinue();
                }}
                className="text-slate-300 hover:text-white hover:bg-slate-700 cursor-pointer"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Continue Editing
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onRename();
                }}
                className="text-slate-300 hover:text-white hover:bg-slate-700 cursor-pointer"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Rename
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-slate-700" />
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete();
                }}
                className="text-red-400 hover:text-red-300 hover:bg-red-500/10 cursor-pointer"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Card Footer */}
      <div className="p-3">
        <h3 className="font-medium text-white text-sm truncate">
          {project.product_title}
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          {formattedDate}
        </p>
      </div>
    </div>
  );
};

// Skeleton for loading state
export const ProjectCardSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
      <div className="aspect-square bg-slate-700/50 animate-pulse" />
      <div className="p-3 space-y-2">
        <div className="h-4 bg-slate-700/50 rounded animate-pulse w-3/4" />
        <div className="h-3 bg-slate-700/50 rounded animate-pulse w-1/2" />
      </div>
    </div>
  );
};
