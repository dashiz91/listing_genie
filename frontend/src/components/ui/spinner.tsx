import React from 'react';
import { cn } from '@/lib/utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeMap = {
  sm: 'w-4 h-4 border-[1.5px]',
  md: 'w-5 h-5 border-2',
  lg: 'w-8 h-8 border-2',
  xl: 'w-12 h-12 border-[3px]',
};

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className }) => (
  <div
    className={cn(
      'rounded-full animate-spin border-current/25 border-t-current',
      sizeMap[size],
      className
    )}
    role="status"
    aria-label="Loading"
  />
);
