/**
 * PushToAmazonButton — "Push to Amazon" action for the results view.
 * Checks Amazon connection, collects ASIN + SKU, pushes listing images,
 * and polls for completion status.
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiClient } from '@/api/client';
import type { AmazonAuthStatus, AmazonPushJobStatus, AmazonSellerSku } from '@/api/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Spinner } from '@/components/ui/spinner';

interface PushToAmazonButtonProps {
  sessionId: string;
  /** Pre-filled ASIN from ASIN import (if available) */
  asin?: string;
  label?: string;
  className?: string;
}

type PushState =
  | { phase: 'idle' }
  | { phase: 'checking' }
  | { phase: 'not_connected' }
  | { phase: 'form' }
  | { phase: 'pushing'; jobId: string; status: AmazonPushJobStatus; progress?: number; message?: string }
  | { phase: 'completed'; message?: string }
  | { phase: 'failed'; error: string };

const PushToAmazonButton: React.FC<PushToAmazonButtonProps> = ({
  sessionId,
  asin: prefillAsin,
  label = 'Push to Amazon',
  className,
}) => {
  const [state, setState] = useState<PushState>({ phase: 'idle' });
  const [asin, setAsin] = useState(prefillAsin || '');
  const [sku, setSku] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [skuOptions, setSkuOptions] = useState<AmazonSellerSku[]>([]);
  const [skuSearch, setSkuSearch] = useState('');
  const [selectedSkuOption, setSelectedSkuOption] = useState('');
  const [isLoadingSkus, setIsLoadingSkus] = useState(false);
  const [skuLookupError, setSkuLookupError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const dialogRef = useRef<HTMLDivElement>(null);

  // Update ASIN when prefill changes
  useEffect(() => {
    if (prefillAsin) setAsin(prefillAsin);
  }, [prefillAsin]);

  useEffect(() => {
    if (state.phase !== 'form') {
      setSelectedSkuOption('');
      setSkuSearch('');
    }
  }, [state.phase]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // Close dialog on outside click
  useEffect(() => {
    if (state.phase !== 'form' && state.phase !== 'pushing' && state.phase !== 'completed' && state.phase !== 'failed' && state.phase !== 'not_connected') return;

    const handleClick = (e: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
        // Only allow closing if not actively pushing
        if (state.phase !== 'pushing') {
          setState({ phase: 'idle' });
          if (pollRef.current) clearInterval(pollRef.current);
        }
      }
    };

    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [state.phase]);

  const loadSkuOptions = useCallback(async (query?: string) => {
    setIsLoadingSkus(true);
    setSkuLookupError(null);
    try {
      const result = await apiClient.getAmazonSellerSkus(query, 20);
      setSkuOptions(result.skus || []);
    } catch {
      setSkuLookupError('Could not load SKUs from Amazon. You can still enter SKU manually.');
      setSkuOptions([]);
    } finally {
      setIsLoadingSkus(false);
    }
  }, []);

  useEffect(() => {
    if (state.phase === 'form') {
      loadSkuOptions();
    }
  }, [state.phase, loadSkuOptions]);

  const startPoll = useCallback((jobId: string) => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const result = await apiClient.getAmazonPushStatus(jobId);
        if (result.status === 'completed') {
          setState({ phase: 'completed', message: result.step || 'Images pushed successfully!' });
          if (pollRef.current) clearInterval(pollRef.current);
        } else if (result.status === 'failed') {
          setState({ phase: 'failed', error: result.error_message || 'Push failed. Please try again.' });
          if (pollRef.current) clearInterval(pollRef.current);
        } else {
          setState({
            phase: 'pushing',
            jobId,
            status: result.status,
            progress: result.progress,
            message: result.step,
          });
        }
      } catch {
        // Don't stop polling on transient errors
      }
    }, 2000);
  }, []);

  const handleButtonClick = async () => {
    setState({ phase: 'checking' });
    try {
      const authStatus: AmazonAuthStatus = await apiClient.getAmazonAuthStatus();
      if (authStatus.connected) {
        setState({ phase: 'form' });
      } else {
        setState({ phase: 'not_connected' });
      }
    } catch {
      setState({ phase: 'not_connected' });
    }
  };

  const handleSubmit = async () => {
    const trimmedAsin = asin.trim().toUpperCase();
    const trimmedSku = sku.trim();

    if (!trimmedAsin) {
      setFormError('ASIN is required');
      return;
    }
    if (!/^[A-Z0-9]{10}$/.test(trimmedAsin)) {
      setFormError('ASIN must be exactly 10 alphanumeric characters');
      return;
    }
    if (!trimmedSku) {
      setFormError('SKU is required');
      return;
    }

    setFormError(null);
    setState({ phase: 'pushing', jobId: '', status: 'queued', message: 'Starting push...' });

    try {
      const result = await apiClient.pushListingImages(sessionId, trimmedAsin, trimmedSku);
      setState({ phase: 'pushing', jobId: result.job_id, status: result.status, message: 'Push queued...' });
      startPoll(result.job_id);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setState({ phase: 'failed', error: error.response?.data?.detail || 'Failed to start push. Please try again.' });
    }
  };

  const statusLabel = (status: AmazonPushJobStatus): string => {
    switch (status) {
      case 'queued': return 'Queued';
      case 'preparing': return 'Preparing images...';
      case 'submitting': return 'Submitting to Amazon...';
      case 'processing': return 'Amazon is processing...';
      case 'completed': return 'Complete!';
      case 'failed': return 'Failed';
    }
  };

  const showDialog = state.phase !== 'idle' && state.phase !== 'checking';

  return (
    <div className="relative">
      {/* Trigger button */}
      <button
        onClick={handleButtonClick}
        disabled={state.phase === 'checking'}
        className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[#FF9900] bg-[#FF9900]/10 border border-[#FF9900]/30 rounded-lg hover:bg-[#FF9900]/20 transition-colors disabled:opacity-50 ${className || ''}`}
      >
        {state.phase === 'checking' ? (
          <Spinner size="sm" className="text-[#FF9900]" />
        ) : (
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        )}
        {label}
      </button>

      {/* Dialog overlay */}
      {showDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div ref={dialogRef} className="bg-slate-800 border border-slate-700 rounded-xl shadow-xl w-full max-w-md mx-4">
            {/* Not connected */}
            {state.phase === 'not_connected' && (
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#FF9900]/10 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-[#FF9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.172 13.828a4 4 0 015.656 0l4-4a4 4 0 00-5.656-5.656l-1.102 1.101" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-white">Amazon Not Connected</h3>
                    <p className="text-sm text-slate-400">Connect your Seller Central account in Settings first.</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    className="flex-1 bg-[#FF9900] hover:bg-[#e68a00] text-slate-900 font-medium"
                    onClick={() => {
                      window.location.href = '/app/settings';
                    }}
                  >
                    Go to Settings
                  </Button>
                  <Button
                    variant="outline"
                    className="border-slate-600 text-slate-300"
                    onClick={() => setState({ phase: 'idle' })}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {/* Form */}
            {state.phase === 'form' && (
              <div className="p-6 space-y-4">
                <div>
                  <h3 className="text-base font-semibold text-white">Push to Amazon</h3>
                  <p className="text-sm text-slate-400 mt-1">Enter the ASIN and SKU for the listing to update.</p>
                </div>

                {formError && (
                  <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-2.5 text-red-400 text-sm">
                    {formError}
                  </div>
                )}

                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">ASIN</label>
                    <Input
                      value={asin}
                      onChange={(e) => setAsin(e.target.value)}
                      placeholder="e.g., B0XXXXXXXXX"
                      className="bg-slate-900 border-slate-700 text-white font-mono"
                      maxLength={10}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">Find SKU from your account</label>
                    <div className="flex gap-2">
                      <Input
                        value={skuSearch}
                        onChange={(e) => setSkuSearch(e.target.value)}
                        placeholder="Search SKU/title"
                        className="bg-slate-900 border-slate-700 text-white"
                      />
                      <Button
                        variant="outline"
                        className="border-slate-600 text-slate-300"
                        onClick={() => loadSkuOptions(skuSearch)}
                        disabled={isLoadingSkus}
                      >
                        {isLoadingSkus ? <Spinner size="sm" className="text-slate-300" /> : 'Search'}
                      </Button>
                    </div>
                    {skuLookupError && (
                      <p className="text-xs text-amber-400 mt-1">{skuLookupError}</p>
                    )}
                    <select
                      className="mt-2 w-full px-3 py-2 rounded-md bg-slate-900 border border-slate-700 text-white text-sm"
                      value={selectedSkuOption}
                      onChange={(e) => {
                        const selectedSku = e.target.value;
                        setSelectedSkuOption(selectedSku);
                        if (!selectedSku) return;
                        const match = skuOptions.find((opt) => opt.sku === selectedSku);
                        setSku(selectedSku);
                        if (match?.asin) setAsin(match.asin);
                      }}
                    >
                      <option value="">Select SKU from your account (optional)</option>
                      {skuOptions.map((opt) => (
                        <option key={opt.sku} value={opt.sku}>
                          {opt.sku}{opt.asin ? ` · ${opt.asin}` : ''}{opt.title ? ` · ${opt.title}` : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">SKU</label>
                    <Input
                      value={sku}
                      onChange={(e) => setSku(e.target.value)}
                      placeholder="Your seller SKU for this product"
                      className="bg-slate-900 border-slate-700 text-white font-mono"
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      Find your SKU in Seller Central under Inventory &gt; Manage Inventory.
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    className="flex-1 bg-[#FF9900] hover:bg-[#e68a00] text-slate-900 font-medium"
                    onClick={handleSubmit}
                  >
                    Push Listing Images
                  </Button>
                  <Button
                    variant="outline"
                    className="border-slate-600 text-slate-300"
                    onClick={() => setState({ phase: 'idle' })}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {/* Pushing — progress */}
            {state.phase === 'pushing' && (
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <Spinner size="lg" className="text-[#FF9900]" />
                  <div>
                    <h3 className="text-base font-semibold text-white">{statusLabel(state.status)}</h3>
                    {state.message && <p className="text-sm text-slate-400">{state.message}</p>}
                  </div>
                </div>
                {state.progress != null && (
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-[#FF9900] h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(state.progress, 100)}%` }}
                    />
                  </div>
                )}
                <p className="text-xs text-slate-500">
                  This may take a minute. Do not close this dialog.
                </p>
              </div>
            )}

            {/* Completed */}
            {state.phase === 'completed' && (
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-green-400">Pushed Successfully!</h3>
                    <p className="text-sm text-slate-400">{state.message || 'Your listing images are now on Amazon.'}</p>
                  </div>
                </div>
                <Button
                  className="w-full bg-slate-700 hover:bg-slate-600 text-white"
                  onClick={() => setState({ phase: 'idle' })}
                >
                  Done
                </Button>
              </div>
            )}

            {/* Failed */}
            {state.phase === 'failed' && (
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-red-500/20 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-red-400">Push Failed</h3>
                    <p className="text-sm text-slate-400">{state.error}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    className="flex-1 bg-[#FF9900] hover:bg-[#e68a00] text-slate-900 font-medium"
                    onClick={() => setState({ phase: 'form' })}
                  >
                    Try Again
                  </Button>
                  <Button
                    variant="outline"
                    className="border-slate-600 text-slate-300"
                    onClick={() => setState({ phase: 'idle' })}
                  >
                    Close
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PushToAmazonButton;
