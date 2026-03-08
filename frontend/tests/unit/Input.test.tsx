import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '../../components/ui/Input';
import { axe } from 'vitest-axe';
import { describe, it, expect, vi } from 'vitest';

describe('Input Component', () => {
  it('renders with label and links it via htmlFor', () => {
    render(<Input label="Email" name="email" />);
    const input = screen.getByLabelText('Email');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('name', 'email');
  });

  it('shows error message with aria-invalid and aria-describedby', () => {
    render(<Input label="Mot de passe" name="password" error="Champ requis" />);
    const input = screen.getByLabelText('Mot de passe');
    expect(input).toHaveAttribute('aria-invalid', 'true');

    const errorEl = screen.getByText('Champ requis');
    expect(errorEl).toBeInTheDocument();
    expect(errorEl).toHaveAttribute('role', 'alert');

    // aria-describedby should link to error
    const describedBy = input.getAttribute('aria-describedby');
    expect(describedBy).toBeTruthy();
    expect(errorEl.id).toBe(describedBy);
  });

  it('does not have aria-invalid when no error', () => {
    render(<Input label="Nom" name="name" />);
    const input = screen.getByLabelText('Nom');
    expect(input).not.toHaveAttribute('aria-invalid');
  });

  it('handles onChange', () => {
    const handleChange = vi.fn();
    render(<Input label="Test" name="test" onChange={handleChange} />);
    fireEvent.change(screen.getByLabelText('Test'), { target: { value: 'hello' } });
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  it('renders disabled state', () => {
    render(<Input label="Disabled" name="disabled" disabled />);
    expect(screen.getByLabelText('Disabled')).toBeDisabled();
  });

  it('passes a11y audit', async () => {
    const { container } = render(
      <main>
        <Input label="Accessible Input" name="a11y" />
        <Input label="With Error" name="err" error="Error message" />
      </main>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
