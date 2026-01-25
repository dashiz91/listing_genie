import React from 'react';
import { cn } from '@/lib/utils';

interface ProductInfoPanelProps {
  productTitle: string;
  brandName?: string;
  features: (string | undefined)[];
  price?: string;
  className?: string;
}

export const ProductInfoPanel: React.FC<ProductInfoPanelProps> = ({
  productTitle,
  brandName,
  features,
  price = '$XX.XX',
  className,
}) => {
  // Filter out undefined features
  const validFeatures = features.filter(Boolean) as string[];

  return (
    <div className={cn('flex flex-col gap-4 text-left', className)}>
      {/* Brand Name (link style) */}
      {brandName && (
        <a href="#" className="text-sm text-teal-600 hover:text-teal-700 hover:underline">
          {brandName}
        </a>
      )}

      {/* Product Title */}
      <h1 className="text-xl font-normal text-slate-900 leading-tight">
        {productTitle}
      </h1>

      {/* Rating (mockup) */}
      <div className="flex items-center gap-2">
        <div className="flex">
          {[1, 2, 3, 4].map((i) => (
            <svg
              key={i}
              className="w-4 h-4 text-amber-400 fill-current"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          ))}
          {/* Half star */}
          <svg className="w-4 h-4 text-amber-400" viewBox="0 0 20 20">
            <defs>
              <linearGradient id="half-star">
                <stop offset="50%" stopColor="currentColor" />
                <stop offset="50%" stopColor="#E5E7EB" />
              </linearGradient>
            </defs>
            <path
              fill="url(#half-star)"
              d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
            />
          </svg>
        </div>
        <span className="text-sm text-teal-600 hover:text-teal-700 hover:underline cursor-pointer">
          4.5
        </span>
        <span className="text-sm text-slate-500">(1,247 ratings)</span>
      </div>

      {/* Divider */}
      <hr className="border-slate-200" />

      {/* Price */}
      <div>
        <span className="text-sm text-slate-600">Price: </span>
        <span className="text-2xl font-medium text-slate-900">{price}</span>
      </div>

      {/* Features / Bullet Points */}
      {validFeatures.length > 0 && (
        <div className="space-y-1">
          <p className="text-sm font-medium text-slate-700">About this item</p>
          <ul className="space-y-1.5 text-sm text-slate-700">
            {validFeatures.map((feature, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-slate-400 mt-1">•</span>
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Add to Cart Button (mockup) */}
      <div className="mt-4 space-y-2">
        <button
          disabled
          className="w-full py-2 px-4 bg-amber-400 hover:bg-amber-500 text-slate-900 text-sm font-medium rounded-full transition-colors cursor-not-allowed opacity-70"
        >
          Add to Cart
        </button>
        <button
          disabled
          className="w-full py-2 px-4 bg-amber-500 hover:bg-amber-600 text-slate-900 text-sm font-medium rounded-full transition-colors cursor-not-allowed opacity-70"
        >
          Buy Now
        </button>
        <p className="text-xs text-slate-500 text-center mt-2">
          (Preview only - buttons disabled)
        </p>
      </div>
    </div>
  );
};
