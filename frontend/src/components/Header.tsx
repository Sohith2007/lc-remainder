import React from 'react';
import './Header.css';

interface HeaderProps {
  onTodaysProblemClick: () => void;
  onSubscribeClick?: () => void;
  onLogoClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onTodaysProblemClick, onSubscribeClick, onLogoClick }) => {
  return (
    <header className="header">
      <div className="header-container">
        <button className="logo" onClick={onLogoClick} type="button">
          LeetReminder
        </button>
        <nav className="nav-links">
          <button className="nav-button" onClick={onTodaysProblemClick}>
            Today's Problem
          </button>
        </nav>
        <button className="subscribe-btn" onClick={onSubscribeClick}>
          Subscribe
        </button>
      </div>
    </header>
  );
};
