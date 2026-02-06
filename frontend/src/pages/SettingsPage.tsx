import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { apiClient, UserSettings, AssetItem, PlanInfo, CreditsInfo, CreditAdjustmentResponse } from '../api/client';
import type { AmazonAuthStatus } from '../api/types';
import { useAuth } from '../contexts/AuthContext';
import { Spinner } from '@/components/ui/spinner';

export const SettingsPage: React.FC = () => {
  const { user, signOut } = useAuth();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form state
  const [brandName, setBrandName] = useState('');
  const [brandColors, setBrandColors] = useState<string[]>([]);
  const [newColor, setNewColor] = useState('#C85A35');

  // Asset picker state
  const [showLogoPicker, setShowLogoPicker] = useState(false);
  const [showStyleRefPicker, setShowStyleRefPicker] = useState(false);
  const [logos, setLogos] = useState<AssetItem[]>([]);
  const [styleRefs, setStyleRefs] = useState<AssetItem[]>([]);
  const [selectedLogoPath, setSelectedLogoPath] = useState<string | null>(null);
  const [selectedStyleRefPath, setSelectedStyleRefPath] = useState<string | null>(null);

  // Plans state
  const [plans, setPlans] = useState<PlanInfo[]>([]);
  const [currentPlan, setCurrentPlan] = useState<string>('free');

  // Credits state
  const [creditsInfo, setCreditsInfo] = useState<CreditsInfo | null>(null);

  // Admin credit adjustment state
  const [adminTargetEmail, setAdminTargetEmail] = useState('');
  const [adminAmount, setAdminAmount] = useState('');
  const [adminReason, setAdminReason] = useState('');
  const [adminAdjusting, setAdminAdjusting] = useState(false);
  const [adminResult, setAdminResult] = useState<CreditAdjustmentResponse | null>(null);
  const [adminError, setAdminError] = useState<string | null>(null);

  // Amazon Seller Central state
  const [amazonAuth, setAmazonAuth] = useState<AmazonAuthStatus | null>(null);
  const [amazonLoading, setAmazonLoading] = useState(false);
  const [amazonConnecting, setAmazonConnecting] = useState(false);
  const [amazonDisconnecting, setAmazonDisconnecting] = useState(false);
  const [amazonMessage, setAmazonMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.getSettings();
      setSettings(data);
      setBrandName(data.brand_presets.default_brand_name || '');
      setBrandColors(data.brand_presets.default_brand_colors || []);
      setSelectedLogoPath(data.brand_presets.default_logo_path);
      setSelectedStyleRefPath(data.brand_presets.default_style_reference_path);
    } catch (err) {
      console.error('Failed to fetch settings:', err);
      setError('Failed to load settings. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchAssets = useCallback(async () => {
    try {
      const data = await apiClient.listAssets('all');
      setLogos(data.assets.filter(a => a.type === 'logos'));
      setStyleRefs(data.assets.filter(a => a.type === 'style-refs'));
    } catch (err) {
      console.error('Failed to fetch assets:', err);
    }
  }, []);

  const fetchPlans = useCallback(async () => {
    try {
      const data = await apiClient.getPlans();
      setPlans(data.plans);
      setCurrentPlan(data.current_plan);
    } catch (err) {
      console.error('Failed to fetch plans:', err);
    }
  }, []);

  const fetchCredits = useCallback(async () => {
    try {
      const data = await apiClient.getCredits();
      setCreditsInfo(data);
    } catch (err) {
      console.error('Failed to fetch credits:', err);
    }
  }, []);

  const fetchAmazonAuth = useCallback(async () => {
    setAmazonLoading(true);
    try {
      const data = await apiClient.getAmazonAuthStatus();
      setAmazonAuth(data);
    } catch (err) {
      console.error('Failed to fetch Amazon auth status:', err);
      setAmazonAuth({ connected: false, seller_id: null, marketplace_id: '', connection_mode: 'none', last_connected_at: null });
    } finally {
      setAmazonLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
    fetchAssets();
    fetchPlans();
    fetchCredits();
    fetchAmazonAuth();
  }, [fetchSettings, fetchAssets, fetchPlans, fetchCredits, fetchAmazonAuth]);

  // Parse Amazon OAuth callback query params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const amazonConnect = params.get('amazon_connect');
    if (amazonConnect === 'success') {
      setAmazonMessage({ type: 'success', text: 'Amazon Seller Central connected successfully!' });
      fetchAmazonAuth();
      // Clean URL
      const url = new URL(window.location.href);
      url.searchParams.delete('amazon_connect');
      window.history.replaceState({}, '', url.toString());
    } else if (amazonConnect === 'error') {
      const errorMsg = params.get('reason') || 'Failed to connect Amazon account. Please try again.';
      setAmazonMessage({ type: 'error', text: errorMsg });
      const url = new URL(window.location.href);
      url.searchParams.delete('amazon_connect');
      url.searchParams.delete('reason');
      window.history.replaceState({}, '', url.toString());
    }
  }, [fetchAmazonAuth]);

  const handleSaveBrandPresets = async () => {
    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);
    try {
      await apiClient.updateBrandPresets({
        default_brand_name: brandName || null,
        default_brand_colors: brandColors,
        default_logo_path: selectedLogoPath,
        default_style_reference_path: selectedStyleRefPath,
      });
      setSuccessMessage('Brand presets saved successfully!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error('Failed to save brand presets:', err);
      setError('Failed to save brand presets. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const addColor = () => {
    if (newColor && !brandColors.includes(newColor)) {
      setBrandColors([...brandColors, newColor]);
    }
  };

  const removeColor = (color: string) => {
    setBrandColors(brandColors.filter(c => c !== color));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-80px)]">
        <div className="flex flex-col items-center gap-4">
          <Spinner size="xl" className="text-redd-500" />
          <p className="text-slate-400">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 mt-1">Manage your account and preferences</p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-400">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="bg-green-500/10 border border-green-500/50 rounded-lg p-4 text-green-400">
          {successMessage}
        </div>
      )}

      {/* Brand Presets Section */}
      <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-redd-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
          </svg>
          Brand Presets
        </h2>
        <p className="text-sm text-slate-400 mb-6">
          Set default brand settings that auto-fill when creating new projects.
        </p>

        <div className="space-y-6">
          {/* Brand Name */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Default Brand Name
            </label>
            <Input
              value={brandName}
              onChange={(e) => setBrandName(e.target.value)}
              placeholder="e.g., ACME Products"
              className="bg-slate-900 border-slate-700 text-white max-w-md"
            />
          </div>

          {/* Brand Colors */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Brand Colors
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {brandColors.map((color) => (
                <div
                  key={color}
                  className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5"
                >
                  <div
                    className="w-5 h-5 rounded-full border border-slate-600"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-sm text-white font-mono">{color}</span>
                  <button
                    onClick={() => removeColor(color)}
                    className="text-slate-400 hover:text-red-400"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2 max-w-xs">
              <input
                type="color"
                value={newColor}
                onChange={(e) => setNewColor(e.target.value)}
                className="w-12 h-10 rounded border border-slate-700 bg-slate-900 cursor-pointer"
              />
              <Input
                value={newColor}
                onChange={(e) => setNewColor(e.target.value)}
                className="bg-slate-900 border-slate-700 text-white font-mono flex-1"
                maxLength={7}
              />
              <Button
                variant="outline"
                onClick={addColor}
                className="border-slate-600 text-slate-300"
              >
                Add
              </Button>
            </div>
          </div>

          {/* Default Logo */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Default Logo
            </label>
            <div className="flex items-center gap-4">
              {selectedLogoPath && settings?.brand_presets.default_logo_url ? (
                <div className="relative w-20 h-20 bg-slate-900 rounded-lg border border-slate-700 overflow-hidden">
                  <img
                    src={settings.brand_presets.default_logo_url}
                    alt="Default logo"
                    className="w-full h-full object-contain p-2"
                  />
                  <button
                    onClick={() => setSelectedLogoPath(null)}
                    className="absolute top-1 right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowLogoPicker(true)}
                  className="w-20 h-20 bg-slate-900 rounded-lg border border-dashed border-slate-600 flex flex-col items-center justify-center text-slate-400 hover:border-redd-500 hover:text-redd-400 transition-colors"
                >
                  <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                  </svg>
                  <span className="text-xs">Select</span>
                </button>
              )}
              {logos.length === 0 && (
                <p className="text-sm text-slate-500">
                  No logos found. Upload a logo in a project first.
                </p>
              )}
            </div>
          </div>

          {/* Default Style Reference */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Default Style Reference
            </label>
            <div className="flex items-center gap-4">
              {selectedStyleRefPath && settings?.brand_presets.default_style_reference_url ? (
                <div className="relative w-20 h-20 bg-slate-900 rounded-lg border border-slate-700 overflow-hidden">
                  <img
                    src={settings.brand_presets.default_style_reference_url}
                    alt="Default style reference"
                    className="w-full h-full object-cover"
                  />
                  <button
                    onClick={() => setSelectedStyleRefPath(null)}
                    className="absolute top-1 right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowStyleRefPicker(true)}
                  className="w-20 h-20 bg-slate-900 rounded-lg border border-dashed border-slate-600 flex flex-col items-center justify-center text-slate-400 hover:border-redd-500 hover:text-redd-400 transition-colors"
                >
                  <svg className="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                  </svg>
                  <span className="text-xs">Select</span>
                </button>
              )}
              {styleRefs.length === 0 && (
                <p className="text-sm text-slate-500">
                  No style references found. Upload one in a project first.
                </p>
              )}
            </div>
          </div>

          <Button
            onClick={handleSaveBrandPresets}
            disabled={isSaving}
            className="bg-redd-500 hover:bg-redd-600 text-white"
          >
            {isSaving ? (
              <>
                <Spinner size="sm" className="text-current mr-2" />
                Saving...
              </>
            ) : (
              'Save Brand Presets'
            )}
          </Button>
        </div>
      </section>

      {/* Credits Balance Section */}
      <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-redd-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Credits
          {creditsInfo?.is_admin && (
            <span className="ml-2 px-2 py-0.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-bold rounded-full">
              ADMIN
            </span>
          )}
        </h2>

        <div className="flex items-center gap-6 mb-6">
          <div className="flex-1 bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
            {creditsInfo?.is_admin ? (
              <>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">∞</span>
                  <span className="text-slate-400">unlimited credits</span>
                </div>
                <p className="text-sm text-amber-400/80 mt-1">
                  Admin account - no credit limits apply
                </p>
              </>
            ) : (
              <>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-bold text-redd-400">{settings?.usage.credits_balance || 0}</span>
                  <span className="text-slate-400">credits remaining</span>
                </div>
                <p className="text-sm text-slate-500 mt-1">
                  {settings?.usage.plan_tier === 'free'
                    ? 'Lifetime credits (never reset)'
                    : 'Resets monthly on billing date'
                  }
                </p>
              </>
            )}
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-400">Current Plan</p>
            <p className="text-xl font-semibold text-white capitalize">
              {creditsInfo?.is_admin ? 'Admin' : (settings?.usage.plan_tier || 'Free')}
            </p>
          </div>
        </div>

        {/* Credit costs info */}
        <div className="bg-slate-900/30 rounded-lg p-4 border border-slate-700/30 mb-4">
          <h3 className="text-sm font-medium text-white mb-3">Credit Costs</h3>
          <div className="grid grid-cols-2 gap-4 text-sm mb-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Flash model (fast)</span>
              <span className="text-white font-mono">1 credit/image</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Pro model (best)</span>
              <span className="text-white font-mono">3 credits/image</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Framework analysis</span>
              <span className="text-white font-mono">1 credit</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Edit/Mobile transform</span>
              <span className="text-white font-mono">1 credit</span>
            </div>
          </div>
          <div className="border-t border-slate-700/50 pt-3">
            <h4 className="text-xs font-medium text-slate-400 mb-2">Full Listing Cost</h4>
            <div className="flex gap-4 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-slate-400">With Pro:</span>
                <span className="text-redd-400 font-bold">~47 credits</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400">With Flash:</span>
                <span className="text-green-400 font-bold">~23 credits</span>
              </div>
            </div>
          </div>
        </div>

        {/* Usage stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50 text-center">
            <p className="text-2xl font-bold text-white">{settings?.usage.projects_count || 0}</p>
            <p className="text-xs text-slate-400">Projects</p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50 text-center">
            <p className="text-2xl font-bold text-white">{settings?.usage.images_generated_total || 0}</p>
            <p className="text-xs text-slate-400">Images Total</p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50 text-center">
            <p className="text-2xl font-bold text-white">{settings?.usage.images_generated_this_month || 0}</p>
            <p className="text-xs text-slate-400">This Month</p>
          </div>
        </div>
      </section>

      {/* Amazon Seller Central Section */}
      <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-[#FF9900]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14.1 13.3c-1.3 1-3.2 1.5-4.8 1.5-2.3 0-4.3-.8-5.9-2.2-.1-.1 0-.3.1-.2 1.7 1 3.7 1.5 5.8 1.5 1.4 0 3-.3 4.4-.9.2-.1.4.1.4.3zm1.2-1.4c-.2-.2-1.1-.1-1.5-.1-.1 0-.2-.1-.1-.2.7-.5 2-.4 2.1-.2.2.2 0 1.5-.7 2.1-.1.1-.2 0-.2-.1.2-.4.4-1.3.4-1.5z" />
            <path d="M13.1 2.9C7.4 2.9 3.4 6.3 3.4 11c0 3 1.5 5.6 3.9 7.5.2.1.1.4-.1.4C5.2 19.3 2 17.3 2 12.7 2 7 6.8 2 13.1 2c3.7 0 7 1.8 8.9 4.5.1.2 0 .4-.2.3-1.4-.8-5.5-2.6-8.7-3.9z" />
          </svg>
          Amazon Seller Central
        </h2>
        <p className="text-sm text-slate-400 mb-6">
          Connect your Amazon Seller Central account to push listing images directly to your live listings.
        </p>

        {amazonMessage && (
          <div className={`rounded-lg p-3 text-sm mb-4 ${
            amazonMessage.type === 'success'
              ? 'bg-green-500/10 border border-green-500/50 text-green-400'
              : 'bg-red-500/10 border border-red-500/50 text-red-400'
          }`}>
            {amazonMessage.text}
          </div>
        )}

        {amazonLoading ? (
          <div className="flex items-center gap-3 py-4">
            <Spinner size="md" className="text-slate-400" />
            <span className="text-sm text-slate-400">Checking connection...</span>
          </div>
        ) : amazonAuth?.connected ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3 bg-green-500/10 border border-green-500/30 rounded-lg p-4">
              <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-green-400">Connected</p>
                <p className="text-xs text-slate-400">
                  Seller ID: {amazonAuth.seller_id || 'N/A'}
                  {amazonAuth.marketplace_id && ` | Marketplace: ${amazonAuth.marketplace_id}`}
                  {amazonAuth.connection_mode && amazonAuth.connection_mode !== 'none' && ` | Via: ${amazonAuth.connection_mode}`}
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              className="border-red-500/50 text-red-400 hover:bg-red-500/10"
              disabled={amazonDisconnecting}
              onClick={async () => {
                if (!window.confirm('Disconnect your Amazon Seller Central account? You can reconnect anytime.')) return;
                setAmazonDisconnecting(true);
                setAmazonMessage(null);
                try {
                  await apiClient.disconnectAmazon();
                  setAmazonAuth({ connected: false, seller_id: null, marketplace_id: '', connection_mode: 'none', last_connected_at: null });
                  setAmazonMessage({ type: 'success', text: 'Amazon account disconnected.' });
                } catch (err) {
                  console.error('Failed to disconnect:', err);
                  setAmazonMessage({ type: 'error', text: 'Failed to disconnect. Please try again.' });
                } finally {
                  setAmazonDisconnecting(false);
                }
              }}
            >
              {amazonDisconnecting ? (
                <>
                  <Spinner size="sm" className="text-current mr-2" />
                  Disconnecting...
                </>
              ) : (
                'Disconnect Amazon Account'
              )}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-3 bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
              <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.172 13.828a4 4 0 015.656 0l4-4a4 4 0 00-5.656-5.656l-1.102 1.101" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Not Connected</p>
                <p className="text-xs text-slate-500">Connect to push images directly to your Amazon listings</p>
              </div>
            </div>
            <Button
              className="bg-[#FF9900] hover:bg-[#e68a00] text-slate-900 font-medium"
              disabled={amazonConnecting}
              onClick={async () => {
                setAmazonConnecting(true);
                setAmazonMessage(null);
                try {
                  const { auth_url } = await apiClient.getAmazonAuthUrl();
                  window.location.href = auth_url;
                } catch (err) {
                  console.error('Failed to get auth URL:', err);
                  setAmazonMessage({ type: 'error', text: 'Failed to start Amazon connection. Please try again.' });
                  setAmazonConnecting(false);
                }
              }}
            >
              {amazonConnecting ? (
                <>
                  <Spinner size="sm" className="text-current mr-2" />
                  Connecting...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.172 13.828a4 4 0 015.656 0l4-4a4 4 0 00-5.656-5.656l-1.102 1.101" />
                  </svg>
                  Connect Amazon Account
                </>
              )}
            </Button>
          </div>
        )}
      </section>

      {/* Admin Credit Management Section - Only visible to admins */}
      {creditsInfo?.is_admin && (
        <section className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
            Admin: Credit Management
            <span className="ml-auto px-2 py-0.5 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-bold rounded-full">
              ADMIN ONLY
            </span>
          </h2>
          <p className="text-sm text-slate-400 mb-6">
            Adjust credits for any user by their email address. Use positive numbers to add credits, negative to subtract.
          </p>

          {adminError && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-400 text-sm mb-4">
              {adminError}
            </div>
          )}

          {adminResult && (
            <div className="bg-green-500/10 border border-green-500/50 rounded-lg p-3 text-green-400 text-sm mb-4">
              <strong>Success!</strong> Adjusted {adminResult.email}: {adminResult.previous_balance} → {adminResult.new_balance}
              ({adminResult.amount_adjusted > 0 ? '+' : ''}{adminResult.amount_adjusted} credits)
            </div>
          )}

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  User Email
                </label>
                <Input
                  type="email"
                  value={adminTargetEmail}
                  onChange={(e) => setAdminTargetEmail(e.target.value)}
                  placeholder="user@example.com"
                  className="bg-slate-900 border-slate-700 text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Amount
                </label>
                <Input
                  type="number"
                  value={adminAmount}
                  onChange={(e) => setAdminAmount(e.target.value)}
                  placeholder="e.g., 100 or -50"
                  className="bg-slate-900 border-slate-700 text-white"
                />
                <p className="text-xs text-slate-500 mt-1">Positive = add, Negative = subtract</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Reason (optional)
                </label>
                <Input
                  value={adminReason}
                  onChange={(e) => setAdminReason(e.target.value)}
                  placeholder="e.g., Beta tester bonus"
                  className="bg-slate-900 border-slate-700 text-white"
                />
              </div>
            </div>

            <Button
              onClick={async () => {
                if (!adminTargetEmail || !adminAmount) {
                  setAdminError('Please enter both email and amount');
                  return;
                }

                const amount = parseInt(adminAmount, 10);
                if (isNaN(amount)) {
                  setAdminError('Amount must be a valid number');
                  return;
                }

                setAdminAdjusting(true);
                setAdminError(null);
                setAdminResult(null);

                try {
                  const result = await apiClient.adjustUserCredits(
                    adminTargetEmail.trim(),
                    amount,
                    adminReason.trim()
                  );
                  setAdminResult(result);
                  setAdminTargetEmail('');
                  setAdminAmount('');
                  setAdminReason('');
                } catch (err: unknown) {
                  const error = err as { response?: { data?: { detail?: string } } };
                  setAdminError(error.response?.data?.detail || 'Failed to adjust credits');
                } finally {
                  setAdminAdjusting(false);
                }
              }}
              disabled={adminAdjusting || !adminTargetEmail || !adminAmount}
              className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
            >
              {adminAdjusting ? (
                <>
                  <Spinner size="sm" className="text-current mr-2" />
                  Adjusting...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Adjust Credits
                </>
              )}
            </Button>
          </div>
        </section>
      )}

      {/* Pricing Plans Section */}
      <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <svg className="w-5 h-5 text-redd-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
          </svg>
          Pricing
        </h2>
        <p className="text-sm text-slate-400 mb-6">Choose a plan that fits your needs</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {plans.map((plan) => {
            const isCurrentPlan = plan.id === currentPlan;
            const isPopular = plan.id === 'pro';

            return (
              <div
                key={plan.id}
                className={`relative rounded-xl border p-5 transition-all ${
                  isCurrentPlan
                    ? 'border-redd-500 bg-redd-500/5'
                    : isPopular
                    ? 'border-slate-600 bg-slate-800/50'
                    : 'border-slate-700/50 bg-slate-900/30'
                }`}
              >
                {isPopular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-redd-500 text-white text-xs font-medium px-3 py-1 rounded-full">
                    Popular
                  </div>
                )}

                <h3 className="text-lg font-semibold text-white">{plan.name}</h3>

                <div className="mt-3 mb-4">
                  <span className="text-3xl font-bold text-white">${plan.price}</span>
                  <span className="text-slate-400">/mo</span>
                </div>

                <div className="flex items-center gap-2 mb-4 text-sm">
                  <svg className="w-4 h-4 text-redd-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span className="text-white font-medium">
                    {plan.credits_per_period.toLocaleString()} credits/{plan.period}
                  </span>
                </div>

                <ul className="space-y-2 mb-5">
                  {plan.features.slice(0, 4).map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-slate-300">
                      <svg className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>

                <Button
                  className={`w-full ${
                    isCurrentPlan
                      ? 'bg-slate-700 text-slate-300 cursor-default'
                      : 'bg-redd-500 hover:bg-redd-600 text-white'
                  }`}
                  disabled={isCurrentPlan || plan.price > 0}
                >
                  {isCurrentPlan ? 'Current Plan' : plan.price === 0 ? 'Get Started' : 'Coming Soon'}
                </Button>
              </div>
            );
          })}
        </div>

        <p className="text-center text-sm text-slate-500 mt-6">
          Paid plans coming soon with Stripe integration
        </p>
      </section>

      {/* Account Section */}
      <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-redd-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
          Account
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
            <p className="text-white">{settings?.email || user?.email || 'Not available'}</p>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              className="border-slate-600 text-slate-300"
              onClick={() => {
                // TODO: Implement password change via Supabase
                window.alert('Password change will be available soon.');
              }}
            >
              Change Password
            </Button>
            <Button
              variant="outline"
              className="border-red-500/50 text-red-400 hover:bg-red-500/10"
              onClick={() => signOut()}
            >
              Sign Out
            </Button>
          </div>
        </div>
      </section>

      {/* Asset Picker Modals */}
      {showLogoPicker && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Select Logo</h3>
              <button
                onClick={() => setShowLogoPicker(false)}
                className="text-slate-400 hover:text-white"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {logos.length === 0 ? (
                <p className="text-center text-slate-400 py-8">
                  No logos found. Upload a logo in a project first.
                </p>
              ) : (
                <div className="grid grid-cols-4 gap-3">
                  {logos.map((logo) => (
                    <button
                      key={logo.id}
                      onClick={() => {
                        // Extract the path from the URL (it's in the query param)
                        const urlParams = new URLSearchParams(logo.url.split('?')[1]);
                        const path = urlParams.get('path') || logo.url;
                        setSelectedLogoPath(path);
                        setShowLogoPicker(false);
                      }}
                      className="aspect-square bg-slate-900 rounded-lg border border-slate-700 overflow-hidden hover:border-redd-500 transition-colors p-2"
                    >
                      <img
                        src={logo.url}
                        alt={logo.name}
                        className="w-full h-full object-contain"
                      />
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {showStyleRefPicker && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl border border-slate-700 max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Select Style Reference</h3>
              <button
                onClick={() => setShowStyleRefPicker(false)}
                className="text-slate-400 hover:text-white"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {styleRefs.length === 0 ? (
                <p className="text-center text-slate-400 py-8">
                  No style references found. Upload one in a project first.
                </p>
              ) : (
                <div className="grid grid-cols-4 gap-3">
                  {styleRefs.map((ref) => (
                    <button
                      key={ref.id}
                      onClick={() => {
                        const urlParams = new URLSearchParams(ref.url.split('?')[1]);
                        const path = urlParams.get('path') || ref.url;
                        setSelectedStyleRefPath(path);
                        setShowStyleRefPicker(false);
                      }}
                      className="aspect-square bg-slate-900 rounded-lg border border-slate-700 overflow-hidden hover:border-redd-500 transition-colors"
                    >
                      <img
                        src={ref.url}
                        alt={ref.name}
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
