import React from 'react';
import { ButtonVariant } from '../../types';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = ButtonVariant.PRIMARY,
  size = 'md',
  fullWidth = false,
  leftIcon,
  isLoading,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = "inline-flex items-center justify-center font-semibold rounded-2xl transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-opacity-50 touch-manipulation select-none active:scale-[0.97]";

  const sizeStyles = {
    sm: "min-h-[36px] px-4 text-sm", // Compact but clickable
    md: "min-h-[48px] px-6 text-base", // AA Standard for touch targets
    lg: "min-h-[56px] px-8 text-lg" // Generous touch target
  };

  const variants = {
    [ButtonVariant.PRIMARY]: "gradient-hero text-white shadow-clay hover:shadow-clay-hover active:shadow-clay-pressed focus:ring-sitou-primary",
    [ButtonVariant.SECONDARY]: "bg-sitou-primary-light text-sitou-primary-dark hover:bg-amber-200/60 focus:ring-sitou-primary-light shadow-clay-sm",
    [ButtonVariant.GHOST]: "bg-transparent text-sitou-text hover:bg-gray-100 focus:ring-gray-200",
    [ButtonVariant.DANGER]: "gradient-danger text-white hover:shadow-glow-orange focus:ring-sitou-red shadow-clay-sm",
    [ButtonVariant.SUCCESS]: "gradient-success text-white shadow-clay-sm hover:shadow-glow-green focus:ring-sitou-green"
  };

  const widthStyle = fullWidth ? "w-full" : "";
  const disabledStyle = (disabled || isLoading) ? "opacity-50 cursor-not-allowed pointer-events-none" : "";

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variants[variant]} ${widthStyle} ${disabledStyle} ${className}`}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="animate-spin mr-2" role="status" aria-label="Chargement">
           <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
           </svg>
        </span>
      ) : leftIcon ? (
        <span className="mr-2" aria-hidden="true">{leftIcon}</span>
      ) : null}
      {children}
    </button>
  );
};
