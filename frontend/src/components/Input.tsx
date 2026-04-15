import React from 'react';
import './Input.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  className = '',
  ...props
}) => {
  return (
    <div className="input-wrapper">
      {label && <label className="input-label">{label}</label>}
      <input className={`input ${error ? 'input-error' : ''} ${className}`} {...props} />
      {error && <div className="input-error-text">{error}</div>}
      {helperText && !error && <div className="input-helper-text">{helperText}</div>}
    </div>
  );
};
