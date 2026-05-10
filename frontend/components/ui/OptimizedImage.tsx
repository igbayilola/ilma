import React, { useState } from 'react';

interface OptimizedImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  /** Fallback displayed on error or while loading (default: gray placeholder) */
  fallback?: React.ReactNode;
  /** Override loading strategy (default: "lazy") */
  loading?: 'lazy' | 'eager';
}

/**
 * Drop-in `<img>` replacement with:
 * - `loading="lazy"` by default (native browser lazy loading)
 * - `decoding="async"` (non-blocking decode)
 * - Error fallback (gray placeholder instead of broken icon)
 * - `width`/`height` pass-through to prevent CLS
 */
export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  fallback,
  loading = 'lazy',
  onError,
  className = '',
  alt = '',
  src,
  ...rest
}) => {
  const [hasError, setHasError] = useState(false);

  if (hasError || !src) {
    if (fallback) return <>{fallback}</>;
    return (
      <div
        className={`bg-gray-200 flex items-center justify-center text-gray-400 ${className}`}
        role="img"
        aria-label={alt}
        style={rest.style}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      loading={loading}
      decoding="async"
      className={className}
      onError={(e) => {
        setHasError(true);
        onError?.(e);
      }}
      {...rest}
    />
  );
};
