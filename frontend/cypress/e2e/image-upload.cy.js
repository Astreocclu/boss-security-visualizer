describe('Image Upload Flow', () => {
  beforeEach(() => {
    cy.login();
    cy.visit('/upload');
  });

  describe('Upload Interface', () => {
    it('should display upload form', () => {
      cy.get('[data-testid="image-uploader"]').should('be.visible');
      cy.get('[data-testid="screen-type-select"]').should('be.visible');
      cy.get('[data-testid="upload-button"]').should('be.visible');
    });

    it('should show drag and drop area', () => {
      cy.get('[data-testid="upload-area"]').should('be.visible');
      cy.get('[data-testid="upload-area"]').should('contain', 'Drag and drop');
      cy.get('[data-testid="browse-button"]').should('be.visible');
    });

    it('should display upload constraints', () => {
      cy.get('[data-testid="upload-constraints"]').should('be.visible');
      cy.get('[data-testid="upload-constraints"]').should('contain', 'Max size');
      cy.get('[data-testid="upload-constraints"]').should('contain', 'Supported');
    });
  });

  describe('File Selection', () => {
    it('should accept valid image files', () => {
      cy.uploadImage('test-image.jpg');
      cy.get('[data-testid="image-preview"]').should('be.visible');
      cy.get('[data-testid="file-info"]').should('contain', 'test-image.jpg');
      cy.get('[data-testid="remove-button"]').should('be.visible');
    });

    it('should reject invalid file types', () => {
      cy.fixture('test-document.pdf', 'base64').then(fileContent => {
        cy.get('[data-testid="image-upload-input"]').selectFile({
          contents: Cypress.Buffer.from(fileContent, 'base64'),
          fileName: 'document.pdf',
          mimeType: 'application/pdf'
        }, { force: true });
      });

      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'valid image file');
    });

    it('should reject files that are too large', () => {
      // Create a large file (simulate 15MB)
      const largeFileContent = 'x'.repeat(15 * 1024 * 1024);
      
      cy.get('[data-testid="image-upload-input"]').selectFile({
        contents: largeFileContent,
        fileName: 'large-image.jpg',
        mimeType: 'image/jpeg'
      }, { force: true });

      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'size should be less than');
    });

    it('should allow file removal', () => {
      cy.uploadImage();
      cy.get('[data-testid="image-preview"]').should('be.visible');
      
      cy.get('[data-testid="remove-button"]').click();
      cy.get('[data-testid="image-preview"]').should('not.exist');
      cy.get('[data-testid="upload-area"]').should('be.visible');
    });
  });

  describe('Screen Type Selection', () => {
    it('should load available screen types', () => {
      cy.wait('@getScreenTypes');
      cy.get('[data-testid="screen-type-select"]').click();
      cy.get('[data-testid="screen-type-option"]').should('have.length.at.least', 1);
      cy.get('[data-testid="screen-type-option"]').first().should('contain', 'Security');
    });

    it('should require screen type selection', () => {
      cy.uploadImage();
      cy.get('[data-testid="upload-button"]').click();
      
      cy.get('[data-testid="screen-type-error"]').should('be.visible');
      cy.get('[data-testid="screen-type-error"]').should('contain', 'Please select a screen type');
    });
  });

  describe('Upload Process', () => {
    it('should successfully upload image and create visualization request', () => {
      cy.intercept('POST', '**/api/visualizations/', {
        statusCode: 201,
        body: {
          id: 1,
          status: 'pending',
          original_image_url: 'http://example.com/uploaded-image.jpg',
          screen_type_name: 'Security',
          created_at: new Date().toISOString()
        }
      }).as('createVisualization');

      cy.uploadImage();
      cy.get('[data-testid="screen-type-select"]').click();
      cy.get('[data-testid="screen-type-option"]').first().click();
      cy.get('[data-testid="upload-button"]').click();

      cy.wait('@createVisualization');
      cy.get('[data-testid="success-message"]').should('be.visible');
      cy.get('[data-testid="success-message"]').should('contain', 'uploaded successfully');
      
      // Should redirect to requests page
      cy.url().should('include', '/requests');
    });

    it('should show loading state during upload', () => {
      cy.intercept('POST', '**/api/visualizations/', {
        delay: 2000,
        statusCode: 201,
        body: { id: 1, status: 'pending' }
      }).as('slowUpload');

      cy.uploadImage();
      cy.get('[data-testid="screen-type-select"]').click();
      cy.get('[data-testid="screen-type-option"]').first().click();
      cy.get('[data-testid="upload-button"]').click();

      cy.get('[data-testid="loading-spinner"]').should('be.visible');
      cy.get('[data-testid="upload-button"]').should('be.disabled');
      
      cy.wait('@slowUpload');
      cy.get('[data-testid="loading-spinner"]').should('not.exist');
    });

    it('should handle upload errors gracefully', () => {
      cy.intercept('POST', '**/api/visualizations/', {
        statusCode: 500,
        body: { detail: 'Upload failed' }
      }).as('uploadError');

      cy.uploadImage();
      cy.get('[data-testid="screen-type-select"]').click();
      cy.get('[data-testid="screen-type-option"]').first().click();
      cy.get('[data-testid="upload-button"]').click();

      cy.wait('@uploadError');
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'Upload failed');
    });

    it('should handle network errors', () => {
      cy.simulateNetworkError('**/api/visualizations/');

      cy.uploadImage();
      cy.get('[data-testid="screen-type-select"]').click();
      cy.get('[data-testid="screen-type-option"]').first().click();
      cy.get('[data-testid="upload-button"]').click();

      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="error-message"]').should('contain', 'network error');
    });
  });

  describe('Drag and Drop', () => {
    it('should handle drag and drop upload', () => {
      cy.fixture('test-image.jpg', 'base64').then(fileContent => {
        const file = {
          contents: Cypress.Buffer.from(fileContent, 'base64'),
          fileName: 'dropped-image.jpg',
          mimeType: 'image/jpeg'
        };

        cy.get('[data-testid="upload-area"]').selectFile(file, {
          action: 'drag-drop'
        });
      });

      cy.get('[data-testid="image-preview"]').should('be.visible');
      cy.get('[data-testid="file-info"]').should('contain', 'dropped-image.jpg');
    });

    it('should show visual feedback during drag over', () => {
      cy.get('[data-testid="upload-area"]').trigger('dragover');
      cy.get('[data-testid="upload-area"]').should('have.class', 'upload-area-drag-over');
      
      cy.get('[data-testid="upload-area"]').trigger('dragleave');
      cy.get('[data-testid="upload-area"]').should('not.have.class', 'upload-area-drag-over');
    });
  });

  describe('Accessibility', () => {
    it('should be keyboard accessible', () => {
      cy.get('[data-testid="upload-area"]').focus();
      cy.get('[data-testid="upload-area"]').should('have.focus');
      
      cy.get('[data-testid="upload-area"]').type('{enter}');
      // File dialog would open (can't test in Cypress)
    });

    it('should have proper ARIA labels', () => {
      cy.get('[data-testid="image-upload-input"]').should('have.attr', 'aria-label');
      cy.get('[data-testid="screen-type-select"]').should('have.attr', 'aria-label');
      cy.get('[data-testid="upload-button"]').should('have.attr', 'aria-label');
    });
  });
});
