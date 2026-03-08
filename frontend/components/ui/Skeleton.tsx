import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'rect' | 'circle' | 'text';
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', variant = 'rect' }) => {
  const base = "animate-pulse bg-gray-200";
  const variants = {
    rect: "rounded-2xl",
    circle: "rounded-full",
    text: "rounded-md h-4"
  };

  return <div className={`${base} ${variants[variant]} ${className}`} />;
};