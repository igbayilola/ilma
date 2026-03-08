import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  leftIcon,
  rightIcon,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || props.name || Math.random().toString(36).substr(2, 9);
  const errorId = error ? `${inputId}-error` : undefined;

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label htmlFor={inputId} className="block text-sm font-bold text-gray-700 mb-1.5">
          {label}
        </label>
      )}
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" aria-hidden="true">
            {leftIcon}
          </div>
        )}
        <input
          id={inputId}
          aria-invalid={error ? true : undefined}
          aria-describedby={errorId}
          className={`
            w-full bg-white border
            ${error ? 'border-red-500 focus:ring-red-200' : 'border-gray-200 focus:ring-ilma-primary-light focus:border-ilma-primary'}
            rounded-xl py-3 px-4 text-gray-800 placeholder-gray-400 font-medium
            transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-opacity-50
            disabled:bg-gray-50 disabled:text-gray-400
            ${leftIcon ? 'pl-10' : ''}
            ${rightIcon ? 'pr-10' : ''}
          `}
          {...props}
        />
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" aria-hidden="true">
            {rightIcon}
          </div>
        )}
      </div>
      {error && (
        <p id={errorId} className="mt-1 text-xs text-red-500 font-medium animate-slide-down" role="alert">
          {error}
        </p>
      )}
    </div>
  );
};