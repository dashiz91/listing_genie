import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { apiClient, AssetItem } from '../api/client';

type AssetType = 'logos' | 'style-refs' | 'products' | 'generated';

export const AssetsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AssetType>('products');
  const [assets, setAssets] = useState<AssetItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAssets = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.listAssets('all');
      setAssets(response.assets);
    } catch (err) {
      console.error('Failed to fetch assets:', err);
      setError('Failed to load assets. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAssets();
  }, [fetchAssets]);

  const EmptyState = ({ type }: { type: AssetType }) => {
    const config = {
      logos: {
        title: 'No logos yet',
        description: 'Brand logos from your projects will appear here.',
        icon: (
          <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
          </svg>
        ),
      },
      'style-refs': {
        title: 'No style references yet',
        description: 'Style reference images from your projects will appear here.',
        icon: (
          <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
          </svg>
        ),
      },
      products: {
        title: 'No product photos yet',
        description: 'Product photos from your projects will appear here.',
        icon: (
          <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
          </svg>
        ),
      },
      generated: {
        title: 'No generated images yet',
        description: 'AI-generated listing images from your projects will appear here.',
        icon: (
          <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
          </svg>
        ),
      },
    };

    const { title, description, icon } = config[type];

    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center mb-6">
          {icon}
        </div>
        <h3 className="text-lg font-medium text-white mb-2">{title}</h3>
        <p className="text-slate-400 text-center max-w-md">{description}</p>
      </div>
    );
  };

  const LoadingState = () => (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="w-12 h-12 border-4 border-slate-600 border-t-redd-500 rounded-full animate-spin mb-4" />
      <p className="text-slate-400">Loading assets...</p>
    </div>
  );

  const AssetGrid = ({ type }: { type: AssetType }) => {
    const filteredAssets = assets.filter(a => a.type === type);

    if (isLoading) {
      return <LoadingState />;
    }

    if (filteredAssets.length === 0) {
      return <EmptyState type={type} />;
    }

    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {filteredAssets.map(asset => (
          <div
            key={asset.id}
            className="group relative bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden
                       hover:border-redd-500/50 hover:bg-slate-800/80 transition-all duration-200"
          >
            <div className="aspect-square">
              <img
                src={asset.url}
                alt={asset.name}
                className="w-full h-full object-cover"
                loading="lazy"
                onError={(e) => {
                  // Hide broken images
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            </div>
            <div className="p-3">
              <p className="text-sm text-white truncate" title={asset.name}>{asset.name}</p>
              <p className="text-xs text-slate-500">
                {new Date(asset.created_at).toLocaleDateString()}
              </p>
            </div>
            {/* Hover overlay */}
            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
              <Button
                size="sm"
                variant="outline"
                className="border-white/50 text-white hover:bg-white/10"
                onClick={() => {
                  // Open in new tab to view full size
                  window.open(asset.url, '_blank');
                }}
              >
                View
              </Button>
              {asset.session_id && (
                <Button
                  size="sm"
                  variant="outline"
                  className="border-redd-500/50 text-redd-400 hover:bg-redd-500/10"
                  onClick={() => {
                    // Navigate to project
                    window.location.href = `/app?session=${asset.session_id}`;
                  }}
                >
                  Open Project
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Count assets per category
  const logosCount = assets.filter(a => a.type === 'logos').length;
  const styleRefsCount = assets.filter(a => a.type === 'style-refs').length;
  const productsCount = assets.filter(a => a.type === 'products').length;
  const generatedCount = assets.filter(a => a.type === 'generated').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Assets</h1>
          <p className="text-slate-400 mt-1">
            Browse assets from all your projects
          </p>
        </div>
        <Button
          variant="outline"
          className="border-slate-600 text-slate-300 hover:bg-slate-800"
          onClick={fetchAssets}
          disabled={isLoading}
        >
          <svg className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </Button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as AssetType)} className="w-full">
        <TabsList className="bg-slate-800 border border-slate-700">
          <TabsTrigger
            value="products"
            className="data-[state=active]:bg-slate-700 data-[state=active]:text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
            </svg>
            Products {productsCount > 0 && <span className="ml-1.5 text-xs bg-slate-600 px-1.5 py-0.5 rounded-full">{productsCount}</span>}
          </TabsTrigger>
          <TabsTrigger
            value="generated"
            className="data-[state=active]:bg-slate-700 data-[state=active]:text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
            </svg>
            Generated {generatedCount > 0 && <span className="ml-1.5 text-xs bg-slate-600 px-1.5 py-0.5 rounded-full">{generatedCount}</span>}
          </TabsTrigger>
          <TabsTrigger
            value="logos"
            className="data-[state=active]:bg-slate-700 data-[state=active]:text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
            </svg>
            Logos {logosCount > 0 && <span className="ml-1.5 text-xs bg-slate-600 px-1.5 py-0.5 rounded-full">{logosCount}</span>}
          </TabsTrigger>
          <TabsTrigger
            value="style-refs"
            className="data-[state=active]:bg-slate-700 data-[state=active]:text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
            </svg>
            Style Refs {styleRefsCount > 0 && <span className="ml-1.5 text-xs bg-slate-600 px-1.5 py-0.5 rounded-full">{styleRefsCount}</span>}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="products" className="mt-6">
          <AssetGrid type="products" />
        </TabsContent>
        <TabsContent value="generated" className="mt-6">
          <AssetGrid type="generated" />
        </TabsContent>
        <TabsContent value="logos" className="mt-6">
          <AssetGrid type="logos" />
        </TabsContent>
        <TabsContent value="style-refs" className="mt-6">
          <AssetGrid type="style-refs" />
        </TabsContent>
      </Tabs>
    </div>
  );
};
