// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Custom command to login
Cypress.Commands.add('login', (username = 'testuser', password = 'testpass123') => {
  cy.visit('/login');
  cy.get('[data-testid="username-input"]').type(username);
  cy.get('[data-testid="password-input"]').type(password);
  cy.get('[data-testid="login-button"]').click();
  cy.wait('@login');
  cy.url().should('not.include', '/login');
});

// Custom command to register a new user
Cypress.Commands.add('register', (userData = {}) => {
  const defaultData = {
    username: 'newuser',
    email: 'newuser@example.com',
    password: 'newpass123',
    firstName: 'New',
    lastName: 'User'
  };
  
  const user = { ...defaultData, ...userData };
  
  cy.visit('/register');
  cy.get('[data-testid="username-input"]').type(user.username);
  cy.get('[data-testid="email-input"]').type(user.email);
  cy.get('[data-testid="password-input"]').type(user.password);
  cy.get('[data-testid="first-name-input"]').type(user.firstName);
  cy.get('[data-testid="last-name-input"]').type(user.lastName);
  cy.get('[data-testid="register-button"]').click();
  cy.wait('@register');
});

// Custom command to upload an image
Cypress.Commands.add('uploadImage', (fileName = 'test-image.jpg') => {
  cy.fixture(fileName, 'base64').then(fileContent => {
    cy.get('[data-testid="image-upload-input"]').selectFile({
      contents: Cypress.Buffer.from(fileContent, 'base64'),
      fileName: fileName,
      mimeType: 'image/jpeg'
    }, { force: true });
  });
});

// Custom command to wait for loading to complete
Cypress.Commands.add('waitForLoading', () => {
  cy.get('[data-testid="loading-spinner"]', { timeout: 10000 }).should('not.exist');
});

// Custom command to check accessibility
Cypress.Commands.add('checkA11y', (context = null, options = {}) => {
  cy.injectAxe();
  cy.checkA11y(context, {
    includedImpacts: ['critical', 'serious'],
    ...options
  });
});

// Custom command to mock API responses
Cypress.Commands.add('mockApiResponse', (method, url, response, statusCode = 200) => {
  cy.intercept(method, url, {
    statusCode,
    body: response
  });
});

// Custom command to simulate network errors
Cypress.Commands.add('simulateNetworkError', (url) => {
  cy.intercept('*', url, { forceNetworkError: true });
});

// Custom command to check responsive design
Cypress.Commands.add('checkResponsive', (breakpoints = ['mobile', 'tablet', 'desktop']) => {
  const viewports = {
    mobile: [375, 667],
    tablet: [768, 1024],
    desktop: [1280, 720]
  };
  
  breakpoints.forEach(breakpoint => {
    const [width, height] = viewports[breakpoint];
    cy.viewport(width, height);
    cy.wait(500); // Allow time for responsive changes
    cy.screenshot(`responsive-${breakpoint}`);
  });
});

// Custom command to test form validation
Cypress.Commands.add('testFormValidation', (formSelector, validationTests) => {
  validationTests.forEach(test => {
    cy.get(formSelector).within(() => {
      if (test.input) {
        cy.get(test.field).clear().type(test.input);
      }
      if (test.submit) {
        cy.get('[type="submit"]').click();
      }
      if (test.expectedError) {
        cy.contains(test.expectedError).should('be.visible');
      }
    });
  });
});

// Custom command to logout
Cypress.Commands.add('logout', () => {
  cy.get('[data-testid="user-menu"]').click();
  cy.get('[data-testid="logout-button"]').click();
  cy.url().should('include', '/login');
});
