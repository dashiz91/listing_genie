/**
 * StyleLibrary - Browse and select pre-generated styles
 *
 * Shows categorized styles that users can browse without spending credits.
 * Selecting a style applies it as the style reference for generation.
 */
import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet';

interface StylePreset {
  id: string;
  name: string;
  category: string;
  description: string;
  colors: string[];
  preview_image: string;
  tags: string[];
}

interface Category {
  id: string;
  name: string;
  description: string;
}

interface StyleLibraryProps {
  open: boolean;
  onClose: () => void;
  onSelectStyle: (style: StylePreset) => void;
  selectedStyleId?: string;
}

// Fallback data if API fails
const FALLBACK_CATEGORIES: Category[] = [
  { id: 'seasonal', name: 'Seasonal', description: 'Holiday and seasonal themes' },
  { id: 'minimalist', name: 'Minimalist', description: 'Clean, simple, modern designs' },
  { id: 'luxury', name: 'Luxury', description: 'Premium, high-end aesthetics' },
  { id: 'vibrant', name: 'Vibrant', description: 'Bold, colorful, energetic styles' },
  { id: 'natural', name: 'Natural', description: 'Organic, earthy, eco-friendly looks' },
  { id: 'iconic', name: 'Iconic', description: 'Inspired by world-famous brand aesthetics' },
];

const FALLBACK_STYLES: StylePreset[] = [
  // Seasonal
  {
    id: 'christmas',
    name: 'Holiday Magic',
    category: 'seasonal',
    description: 'Festive red and green with golden accents',
    colors: ['#C41E3A', '#165B33', '#D4AF37', '#FFFFFF'],
    preview_image: '/styles/christmas.png',
    tags: ['christmas', 'holiday', 'winter'],
  },
  // Minimalist
  {
    id: 'clean-white',
    name: 'Pure & Simple',
    category: 'minimalist',
    description: 'Clean white backgrounds with subtle shadows',
    colors: ['#FFFFFF', '#F5F5F5', '#333333', '#666666'],
    preview_image: '/styles/clean-white.png',
    tags: ['minimal', 'clean', 'white'],
  },
  // Luxury
  {
    id: 'gold-luxe',
    name: 'Golden Hour',
    category: 'luxury',
    description: 'Rich gold accents with deep backgrounds',
    colors: ['#D4AF37', '#1A1A2E', '#B8860B', '#000000'],
    preview_image: '/styles/gold-luxe.png',
    tags: ['gold', 'luxury', 'premium'],
  },
  // Vibrant
  {
    id: 'neon-pop',
    name: 'Neon Pop',
    category: 'vibrant',
    description: 'Bold neon colors that demand attention',
    colors: ['#FF00FF', '#00FFFF', '#FFFF00', '#1A1A2E'],
    preview_image: '/styles/neon-pop.png',
    tags: ['neon', 'bold', 'bright'],
  },
  // Natural
  {
    id: 'earth-tones',
    name: 'Earth & Clay',
    category: 'natural',
    description: 'Warm terracotta and natural earth tones',
    colors: ['#CC7351', '#D4A574', '#8B7355', '#3D2B1F'],
    preview_image: '/styles/earth-tones.png',
    tags: ['earth', 'natural', 'organic'],
  },
  // Iconic (brand-inspired)
  {
    id: 'tech-minimal',
    name: 'Tech Minimal',
    category: 'iconic',
    description: 'Ultra-clean premium tech aesthetic with perfect lighting',
    colors: ['#FFFFFF', '#F5F5F5', '#86868B', '#1D1D1F'],
    preview_image: '/styles/tech-minimal.png',
    tags: ['tech', 'minimal', 'premium'],
  },
  {
    id: 'athletic-energy',
    name: 'Athletic Energy',
    category: 'iconic',
    description: 'Bold, dynamic, empowering sports aesthetic',
    colors: ['#000000', '#FFFFFF', '#FF5722', '#1A1A1A'],
    preview_image: '/styles/athletic-energy.png',
    tags: ['athletic', 'bold', 'dynamic'],
  },
  {
    id: 'sport-stripes',
    name: 'Sport Stripes',
    category: 'iconic',
    description: 'Clean sporty design with iconic stripe elements',
    colors: ['#000000', '#FFFFFF', '#1A1A1A', '#E0E0E0'],
    preview_image: '/styles/sport-stripes.png',
    tags: ['sporty', 'stripes', 'athletic'],
  },
  {
    id: 'cosmic-dark',
    name: 'Cosmic Dark',
    category: 'iconic',
    description: 'Futuristic space-age aesthetic with sleek minimalism',
    colors: ['#0A0A0A', '#1A1A2E', '#00D4FF', '#FFFFFF'],
    preview_image: '/styles/cosmic-dark.png',
    tags: ['futuristic', 'space', 'tech'],
  },
  {
    id: 'heritage-craft',
    name: 'Heritage Craft',
    category: 'iconic',
    description: 'Timeless luxury with rich heritage patterns',
    colors: ['#5C4033', '#D4A574', '#C9A961', '#1A1A1A'],
    preview_image: '/styles/heritage-craft.png',
    tags: ['luxury', 'heritage', 'elegant'],
  },
  {
    id: 'playful-pop',
    name: 'Playful Pop',
    category: 'iconic',
    description: 'Bright, friendly, and approachable with primary colors',
    colors: ['#4285F4', '#EA4335', '#FBBC05', '#34A853'],
    preview_image: '/styles/playful-pop.png',
    tags: ['playful', 'colorful', 'friendly'],
  },
];

