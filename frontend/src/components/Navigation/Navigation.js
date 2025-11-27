import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Button } from '../Common';
import useAuthStore from '../../store/authStore';
import './Navigation.css';

const Navigation = ({ 
  title = 'Homescreen Visualizer',
  showUserMenu = true,
  className = '' 
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, logout, isAuthenticated } = useAuthStore();

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleLogout = () => {
    logout();
    setIsMobileMenuOpen(false);
  };

  const navClasses = [
    'navigation',
    className
  ].filter(Boolean).join(' ');

  const mobileMenuClasses = [
    'navigation-mobile-menu',
    isMobileMenuOpen && 'navigation-mobile-menu-open'
  ].filter(Boolean).join(' ');

  return (
    <nav className={navClasses}>
      <div className="navigation-container">
        {/* Logo/Title */}
        <div className="navigation-brand">
          <h1 className="navigation-title">{title}</h1>
        </div>

        {/* Desktop Navigation */}
        {isAuthenticated && (
          <div className="navigation-desktop">
            <div className="navigation-links">
              <a href="/dashboard" className="navigation-link">
                Dashboard
              </a>
              <a href="/requests" className="navigation-link">
                My Requests
              </a>
              <a href="/upload" className="navigation-link">
                Upload
              </a>
            </div>

            {showUserMenu && user && (
              <div className="navigation-user">
                <span className="navigation-username">
                  Welcome, {user.username}
                </span>
                <Button
                  variant="outline"
                  size="small"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Mobile Menu Button */}
        {isAuthenticated && (
          <button
            className="navigation-mobile-toggle"
            onClick={toggleMobileMenu}
            aria-label="Toggle mobile menu"
            aria-expanded={isMobileMenuOpen}
          >
            <span className="navigation-hamburger">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </button>
        )}
      </div>

      {/* Mobile Menu */}
      {isAuthenticated && (
        <div className={mobileMenuClasses}>
          <div className="navigation-mobile-links">
            <a 
              href="/dashboard" 
              className="navigation-mobile-link"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Dashboard
            </a>
            <a 
              href="/requests" 
              className="navigation-mobile-link"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              My Requests
            </a>
            <a 
              href="/upload" 
              className="navigation-mobile-link"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Upload
            </a>
          </div>

          {showUserMenu && user && (
            <div className="navigation-mobile-user">
              <div className="navigation-mobile-username">
                Welcome, {user.username}
              </div>
              <Button
                variant="outline"
                size="medium"
                fullWidth
                onClick={handleLogout}
              >
                Logout
              </Button>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

Navigation.propTypes = {
  title: PropTypes.string,
  showUserMenu: PropTypes.bool,
  className: PropTypes.string
};

export default React.memo(Navigation);
