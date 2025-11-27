describe('Dashboard Flow', () => {
  beforeEach(() => {
    cy.login();
    cy.visit('/dashboard');
  });

  describe('Dashboard Layout', () => {
    it('should display main dashboard components', () => {
      cy.get('[data-testid="dashboard-header"]').should('be.visible');
      cy.get('[data-testid="stats-section"]').should('be.visible');
      cy.get('[data-testid="recent-requests"]').should('be.visible');
      cy.get('[data-testid="quick-actions"]').should('be.visible');
    });

    it('should show user welcome message', () => {
      cy.get('[data-testid="welcome-message"]').should('be.visible');
      cy.get('[data-testid="welcome-message"]').should('contain', 'Welcome, testuser');
    });

    it('should display navigation menu', () => {
      cy.get('[data-testid="navigation"]').should('be.visible');
      cy.get('[data-testid="nav-dashboard"]').should('have.class', 'active');
      cy.get('[data-testid="nav-upload"]').should('be.visible');
      cy.get('[data-testid="nav-requests"]').should('be.visible');
    });
  });

  describe('Statistics Section', () => {
    it('should display user statistics', () => {
      cy.intercept('GET', '**/api/visualizations/stats/', {
        statusCode: 200,
        body: {
          total_requests: 15,
          completed_requests: 12,
          pending_requests: 3,
          total_images_generated: 36
        }
      }).as('getStats');

      cy.wait('@getStats');
      
      cy.get('[data-testid="stat-total-requests"]').should('contain', '15');
      cy.get('[data-testid="stat-completed"]').should('contain', '12');
      cy.get('[data-testid="stat-pending"]').should('contain', '3');
      cy.get('[data-testid="stat-generated-images"]').should('contain', '36');
    });

    it('should handle stats loading state', () => {
      cy.intercept('GET', '**/api/visualizations/stats/', {
        delay: 2000,
        statusCode: 200,
        body: { total_requests: 0 }
      }).as('slowStats');

      cy.get('[data-testid="stats-loading"]').should('be.visible');
      cy.wait('@slowStats');
      cy.get('[data-testid="stats-loading"]').should('not.exist');
    });

    it('should handle stats error gracefully', () => {
      cy.intercept('GET', '**/api/visualizations/stats/', {
        statusCode: 500,
        body: { detail: 'Stats unavailable' }
      }).as('statsError');

      cy.wait('@statsError');
      cy.get('[data-testid="stats-error"]').should('be.visible');
      cy.get('[data-testid="stats-error"]').should('contain', 'Unable to load statistics');
    });
  });

  describe('Recent Requests Section', () => {
    it('should display recent visualization requests', () => {
      cy.wait('@getVisualizations');
      
      cy.get('[data-testid="recent-request"]').should('have.length.at.least', 1);
      cy.get('[data-testid="recent-request"]').first().within(() => {
        cy.get('[data-testid="request-image"]').should('be.visible');
        cy.get('[data-testid="request-status"]').should('be.visible');
        cy.get('[data-testid="request-date"]').should('be.visible');
        cy.get('[data-testid="request-type"]').should('be.visible');
      });
    });

    it('should show empty state when no requests exist', () => {
      cy.intercept('GET', '**/api/visualizations/', {
        statusCode: 200,
        body: { count: 0, results: [] }
      }).as('emptyRequests');

      cy.wait('@emptyRequests');
      cy.get('[data-testid="empty-requests"]').should('be.visible');
      cy.get('[data-testid="empty-requests"]').should('contain', 'No visualization requests yet');
    });

    it('should link to individual request details', () => {
      cy.wait('@getVisualizations');
      
      cy.get('[data-testid="recent-request"]').first().click();
      cy.url().should('include', '/requests/1');
    });

    it('should show request status badges', () => {
      cy.wait('@getVisualizations');
      
      cy.get('[data-testid="status-completed"]').should('be.visible');
      cy.get('[data-testid="status-pending"]').should('be.visible');
      cy.get('[data-testid="status-completed"]').should('have.class', 'status-success');
      cy.get('[data-testid="status-pending"]').should('have.class', 'status-warning');
    });
  });

  describe('Quick Actions', () => {
    it('should display quick action buttons', () => {
      cy.get('[data-testid="quick-upload"]').should('be.visible');
      cy.get('[data-testid="quick-view-all"]').should('be.visible');
      cy.get('[data-testid="quick-profile"]').should('be.visible');
    });

    it('should navigate to upload page', () => {
      cy.get('[data-testid="quick-upload"]').click();
      cy.url().should('include', '/upload');
    });

    it('should navigate to requests page', () => {
      cy.get('[data-testid="quick-view-all"]').click();
      cy.url().should('include', '/requests');
    });

    it('should navigate to profile page', () => {
      cy.get('[data-testid="quick-profile"]').click();
      cy.url().should('include', '/profile');
    });
  });

  describe('Responsive Design', () => {
    it('should adapt to mobile viewport', () => {
      cy.viewport(375, 667);
      
      cy.get('[data-testid="dashboard-header"]').should('be.visible');
      cy.get('[data-testid="stats-section"]').should('be.visible');
      
      // Stats should stack vertically on mobile
      cy.get('[data-testid="stats-grid"]').should('have.class', 'mobile-stack');
    });

    it('should adapt to tablet viewport', () => {
      cy.viewport(768, 1024);
      
      cy.get('[data-testid="dashboard-header"]').should('be.visible');
      cy.get('[data-testid="stats-section"]').should('be.visible');
      cy.get('[data-testid="recent-requests"]').should('be.visible');
    });
  });

  describe('Real-time Updates', () => {
    it('should update when new request is completed', () => {
      // Simulate WebSocket or polling update
      cy.intercept('GET', '**/api/visualizations/', {
        statusCode: 200,
        body: {
          count: 3,
          results: [
            {
              id: 3,
              status: 'completed',
              screen_type_name: 'Security',
              created_at: new Date().toISOString(),
              result_count: 2
            }
          ]
        }
      }).as('updatedRequests');

      // Trigger refresh (could be automatic polling)
      cy.get('[data-testid="refresh-button"]').click();
      cy.wait('@updatedRequests');
      
      cy.get('[data-testid="recent-request"]').should('contain', 'completed');
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', () => {
      cy.intercept('GET', '**/api/visualizations/', {
        statusCode: 500,
        body: { detail: 'Server error' }
      }).as('serverError');

      cy.visit('/dashboard');
      cy.wait('@serverError');
      
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="retry-button"]').should('be.visible');
    });

    it('should allow retry after error', () => {
      cy.intercept('GET', '**/api/visualizations/', {
        statusCode: 500,
        body: { detail: 'Server error' }
      }).as('initialError');

      cy.visit('/dashboard');
      cy.wait('@initialError');
      
      // Mock successful retry
      cy.intercept('GET', '**/api/visualizations/', { fixture: 'visualizations.json' }).as('retrySuccess');
      
      cy.get('[data-testid="retry-button"]').click();
      cy.wait('@retrySuccess');
      
      cy.get('[data-testid="recent-requests"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('not.exist');
    });
  });
});