export const StyleLibrary: React.FC<StyleLibraryProps> = ({
  open,
  onClose,
  onSelectStyle,
  selectedStyleId,
}) => {
  const [categories, setCategories] = useState<Category[]>(FALLBACK_CATEGORIES);
  const [styles, setStyles] = useState<StylePreset[]>(FALLBACK_STYLES);
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [hoveredStyle, setHoveredStyle] = useState<string | null>(null);

  // Fetch styles from API
  useEffect(() => {
    if (!open) return;

    const fetchStyles = async () => {
      try {
        const API_BASE = import.meta.env.VITE_API_URL || '';
        const response = await fetch(`${API_BASE}/api/styles`);
        if (response.ok) {
          const data = await response.json();
          setCategories(data.categories || FALLBACK_CATEGORIES);
          setStyles(data.styles || FALLBACK_STYLES);
        }
      } catch (error) {
        console.error('Failed to fetch styles:', error);
        // Keep fallback data
      } finally {
        setLoading(false);
      }
    };

    fetchStyles();
  }, [open]);

  // IDs of styles that have actual preview images generated
  const STYLES_WITH_IMAGES = [
    'christmas', 'clean-white', 'gold-luxe', 'neon-pop', 'earth-tones',
    'tech-minimal', 'athletic-energy', 'sport-stripes', 'cosmic-dark', 'heritage-craft', 'playful-pop'
  ];

  // Filter styles: only show ones with preview images, then by category
  const filteredStyles = styles
    .filter(s => STYLES_WITH_IMAGES.includes(s.id))
    .filter(s => activeCategory === 'all' || s.category === activeCategory);

  return (
    <Sheet open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-2xl bg-slate-900 border-slate-800 overflow-y-auto"
      >
        <SheetHeader className="pb-4 border-b border-slate-800">
          <SheetTitle className="text-white text-xl flex items-center gap-2">
            <span className="text-2xl">🎨</span>
            Style Library
          </SheetTitle>
          <SheetDescription className="text-slate-400">
            Browse pre-made styles to use as your design foundation. No credits required to preview!
          </SheetDescription>
        </SheetHeader>

        {/* Category tabs */}
        <div className="flex gap-2 mt-4 pb-4 overflow-x-auto">
          <button
            onClick={() => setActiveCategory('all')}
            className={cn(
              'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all',
              activeCategory === 'all'
                ? 'bg-redd-500 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
            )}
          >
            All Styles
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={cn(
                'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all',
                activeCategory === cat.id
                  ? 'bg-redd-500 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
              )}
            >
              {cat.name}
            </button>
          ))}
        </div>

        {/* Category description */}
        {activeCategory !== 'all' && (
          <p className="text-sm text-slate-500 mb-4">
            {categories.find(c => c.id === activeCategory)?.description}
          </p>
        )}

        {/* Styles grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-redd-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 pb-6">
            {filteredStyles.map((style) => {
              const isSelected = selectedStyleId === style.id;
              const isHovered = hoveredStyle === style.id;

              return (
                <button
                  key={style.id}
                  onClick={() => {
                    onSelectStyle(style);
                    onClose();
                  }}
                  onMouseEnter={() => setHoveredStyle(style.id)}
                  onMouseLeave={() => setHoveredStyle(null)}
                  className={cn(
                    'relative group rounded-xl overflow-hidden border-2 transition-all text-left',
                    isSelected
                      ? 'border-redd-500 ring-2 ring-redd-500/30'
                      : 'border-slate-700 hover:border-slate-500'
                  )}
                >
                  {/* Preview image - vertical strip format */}
                  <div className="aspect-[9/16] relative overflow-hidden bg-slate-800">
                    <img
                      src={style.preview_image}
                      alt={style.name}
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />

                    {/* Hover overlay */}
                    <div className={cn(
                      'absolute inset-0 bg-black/60 flex items-center justify-center transition-opacity',
                      isHovered ? 'opacity-100' : 'opacity-0'
                    )}>
                      <span className="text-white font-medium px-4 py-2 bg-redd-500 rounded-full text-sm">
                        {isSelected ? '✓ Selected' : 'Use This Style'}
                      </span>
                    </div>

                    {/* Selected badge */}
                    {isSelected && (
                      <div className="absolute top-2 right-2 w-6 h-6 bg-redd-500 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    )}
                  </div>

                  {/* Style info */}
                  <div className="p-3 bg-slate-800">
                    <h3 className="font-medium text-white text-sm">{style.name}</h3>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-1">{style.description}</p>

                    {/* Color swatches */}
                    <div className="flex gap-1 mt-2">
                      {style.colors.slice(0, 4).map((color, idx) => (
                        <div
                          key={idx}
                          className="w-4 h-4 rounded-full border border-slate-600"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Empty state */}
        {!loading && filteredStyles.length === 0 && (
          <div className="text-center py-12">
            <span className="text-4xl">🎨</span>
            <p className="text-slate-400 mt-2">No styles in this category yet</p>
          </div>
        )}

        {/* Footer hint */}
        <div className="sticky bottom-0 bg-slate-900 border-t border-slate-800 py-4 -mx-6 px-6">
          <p className="text-xs text-slate-500 text-center">
            💡 Selecting a style uses it as your design reference. Your product photos + this style = amazing listings!
          </p>
        </div>
      </SheetContent>
    </Sheet>
  );
};

export default StyleLibrary;
