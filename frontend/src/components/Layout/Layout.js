import React from 'react';
import PropTypes from 'prop-types';
import './Layout.css';

const Layout = ({ 
  children, 
  sidebar = null, 
  header = null, 
  footer = null,
  className = '',
  fluid = false 
}) => {
  const layoutClasses = [
    'layout',
    fluid && 'layout-fluid',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={layoutClasses}>
      {header && (
        <header className="layout-header">
          {header}
        </header>
      )}
      
      <div className="layout-body">
        {sidebar && (
          <aside className="layout-sidebar">
            {sidebar}
          </aside>
        )}
        
        <main className="layout-main">
          {children}
        </main>
      </div>
      
      {footer && (
        <footer className="layout-footer">
          {footer}
        </footer>
      )}
    </div>
  );
};

Layout.propTypes = {
  children: PropTypes.node.isRequired,
  sidebar: PropTypes.node,
  header: PropTypes.node,
  footer: PropTypes.node,
  className: PropTypes.string,
  fluid: PropTypes.bool
};

export default React.memo(Layout);
