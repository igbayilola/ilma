import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, ArrowLeft } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  to?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  if (items.length === 0) return null;

  // Mobile: show only back arrow + parent label
  const parentItem = items.length >= 2 ? items[items.length - 2] : null;

  return (
    <>
      {/* Desktop breadcrumb */}
      <nav aria-label="Fil d'Ariane" className="hidden md:flex items-center text-sm font-medium text-gray-500 flex-wrap gap-y-1">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <React.Fragment key={index}>
              {index > 0 && <ChevronRight size={14} className="mx-1.5 text-gray-300 flex-shrink-0" />}
              {isLast || !item.to ? (
                <span className={isLast ? 'text-gray-900 font-bold truncate max-w-[200px]' : 'truncate max-w-[200px]'}>
                  {item.label}
                </span>
              ) : (
                <Link
                  to={item.to}
                  className="hover:text-ilma-primary transition-colors truncate max-w-[200px]"
                >
                  {item.label}
                </Link>
              )}
            </React.Fragment>
          );
        })}
      </nav>

      {/* Mobile: back arrow + parent name */}
      {parentItem && parentItem.to && (
        <nav aria-label="Retour" className="flex md:hidden">
          <Link
            to={parentItem.to}
            className="inline-flex items-center text-sm font-bold text-gray-500 hover:text-ilma-primary transition-colors"
          >
            <ArrowLeft size={16} className="mr-1" />
            {parentItem.label}
          </Link>
        </nav>
      )}
    </>
  );
};
