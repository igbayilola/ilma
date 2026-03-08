import React from 'react';

interface ToggleProps {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

export const Toggle: React.FC<ToggleProps> = ({ label, description, checked, onChange, disabled }) => {
  return (
    <div className={`flex items-center justify-between py-3 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}>
      <div className="flex flex-col mr-4">
        <span className="font-bold text-gray-800" id={`toggle-label-${label.replace(/\s+/g, '-')}`}>{label}</span>
        {description && <span className="text-xs text-gray-500 mt-0.5">{description}</span>}
      </div>

      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-labelledby={`toggle-label-${label.replace(/\s+/g, '-')}`}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={`
          relative inline-flex h-7 w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent 
          transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-ilma-primary focus:ring-offset-2
          ${checked ? 'bg-ilma-primary' : 'bg-gray-200'}
        `}
      >
        <span
          className={`
            pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 
            transition duration-200 ease-in-out
            ${checked ? 'translate-x-5' : 'translate-x-0'}
          `}
        />
      </button>
    </div>
  );
};