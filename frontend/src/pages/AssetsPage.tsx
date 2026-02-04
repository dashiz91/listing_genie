import React, { useState } from 'react';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

type AssetType = 'logos' | 'style-refs' | 'products';

interface Asset {
  id: string;
  name: string;
  url: string;
  type: AssetType;
  createdAt: Date;
}

export const AssetsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AssetType>('logos');
  const [assets] = useState<Asset[]>([]); // Will be populated from API later

  const EmptyState = ({ type }: { type: AssetType }) => {
    const config = {
      logos: {
        title: 'No logos yet',
        description: 'Upload your brand logos to reuse across all your listings.',
        icon: (
          <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
          </svg>
        ),
      },
      'style-refs': {
        title: 'No style references yet',
        description: 'Save style reference images to maintain consistent branding across listings.',
        icon: (
          <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
          </svg>
        ),
      },
      products: {
        title: 'No product photos yet',
        description: 'Build a library of product photos to quickly create new listings.',
        icon: (
          <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
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
        <p className="text-slate-400 text-center max-w-md mb-6">{description}</p>
        <Button className="bg-redd-500 hover:bg-redd-600 text-white">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Upload {type === 'logos' ? 'Logo' : type === 'style-refs' ? 'Style Reference' : 'Product Photo'}
        </Button>
      </div>
    );
  };

  const AssetGrid = ({ type }: { type: AssetType }) => {
    const filteredAssets = assets.filter(a => a.type === type);

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
              />
            </div>
            <div className="p-3">
              <p className="text-sm text-white truncate">{asset.name}</p>
              <p className="text-xs text-slate-500">
                {asset.createdAt.toLocaleDateString()}
              </p>
            </div>
            {/* Hover overlay */}
            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
              <Button size="sm" variant="outline" className="border-white/50 text-white hover:bg-white/10">
                Use
              </Button>
              <Button size="sm" variant="outline" className="border-red-500/50 text-red-400 hover:bg-red-500/10">
                Delete
              </Button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Assets</h1>
          <p className="text-slate-400 mt-1">
            Manage your reusable logos, style references, and product photos
          </p>
        </div>
        <Button className="bg-redd-500 hover:bg-redd-600 text-white">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Upload Asset
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as AssetType)} className="w-full">
        <TabsList className="bg-slate-800 border border-slate-700">
          <TabsTrigger
            value="logos"
            className="data-[state=active]:bg-slate-700 data-[state=active]:text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5M9 11.25v1.5M12 9v3.75m3-6v6" />
            </svg>
            Logos
          </TabsTrigger>
          <TabsTrigger
            value="style-refs"
            className="data-[state=active]:bg-slate-700 data-[state=active]:text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.53 16.122a3 3 0 00-5.78 1.128 2.25 2.25 0 01-2.4 2.245 4.5 4.5 0 008.4-2.245c0-.399-.078-.78-.22-1.128zm0 0a15.998 15.998 0 003.388-1.62m-5.043-.025a15.994 15.994 0 011.622-3.395m3.42 3.42a15.995 15.995 0 004.764-4.648l3.876-5.814a1.151 1.151 0 00-1.597-1.597L14.146 6.32a15.996 15.996 0 00-4.649 4.763m3.42 3.42a6.776 6.776 0 00-3.42-3.42" />
            </svg>
            Style References
          </TabsTrigger>
          <TabsTrigger
            value="products"
            className="data-[state=active]:bg-slate-700 data-[state=active]:text-white"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
            </svg>
            Product Photos
          </TabsTrigger>
        </TabsList>

        <TabsContent value="logos" className="mt-6">
          <AssetGrid type="logos" />
        </TabsContent>
        <TabsContent value="style-refs" className="mt-6">
          <AssetGrid type="style-refs" />
        </TabsContent>
        <TabsContent value="products" className="mt-6">
          <AssetGrid type="products" />
        </TabsContent>
      </Tabs>

      {/* Coming Soon Notice */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4 mt-8">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-redd-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="text-sm font-medium text-white">Coming Soon</h4>
            <p className="text-sm text-slate-400 mt-1">
              Asset management is under development. Soon you'll be able to upload and organize your logos,
              style references, and product photos to quickly reuse them across all your listings.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
