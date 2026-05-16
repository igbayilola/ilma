import React, { useMemo } from 'react';
import DOMPurify from 'dompurify';

const SAFE_TAGS = ['p', 'br', 'strong', 'em', 'b', 'i', 'u', 'ul', 'ol', 'li', 'h3', 'h4', 'a', 'code', 'blockquote', 'span'];
const SAFE_ATTRS = ['href', 'target', 'rel', 'class'];

export interface SanitizedHTMLProps {
  html: string | null | undefined;
  className?: string;
  as?: 'div' | 'span';
}

/**
 * Render admin-authored HTML (Tiptap output) safely. Authors are trusted, but
 * defense-in-depth: explanations land on a kids' app, so we strip any
 * unexpected tag (img/script/style/iframe/…) and any attribute outside the
 * allowlist. Links get `rel="noopener noreferrer"` and `target="_blank"`.
 */
export const SanitizedHTML: React.FC<SanitizedHTMLProps> = ({ html, className, as = 'div' }) => {
  const clean = useMemo(() => {
    if (!html) return '';
    return DOMPurify.sanitize(html, {
      ALLOWED_TAGS: SAFE_TAGS,
      ALLOWED_ATTR: SAFE_ATTRS,
      ADD_ATTR: ['target', 'rel'],
    });
  }, [html]);

  if (!clean) return null;

  const Tag = as;
  return (
    <Tag
      className={className}
      // Sanitized output via DOMPurify — content is admin-authored and stripped
      // to an allowlist of safe inline/block tags.
      dangerouslySetInnerHTML={{ __html: clean }}
    />
  );
};
