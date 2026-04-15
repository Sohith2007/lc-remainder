import React from 'react';
import './Footer.css';

export const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-brand">LeetReminder</div>
        <div className="footer-copyright">
          © 2026 LeetReminder Academic. Precision in every problem.
        </div>
      </div>
    </footer>
  );
};
