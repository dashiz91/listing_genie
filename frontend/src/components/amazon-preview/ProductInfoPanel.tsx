import React from 'react';
import { cn } from '@/lib/utils';

interface ProductInfoPanelProps {
  productTitle: string;
  brandName?: string;
  features: (string | undefined)[];
  price?: string;
  listPrice?: string;
  className?: string;
}

export const ProductInfoPanel: React.FC<ProductInfoPanelProps> = ({
  productTitle,
  brandName,
  features,
  price = '$29.99',
  listPrice = '$39.99',
  className,
}) => {
  // Filter out undefined features
  const validFeatures = features.filter(Boolean) as string[];

  // Generate a random delivery date (2-5 days from now)
  const deliveryDate = new Date();
  deliveryDate.setDate(deliveryDate.getDate() + 3);
  const deliveryDateStr = deliveryDate.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  });

  return (
    <div className={cn('flex flex-col gap-2 text-left', className)}>
      {/* Brand Name (Amazon teal link style) */}
      {brandName && (
        <a href="#" className="text-sm text-[#007185] hover:text-[#C7511F] hover:underline">
          Visit the {brandName} Store
        </a>
      )}

      {/* Product Title */}
      <h1 className="text-lg md:text-xl font-normal text-[#0F1111] leading-tight">
        {productTitle}
      </h1>

      {/* Rating Row */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Star Rating */}
        <div className="flex items-center gap-1">
          <span className="text-sm text-[#007185]">4.5</span>
          <div className="flex">
            {[1, 2, 3, 4].map((i) => (
              <svg
                key={i}
                className="w-4 h-4 text-[#FF9900] fill-current"
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            ))}
            {/* Half star */}
            <svg className="w-4 h-4 text-[#FF9900]" viewBox="0 0 20 20">
              <defs>
                <linearGradient id="half-star-gradient">
                  <stop offset="50%" stopColor="#FF9900" />
                  <stop offset="50%" stopColor="#E0E0E0" />
                </linearGradient>
              </defs>
              <path
                fill="url(#half-star-gradient)"
                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
              />
            </svg>
          </div>
        </div>
        <a href="#" className="text-sm text-[#007185] hover:text-[#C7511F] hover:underline">
          1,247 ratings
        </a>
        <span className="text-slate-300">|</span>
        <a href="#" className="text-sm text-[#007185] hover:text-[#C7511F] hover:underline">
          Search this page
        </a>
      </div>

      {/* Amazon Choice Badge (optional mockup) */}
      <div className="inline-flex items-center gap-1 bg-[#002F36] text-white text-xs px-2 py-1 rounded-sm w-fit">
        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
        </svg>
        <span className="font-medium">Amazon&apos;s</span>
        <span className="font-light">Choice</span>
      </div>

      {/* Divider */}
      <hr className="border-slate-200 my-1" />

      {/* Price Section */}
      <div className="space-y-1">
        <div className="flex items-baseline gap-2">
          <span className="text-[#565959] text-sm">-25%</span>
          <span className="text-[28px] text-[#0F1111] font-light">
            <sup className="text-sm align-top">$</sup>
            <span>{price.replace('$', '').split('.')[0]}</span>
            <sup className="text-sm align-top">{price.includes('.') ? price.split('.')[1] : '99'}</sup>
          </span>
        </div>
        <div className="text-sm text-[#565959]">
          List Price: <span className="line-through">{listPrice}</span>
        </div>
      </div>

      {/* Prime Badge */}
      <div className="flex items-center gap-2 mt-1">
        <div className="flex items-center">
          <svg className="w-12 h-5" viewBox="0 0 70 20" fill="none">
            <rect width="70" height="20" rx="2" fill="#232F3E" />
            <text x="6" y="14" fill="white" fontSize="10" fontFamily="Arial" fontWeight="bold">
              prime
            </text>
            <path d="M50 10c3 0 5.5 2.5 5.5 5.5h2c0-4.1-3.4-7.5-7.5-7.5v2z" fill="#FF9900" />
          </svg>
        </div>
        <span className="text-sm text-[#565959]">FREE delivery</span>
      </div>

      {/* Delivery Info */}
      <div className="text-sm">
        <span className="text-[#0F1111]">FREE delivery </span>
        <span className="font-bold text-[#0F1111]">{deliveryDateStr}</span>
        <span className="text-[#0F1111]">. Order within </span>
        <span className="text-[#007600]">2 hrs 15 mins</span>
      </div>

      {/* Location */}
      <div className="flex items-center gap-1 text-sm text-[#007185]">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <a href="#" className="hover:text-[#C7511F] hover:underline">
          Deliver to Your Location
        </a>
      </div>

      {/* Stock Status */}
      <p className="text-lg text-[#007600] font-medium mt-2">In Stock</p>

      {/* Quantity Selector */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-[#0F1111]">Qty:</span>
        <select
          className="bg-[#F0F2F2] border border-[#D5D9D9] rounded-lg px-3 py-1 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#007185]"
          defaultValue="1"
        >
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
            <option key={num} value={num}>
              {num}
            </option>
          ))}
        </select>
      </div>

      {/* Add to Cart / Buy Now Buttons */}
      <div className="space-y-2 mt-2">
        <button
          disabled
          className="w-full py-2 px-4 bg-[#FFD814] hover:bg-[#F7CA00] text-[#0F1111] text-sm font-normal rounded-full transition-colors cursor-not-allowed border border-[#FCD200] shadow-sm"
        >
          Add to Cart
        </button>
        <button
          disabled
          className="w-full py-2 px-4 bg-[#FFA41C] hover:bg-[#FA8900] text-[#0F1111] text-sm font-normal rounded-full transition-colors cursor-not-allowed border border-[#FF8F00] shadow-sm"
        >
          Buy Now
        </button>
      </div>

      {/* Secure transaction */}
      <div className="flex items-center gap-1 text-xs text-[#565959] mt-1">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span>Secure transaction</span>
      </div>

      {/* Sold by / Fulfilled by */}
      <div className="text-sm">
        <span className="text-[#565959]">Ships from </span>
        <span className="text-[#007185]">Amazon</span>
      </div>
      <div className="text-sm">
        <span className="text-[#565959]">Sold by </span>
        <a href="#" className="text-[#007185] hover:text-[#C7511F] hover:underline">
          {brandName || 'Amazon Seller'}
        </a>
      </div>

      {/* Divider */}
      <hr className="border-slate-200 my-2" />

      {/* Features / Bullet Points */}
      {validFeatures.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-bold text-[#0F1111]">About this item</p>
          <ul className="space-y-1.5 text-sm text-[#0F1111]">
            {validFeatures.map((feature, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-[#0F1111] mt-0.5">•</span>
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Preview notice */}
      <p className="text-[10px] text-[#565959] text-center mt-4 border-t border-slate-200 pt-2">
        Preview only - This is a mockup of how your listing will appear
      </p>
    </div>
  );
};
