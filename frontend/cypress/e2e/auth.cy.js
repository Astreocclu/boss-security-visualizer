describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Login', () => {
    it('should display login form when not authenticated', () => {
      cy.url().should('include', '/login');
      cy.get('[data-testid="login-form"]').should('be.visible');
      cy.get('[data-testid="username-input"]').should('be.visible');
      cy.get('[data-testid="password-input"]').should('be.visible');
      cy.get('[data-testid="login-button"]').should('be.visible');
    });

    it('should successfully log in with valid credentials', () => {
      cy.login();
      cy.url().should('not.include', '/login');
      cy.get('[data-testid="user-menu"]').should('be.visible');
      cy.get('[data-testid="user-menu"]').should('contain', 'testuser');
    });

    it('should show error message with invalid credentials', () => {
      cy.intercept('POST', '**/api/auth/login/', {
        statusCode: 401,
        body: { detail: 'Invalid credentials' }
      }).as('loginError');

      cy.visit('/login');
      cy.get('[data-testid="username-input"]').type('wronguser');
      cy.get('[data-testid="password-input"]').type('wrongpass');
      cy.get('[data-testid="login-button"]').click();
      
      cy.wait('@loginError');
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'Invalid credentials');
    });

    it('should handle rate limiting', () => {
      cy.intercept('POST', '**/api/auth/login/', {
        statusCode: 429,
        body: { detail: 'Too many login attempts. Please try again later.' }
      }).as('rateLimited');

      cy.visit('/login');
      cy.get('[data-testid="username-input"]').type('testuser');
      cy.get('[data-testid="password-input"]').type('testpass');
      cy.get('[data-testid="login-button"]').click();
      
      cy.wait('@rateLimited');
      cy.get('[data-testid="error-message"]').should('contain', 'Too many login attempts');
    });

    it('should validate required fields', () => {
      cy.visit('/login');
      cy.get('[data-testid="login-button"]').click();
      
      cy.get('[data-testid="username-input"]').should('have.attr', 'aria-invalid', 'true');
      cy.get('[data-testid="password-input"]').should('have.attr', 'aria-invalid', 'true');
    });
  });

  describe('Registration', () => {
    it('should display registration form', () => {
      cy.visit('/register');
      cy.get('[data-testid="register-form"]').should('be.visible');
      cy.get('[data-testid="username-input"]').should('be.visible');
      cy.get('[data-testid="email-input"]').should('be.visible');
      cy.get('[data-testid="password-input"]').should('be.visible');
      cy.get('[data-testid="register-button"]').should('be.visible');
    });

    it('should successfully register a new user', () => {
      cy.register();
      cy.url().should('not.include', '/register');
      cy.get('[data-testid="user-menu"]').should('be.visible');
    });

    it('should validate email format', () => {
      cy.visit('/register');
      cy.get('[data-testid="email-input"]').type('invalid-email');
      cy.get('[data-testid="register-button"]').click();
      
      cy.get('[data-testid="email-input"]').should('have.attr', 'aria-invalid', 'true');
    });

    it('should validate password strength', () => {
      cy.visit('/register');
      cy.get('[data-testid="password-input"]').type('123');
      cy.get('[data-testid="register-button"]').click();
      
      cy.get('[data-testid="password-error"]').should('contain', 'at least 6 characters');
    });

    it('should handle duplicate username error', () => {
      cy.intercept('POST', '**/api/auth/register/', {
        statusCode: 400,
        body: { username: ['Username already exists'] }
      }).as('duplicateUser');

      cy.register({ username: 'existinguser' });
      cy.wait('@duplicateUser');
      cy.get('[data-testid="error-message"]').should('contain', 'Username already exists');
    });
  });

  describe('Logout', () => {
    it('should successfully log out', () => {
      cy.login();
      cy.logout();
      cy.url().should('include', '/login');
      cy.get('[data-testid="login-form"]').should('be.visible');
    });
  });

  describe('Token Refresh', () => {
    it('should handle token expiration gracefully', () => {
      cy.login();
      
      // Simulate expired token
      cy.intercept('GET', '**/api/visualizations/', {
        statusCode: 401,
        body: { detail: 'Token has expired' }
      }).as('expiredToken');
      
      // Simulate successful token refresh
      cy.intercept('POST', '**/api/auth/refresh/', {
        statusCode: 200,
        body: {
          access: 'new-access-token',
          refresh: 'new-refresh-token'
        }
      }).as('tokenRefresh');

      cy.visit('/dashboard');
      cy.wait('@expiredToken');
      cy.wait('@tokenRefresh');
      
      // Should stay on dashboard after token refresh
      cy.url().should('include', '/dashboard');
    });
  });
});
