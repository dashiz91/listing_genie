import React from 'react';
import { cn } from '@/lib/utils';

interface AmazonBreadcrumbsProps {
  category?: string;
  subcategory?: string;
  productTitle?: string;
  className?: string;
}

export const AmazonBreadcrumbs: React.FC<AmazonBreadcrumbsProps> = ({
  category = 'Home & Kitchen',
  subcategory = 'Home Décor Products',
  productTitle,
  className,
}) => {
  const crumbs = [
    { label: category, href: '#' },
    { label: subcategory, href: '#' },
  ];

  if (productTitle) {
    // Truncate long titles
    const truncated = productTitle.length > 40 ? productTitle.slice(0, 40) + '...' : productTitle;
    crumbs.push({ label: truncated, href: '#' });
  }

  return (
    <nav className={cn('px-4 py-2 text-xs', className)}>
      <ol className="flex items-center flex-wrap gap-1">
        {crumbs.map((crumb, index) => (
          <li key={index} className="flex items-center">
            {index > 0 && (
              <svg
                className="w-3 h-3 mx-1 text-[#565959]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
            <a
              href={crumb.href}
              className={cn(
                'hover:text-[#C7511F] hover:underline',
                index === crumbs.length - 1 ? 'text-[#565959]' : 'text-[#007185]'
              )}
            >
              {crumb.label}
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
};
