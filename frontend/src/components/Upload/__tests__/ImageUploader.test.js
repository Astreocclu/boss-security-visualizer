import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ImageUploader from '../ImageUploader';
import { createMockFile } from '../../../utils/testUtils';

// Mock URL.createObjectURL
const mockCreateObjectURL = jest.fn(() => 'mock-url');
const mockRevokeObjectURL = jest.fn();
global.URL.createObjectURL = mockCreateObjectURL;
global.URL.revokeObjectURL = mockRevokeObjectURL;

describe('ImageUploader Component', () => {
  const mockOnImageSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders upload area with default text', () => {
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    expect(screen.getByText(/drag and drop an image here/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /browse files/i })).toBeInTheDocument();
  });

  it('handles file selection via input', async () => {
    const user = userEvent.setup();
    const file = createMockFile('test.jpg', 1024, 'image/jpeg');
    
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    const input = screen.getByLabelText(/upload image/i);
    await user.upload(input, file);
    
    expect(mockOnImageSelect).toHaveBeenCalledWith(file);
    expect(mockCreateObjectURL).toHaveBeenCalledWith(file);
  });

  it('validates file type', async () => {
    const user = userEvent.setup();
    const invalidFile = createMockFile('test.txt', 1024, 'text/plain');
    
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    const input = screen.getByLabelText(/upload image/i);
    await user.upload(input, invalidFile);
    
    expect(screen.getByText(/please select a valid image file/i)).toBeInTheDocument();
    expect(mockOnImageSelect).toHaveBeenCalledWith(null);
  });

  it('validates file size', async () => {
    const user = userEvent.setup();
    const largeFile = createMockFile('large.jpg', 15 * 1024 * 1024, 'image/jpeg'); // 15MB
    
    render(<ImageUploader onImageSelect={mockOnImageSelect} maxSize={10 * 1024 * 1024} />);
    
    const input = screen.getByLabelText(/upload image/i);
    await user.upload(input, largeFile);
    
    expect(screen.getByText(/image size should be less than 10.0mb/i)).toBeInTheDocument();
    expect(mockOnImageSelect).toHaveBeenCalledWith(null);
  });

  it('shows file preview after successful upload', async () => {
    const user = userEvent.setup();
    const file = createMockFile('test.jpg', 1024, 'image/jpeg');
    
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    const input = screen.getByLabelText(/upload image/i);
    await user.upload(input, file);
    
    await waitFor(() => {
      expect(screen.getByAltText(/selected image preview/i)).toBeInTheDocument();
    });
    
    expect(screen.getByRole('button', { name: /remove/i })).toBeInTheDocument();
  });

  it('shows file information', async () => {
    const user = userEvent.setup();
    const file = createMockFile('test.jpg', 1024, 'image/jpeg');
    
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    const input = screen.getByLabelText(/upload image/i);
    await user.upload(input, file);
    
    expect(screen.getByText('test.jpg')).toBeInTheDocument();
    expect(screen.getByText('1.0 KB')).toBeInTheDocument();
    expect(screen.getByText('image/jpeg')).toBeInTheDocument();
  });

  it('handles file removal', async () => {
    const user = userEvent.setup();
    const file = createMockFile('test.jpg', 1024, 'image/jpeg');
    
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    const input = screen.getByLabelText(/upload image/i);
    await user.upload(input, file);
    
    const removeButton = await screen.findByRole('button', { name: /remove/i });
    await user.click(removeButton);
    
    expect(mockOnImageSelect).toHaveBeenLastCalledWith(null);
    expect(mockRevokeObjectURL).toHaveBeenCalled();
    expect(screen.queryByAltText(/selected image preview/i)).not.toBeInTheDocument();
  });

  it('handles drag and drop', async () => {
    const file = createMockFile('dropped.jpg', 2048, 'image/jpeg');
    
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    const dropZone = screen.getByRole('button', { name: /upload image/i });
    
    fireEvent.dragOver(dropZone);
    expect(dropZone).toHaveClass('upload-area-drag-over');
    
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file],
      },
    });
    
    expect(mockOnImageSelect).toHaveBeenCalledWith(file);
  });

  it('handles drag leave', () => {
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    const dropZone = screen.getByRole('button', { name: /upload image/i });
    
    fireEvent.dragOver(dropZone);
    expect(dropZone).toHaveClass('upload-area-drag-over');
    
    fireEvent.dragLeave(dropZone);
    expect(dropZone).not.toHaveClass('upload-area-drag-over');
  });

  it('is disabled when disabled prop is true', () => {
    render(<ImageUploader onImageSelect={mockOnImageSelect} disabled />);
    
    const input = screen.getByLabelText(/upload image/i);
    const browseButton = screen.getByRole('button', { name: /browse files/i });
    
    expect(input).toBeDisabled();
    expect(browseButton).toBeDisabled();
  });

  it('shows custom accepted types in constraints', () => {
    render(
      <ImageUploader 
        onImageSelect={mockOnImageSelect} 
        acceptedTypes={['image/png', 'image/gif']}
      />
    );
    
    expect(screen.getByText(/supported: png, gif/i)).toBeInTheDocument();
  });

  it('shows custom max size in constraints', () => {
    render(
      <ImageUploader 
        onImageSelect={mockOnImageSelect} 
        maxSize={5 * 1024 * 1024} // 5MB
      />
    );
    
    expect(screen.getByText(/max size: 5.0 mb/i)).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(
      <ImageUploader 
        onImageSelect={mockOnImageSelect} 
        className="custom-uploader"
      />
    );
    
    const uploader = screen.getByRole('button', { name: /upload image/i }).closest('.image-uploader');
    expect(uploader).toHaveClass('custom-uploader');
  });

  it('handles keyboard navigation', async () => {
    const user = userEvent.setup();
    
    render(<ImageUploader onImageSelect={mockOnImageSelect} />);
    
    const dropZone = screen.getByRole('button', { name: /upload image/i });
    
    dropZone.focus();
    expect(dropZone).toHaveFocus();
    
    // Simulate Enter key press
    await user.keyboard('{Enter}');
    // This would normally trigger file dialog, but we can't test that in jsdom
  });
});
