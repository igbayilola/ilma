import React from 'react';
import { OptimizedImage } from '../ui/OptimizedImage';
import { MediaReference } from '../../types';

interface MediaGalleryProps {
  media: MediaReference[];
}

/**
 * Renders media references attached to a question:
 * images, SVGs, diagrams, etc.
 * Excludes interactive media (handled by their own renderers)
 * and audio (handled by AudioRenderer).
 */
export const MediaGallery: React.FC<MediaGalleryProps> = ({ media }) => {
  const displayable = media.filter(m =>
    ['image', 'svg', 'diagram'].includes(m.type) && !m.interactive
  );

  if (displayable.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-3 justify-center mb-4">
      {displayable.map((m) => (
        <figure key={m.id} className="text-center">
          <OptimizedImage
            src={m.url}
            alt={m.alt_text}
            loading="eager"
            width={m.dimensions?.width}
            height={m.dimensions?.height}
            className="rounded-xl max-h-60 object-contain shadow-sm border border-gray-100"
          />
          {m.alt_text && (
            <figcaption className="text-xs text-gray-400 mt-1 max-w-xs">{m.alt_text}</figcaption>
          )}
        </figure>
      ))}
    </div>
  );
};
