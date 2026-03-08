import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Toggle } from '../../components/ui/Toggle';
import { axe } from 'vitest-axe';
import { describe, it, expect, vi } from 'vitest';

describe('Toggle Component', () => {
  it('renders with label', () => {
    render(<Toggle label="Notifications" checked={false} onChange={vi.fn()} />);
    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('has role switch with correct aria-checked', () => {
    const { rerender } = render(<Toggle label="Test" checked={false} onChange={vi.fn()} />);
    const toggle = screen.getByRole('switch');
    expect(toggle).toHaveAttribute('aria-checked', 'false');

    rerender(<Toggle label="Test" checked={true} onChange={vi.fn()} />);
    expect(toggle).toHaveAttribute('aria-checked', 'true');
  });

  it('calls onChange when clicked', () => {
    const onChange = vi.fn();
    render(<Toggle label="Test" checked={false} onChange={onChange} />);

    fireEvent.click(screen.getByRole('switch'));
    expect(onChange).toHaveBeenCalledWith(true);
  });

  it('does not call onChange when disabled', () => {
    const onChange = vi.fn();
    render(<Toggle label="Test" checked={false} onChange={onChange} disabled />);

    fireEvent.click(screen.getByRole('switch'));
    expect(onChange).not.toHaveBeenCalled();
  });

  it('renders description text', () => {
    render(<Toggle label="Test" description="Some helper" checked={false} onChange={vi.fn()} />);
    expect(screen.getByText('Some helper')).toBeInTheDocument();
  });

  it('passes a11y audit', async () => {
    const { container } = render(
      <main>
        <Toggle label="A11y Toggle" checked={true} onChange={vi.fn()} />
      </main>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
