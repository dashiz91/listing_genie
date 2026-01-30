import React from 'react';
import { cn } from '@/lib/utils';

interface AmazonHeaderProps {
  className?: string;
}

export const AmazonHeader: React.FC<AmazonHeaderProps> = ({ className }) => {
  return (
    <div className={cn('bg-[#131921] text-white', className)}>
      {/* Main header */}
      <div className="flex items-center gap-4 px-4 py-2">
        {/* Amazon Logo */}
        <div className="flex items-center gap-1 flex-shrink-0">
          <span className="text-xl font-bold tracking-tight">amazon</span>
          <svg
            className="w-4 h-4 text-[#FF9900] mt-1"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M12 21c-5.5 0-10-4.5-10-10h2c0 4.4 3.6 8 8 8s8-3.6 8-8h2c0 5.5-4.5 10-10 10z" />
          </svg>
        </div>

        {/* Delivery Location */}
        <div className="hidden sm:flex items-center gap-1 text-xs flex-shrink-0">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <div className="leading-tight">
            <p className="text-[#CCCCCC] text-[10px]">Deliver to</p>
            <p className="font-medium text-xs">Location</p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 flex">
          <select className="hidden md:block bg-[#E6E6E6] text-[#555555] text-xs px-2 py-2 rounded-l-md border-r border-[#CDCDCD] focus:outline-none">
            <option>All</option>
          </select>
          <input
            type="text"
            placeholder="Search Amazon"
            className="flex-1 px-3 py-2 text-sm text-slate-900 bg-white focus:outline-none rounded-l-md md:rounded-l-none min-w-0"
          />
          <button className="bg-[#FEBD69] hover:bg-[#F3A847] px-3 py-2 rounded-r-md">
            <svg className="w-5 h-5 text-[#131921]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </div>

        {/* Account & Lists */}
        <div className="hidden lg:block text-xs flex-shrink-0">
          <p className="text-[#CCCCCC] text-[10px]">Hello, Sign in</p>
          <p className="font-medium">Account & Lists</p>
        </div>

        {/* Orders */}
        <div className="hidden lg:block text-xs flex-shrink-0">
          <p className="text-[#CCCCCC] text-[10px]">Returns</p>
          <p className="font-medium">& Orders</p>
        </div>

        {/* Cart */}
        <div className="flex items-center gap-1 flex-shrink-0">
          <div className="relative">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span className="absolute -top-1 right-0 bg-[#F08804] text-[#131921] text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
              0
            </span>
          </div>
          <span className="hidden sm:block text-sm font-medium">Cart</span>
        </div>
      </div>

      {/* Sub-nav */}
      <div className="bg-[#232F3E] px-4 py-1.5 flex items-center gap-4 text-sm overflow-x-auto">
        <button className="flex items-center gap-1 hover:text-[#FF9900] whitespace-nowrap">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          All
        </button>
        <a href="#" className="hover:text-[#FF9900] whitespace-nowrap">Today&apos;s Deals</a>
        <a href="#" className="hover:text-[#FF9900] whitespace-nowrap hidden sm:inline">Customer Service</a>
        <a href="#" className="hover:text-[#FF9900] whitespace-nowrap hidden md:inline">Registry</a>
        <a href="#" className="hover:text-[#FF9900] whitespace-nowrap hidden md:inline">Gift Cards</a>
        <a href="#" className="hover:text-[#FF9900] whitespace-nowrap hidden lg:inline">Sell</a>
      </div>
    </div>
  );
};
