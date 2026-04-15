import React, { useEffect } from 'react';
import './Toast.css';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

interface ToastMessage {
  id: string;
  message: string;
  variant: ToastVariant;
}

interface ToastContainerProps {
  messages: ToastMessage[];
  onRemove: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ messages, onRemove }) => {
  return (
    <div className="toast-container">
      {messages.map((toast) => (
        <Toast key={toast.id} {...toast} onRemove={() => onRemove(toast.id)} />
      ))}
    </div>
  );
};

interface ToastProps extends ToastMessage {
  onRemove: () => void;
}

const Toast: React.FC<ToastProps> = ({ message, variant, onRemove }) => {
  useEffect(() => {
    const timer = setTimeout(onRemove, 4000); // Auto-dismiss after 4 seconds
    return () => clearTimeout(timer);
  }, [onRemove]);

  return (
    <div className={`toast toast-${variant}`}>
      <div className="toast-content">
        <span className="toast-icon">{getToastIcon(variant)}</span>
        <span className="toast-message">{message}</span>
      </div>
      <button className="toast-close" onClick={onRemove} aria-label="Close">
        ✕
      </button>
    </div>
  );
};

function getToastIcon(variant: ToastVariant): string {
  switch (variant) {
    case 'success':
      return '✓';
    case 'error':
      return '✕';
    case 'warning':
      return '⚠';
    case 'info':
      return 'ℹ';
    default:
      return '';
  }
}
