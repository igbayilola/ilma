import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SanitizedHTML } from '../../components/ui/SanitizedHTML';

describe('SanitizedHTML', () => {
  it('renders allowed inline formatting', () => {
    const { container } = render(<SanitizedHTML html="<p><strong>Bold</strong> and <em>italic</em></p>" />);
    expect(container.querySelector('strong')?.textContent).toBe('Bold');
    expect(container.querySelector('em')?.textContent).toBe('italic');
  });

  it('renders lists and headings authored by Tiptap', () => {
    const html = '<h3>Astuce</h3><ul><li>un</li><li>deux</li></ul>';
    const { container } = render(<SanitizedHTML html={html} />);
    expect(container.querySelector('h3')?.textContent).toBe('Astuce');
    expect(container.querySelectorAll('li')).toHaveLength(2);
  });

  it('strips <script> tags', () => {
    const html = '<p>Hello</p><script>window.x=1</script>';
    const { container } = render(<SanitizedHTML html={html} />);
    expect(container.querySelector('script')).toBeNull();
    expect(container.textContent).toContain('Hello');
  });

  it('strips <img> and on* handlers', () => {
    const html = '<p onclick="alert(1)">Click</p><img src="x" onerror="alert(2)" />';
    const { container } = render(<SanitizedHTML html={html} />);
    expect(container.querySelector('img')).toBeNull();
    const p = container.querySelector('p');
    expect(p?.getAttribute('onclick')).toBeNull();
    expect(p?.textContent).toBe('Click');
  });

  it('keeps links but does not allow javascript: URLs', () => {
    const html = '<p>Voir <a href="https://example.org">ici</a> et <a href="javascript:alert(1)">là</a></p>';
    const { container } = render(<SanitizedHTML html={html} />);
    const links = container.querySelectorAll('a');
    expect(links).toHaveLength(2);
    expect(links[0].getAttribute('href')).toBe('https://example.org');
    // DOMPurify either drops the href entirely (null) or replaces it; either way
    // no surviving javascript: URL is acceptable
    const jsHref = links[1].getAttribute('href');
    if (jsHref !== null) {
      expect(jsHref).not.toMatch(/^javascript:/i);
    }
  });

  it('renders nothing for empty / null html', () => {
    const { container: c1 } = render(<SanitizedHTML html="" />);
    expect(c1.firstChild).toBeNull();
    const { container: c2 } = render(<SanitizedHTML html={null} />);
    expect(c2.firstChild).toBeNull();
  });

  it('plain text (no tags) renders as-is wrapped in the container', () => {
    const { container } = render(<SanitizedHTML html="Juste du texte." className="leading-snug" />);
    expect(container.firstChild?.textContent).toBe('Juste du texte.');
    expect((container.firstChild as HTMLElement).className).toContain('leading-snug');
  });
});
