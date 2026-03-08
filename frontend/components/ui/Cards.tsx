import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  interactive?: boolean;
  accent?: 'amber' | 'blue' | 'purple' | 'green' | 'orange' | 'pink' | 'teal';
}

export const Card: React.FC<CardProps> = ({ children, className = '', onClick, interactive = false, accent }) => {
  const accentClass = accent ? `card-accent-${accent}` : '';

  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-gray-800 rounded-3xl p-6 border border-ilma-border dark:border-gray-700 shadow-clay ${accentClass} ${interactive ? 'cursor-pointer hover:shadow-clay-hover transition-all duration-300 transform hover:-translate-y-1' : ''} ${className}`}
    >
      {children}
    </div>
  );
};

interface BadgeProps {
  label: string;
  color?: 'amber' | 'blue' | 'green' | 'red' | 'orange' | 'gray' | 'purple' | 'teal' | 'pink' | 'gold';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ label, color = 'amber', size = 'md', className = '' }) => {
  const colorStyles: Record<string, string> = {
    amber: 'bg-ilma-primary-light text-ilma-primary-dark',
    blue: 'bg-blue-100 text-blue-700',
    green: 'bg-green-100 text-ilma-green',
    red: 'bg-red-100 text-ilma-red',
    orange: 'bg-orange-100 text-ilma-orange',
    gray: 'bg-gray-100 text-gray-600',
    purple: 'bg-ilma-purple-light text-ilma-purple',
    teal: 'bg-ilma-teal-light text-ilma-teal',
    pink: 'bg-ilma-pink-light text-ilma-pink',
    gold: 'bg-ilma-gold-light text-ilma-gold',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1'
  };

  return (
    <span className={`inline-flex items-center font-bold rounded-full ${colorStyles[color] || colorStyles.blue} ${sizeStyles[size]} ${className}`}>
      {label}
    </span>
  );
};
