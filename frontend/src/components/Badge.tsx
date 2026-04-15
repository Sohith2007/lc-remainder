import React from 'react';
import './Badge.css';

interface BadgeProps {
  label: string;
  variant?: 'primary' | 'difficulty' | 'tag';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ label, variant = 'primary', className = '' }) => {
  return <span className={`badge badge-${variant} ${className}`}>{label}</span>;
};
