
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../../components/ui/Button';
import { ButtonVariant } from '../../types';
import { axe } from 'vitest-axe';
import { describe, it, expect, vi } from 'vitest';

describe('Button Component', () => {
  it('renders correctly with default props', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('gradient-hero'); // Default variant
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Action</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state and disables interaction', () => {
    render(<Button isLoading>Loading</Button>);
    const button = screen.getByRole('button');
    
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByText('Loading')).toBeInTheDocument();
  });

  it('renders variants correctly', () => {
    const { rerender } = render(<Button variant={ButtonVariant.DANGER}>Delete</Button>);
    expect(screen.getByRole('button')).toHaveClass('gradient-danger');

    rerender(<Button variant={ButtonVariant.GHOST}>Cancel</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-transparent');
  });

  it('passes accessibility audit (a11y)', async () => {
    const { container } = render(
      <main>
        <Button>Accessible Button</Button>
        <Button variant={ButtonVariant.SECONDARY}>Secondary</Button>
      </main>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
