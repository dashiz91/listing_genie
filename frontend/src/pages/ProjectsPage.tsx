import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { ProjectCard, ProjectCardSkeleton } from '../components/ProjectCard';
import { ProjectDetailModal } from '../components/ProjectDetailModal';
import { RenameModal } from '../components/RenameModal';
import { DeleteConfirmModal } from '../components/DeleteConfirmModal';
import { apiClient } from '../api/client';
import type { ProjectListItem } from '../api/types';

const PAGE_SIZE = 12;

export const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Modal states
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [renameModal, setRenameModal] = useState<{ id: string; title: string } | null>(null);
  const [deleteModal, setDeleteModal] = useState<{ id: string; title: string } | null>(null);

  const loadProjects = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.listProjects(page, PAGE_SIZE, statusFilter);
      setProjects(response.projects);
      setTotalPages(response.total_pages);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleRename = async (newTitle: string) => {
    if (!renameModal) return;
    await apiClient.renameProject(renameModal.id, newTitle);
    // Update local state
    setProjects(prev =>
      prev.map(p =>
        p.session_id === renameModal.id ? { ...p, product_title: newTitle } : p
      )
    );
  };

  const handleDelete = async () => {
    if (!deleteModal) return;
    await apiClient.deleteProject(deleteModal.id);
    // Remove from local state
    setProjects(prev => prev.filter(p => p.session_id !== deleteModal.id));
    setTotal(prev => prev - 1);
    // Close detail modal if open
    if (selectedProject === deleteModal.id) {
      setSelectedProject(null);
    }
  };

  const handleDeleteFromModal = () => {
    if (!selectedProject) return;
    const project = projects.find(p => p.session_id === selectedProject);
    if (project) {
      setDeleteModal({ id: project.session_id, title: project.product_title });
    }
  };

  const handleFilterChange = (value: string) => {
    setStatusFilter(value);
    setPage(1); // Reset to first page when filter changes
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Empty state
  const EmptyState = () => (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mb-6">
        <svg className="w-10 h-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
      </div>
      <h3 className="text-xl font-semibold text-white mb-2">No projects yet</h3>
      <p className="text-slate-400 text-center mb-6 max-w-md">
        {statusFilter !== 'all'
          ? `No projects with status "${statusFilter}" found.`
          : 'Start generating your first Amazon listing images to see them here.'}
      </p>
      {statusFilter === 'all' && (
        <Link to="/app">
          <Button className="bg-redd-500 hover:bg-redd-600 text-white">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create First Project
          </Button>
        </Link>
      )}
    </div>
  );

  // Pagination component
  const Pagination = () => {
    if (totalPages <= 1) return null;

    const pages = [];
    const maxVisible = 5;
    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);

    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    return (
      <div className="flex items-center justify-center gap-2 mt-8">
        <Button
          variant="outline"
          size="sm"
          onClick={() => handlePageChange(page - 1)}
          disabled={page === 1}
          className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white disabled:opacity-50"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </Button>

        {start > 1 && (
          <>
            <Button
              variant={page === 1 ? 'default' : 'outline'}
              size="sm"
              onClick={() => handlePageChange(1)}
              className={page === 1
                ? 'bg-redd-500 hover:bg-redd-600 text-white'
                : 'border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white'
              }
            >
              1
            </Button>
            {start > 2 && <span className="text-slate-500">...</span>}
          </>
        )}

        {pages.map(p => (
          <Button
            key={p}
            variant={page === p ? 'default' : 'outline'}
            size="sm"
            onClick={() => handlePageChange(p)}
            className={page === p
              ? 'bg-redd-500 hover:bg-redd-600 text-white'
              : 'border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white'
            }
          >
            {p}
          </Button>
        ))}

        {end < totalPages && (
          <>
            {end < totalPages - 1 && <span className="text-slate-500">...</span>}
            <Button
              variant={page === totalPages ? 'default' : 'outline'}
              size="sm"
              onClick={() => handlePageChange(totalPages)}
              className={page === totalPages
                ? 'bg-redd-500 hover:bg-redd-600 text-white'
                : 'border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white'
              }
            >
              {totalPages}
            </Button>
          </>
        )}

        <Button
          variant="outline"
          size="sm"
          onClick={() => handlePageChange(page + 1)}
          disabled={page === totalPages}
          className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white disabled:opacity-50"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Button>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Projects</h1>
          <p className="text-slate-400 mt-1">
            {total > 0 ? `${total} project${total !== 1 ? 's' : ''}` : 'Manage your generation sessions'}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Status Filter */}
          <Select value={statusFilter} onValueChange={handleFilterChange}>
            <SelectTrigger className="w-40 bg-slate-800 border-slate-600 text-white">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent className="bg-slate-800 border-slate-700">
              <SelectItem value="all" className="text-slate-300 hover:bg-slate-700">
                All Status
              </SelectItem>
              <SelectItem value="complete" className="text-green-400 hover:bg-slate-700">
                Complete
              </SelectItem>
              <SelectItem value="partial" className="text-yellow-400 hover:bg-slate-700">
                Partial
              </SelectItem>
              <SelectItem value="processing" className="text-blue-400 hover:bg-slate-700">
                Processing
              </SelectItem>
              <SelectItem value="failed" className="text-red-400 hover:bg-slate-700">
                Failed
              </SelectItem>
            </SelectContent>
          </Select>

          {/* New Project Button */}
          <Link to="/app">
            <Button className="bg-redd-500 hover:bg-redd-600 text-white">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Project
            </Button>
          </Link>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <div className="flex items-center gap-2 text-red-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p>{error}</p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={loadProjects}
            className="mt-3 border-red-500/50 text-red-400 hover:bg-red-500/10"
          >
            Try Again
          </Button>
        </div>
      )}

      {/* Content */}
      {loading ? (
        // Loading skeleton grid
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <ProjectCardSkeleton key={i} />
          ))}
        </div>
      ) : projects.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          {/* Projects Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {projects.map(project => (
              <ProjectCard
                key={project.session_id}
                project={project}
                onClick={() => setSelectedProject(project.session_id)}
                onRename={() => setRenameModal({ id: project.session_id, title: project.product_title })}
                onDelete={() => setDeleteModal({ id: project.session_id, title: project.product_title })}
              />
            ))}
          </div>

          {/* Pagination */}
          <Pagination />
        </>
      )}

      {/* Project Detail Modal */}
      <ProjectDetailModal
        isOpen={selectedProject !== null}
        sessionId={selectedProject}
        onClose={() => setSelectedProject(null)}
        onDelete={handleDeleteFromModal}
      />

      {/* Rename Modal */}
      <RenameModal
        isOpen={renameModal !== null}
        currentTitle={renameModal?.title || ''}
        onClose={() => setRenameModal(null)}
        onConfirm={handleRename}
      />

      {/* Delete Confirm Modal */}
      <DeleteConfirmModal
        isOpen={deleteModal !== null}
        projectTitle={deleteModal?.title || ''}
        onClose={() => setDeleteModal(null)}
        onConfirm={handleDelete}
      />
    </div>
  );
};
