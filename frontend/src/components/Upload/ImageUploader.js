import React, { useState, useRef, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { ErrorMessage, Button } from '../Common';
import './ImageUploader.css';

const ImageUploader = ({
  onImageSelect,
  maxSize = 10 * 1024 * 1024, // 10MB default
  acceptedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
  disabled = false,
  className = ''
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [error, setError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  // Clean up the preview URL when component unmounts or when a new file is selected
  useEffect(() => {
    if (selectedFile) {
      const objectUrl = URL.createObjectURL(selectedFile);
      setPreviewUrl(objectUrl);

      // Free memory when this component is unmounted
      return () => URL.revokeObjectURL(objectUrl);
    } else {
      setPreviewUrl(null);
    }
  }, [selectedFile]);

  const validateFile = useCallback((file) => {
    // Validate file type
    if (!acceptedTypes.includes(file.type)) {
      return `Please select a valid image file. Accepted types: ${acceptedTypes.join(', ')}`;
    }

    // Validate file size
    if (file.size > maxSize) {
      const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(1);
      return `Image size should be less than ${maxSizeMB}MB`;
    }

    return null;
  }, [acceptedTypes, maxSize]);

  const handleFileChange = useCallback((file) => {
    if (!file) {
      setSelectedFile(null);
      setError(null);
      onImageSelect(null);
      return;
    }

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      setSelectedFile(null);
      onImageSelect(null);
      return;
    }

    setSelectedFile(file);
    setError(null);
    onImageSelect(file);
  }, [validateFile, onImageSelect]);

  const handleInputChange = (e) => {
    const file = e.target.files[0];
    handleFileChange(file);
  };

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFileChange(file);
    }
  }, [disabled, handleFileChange]);

  const handleBrowseClick = useCallback(() => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, [disabled]);

  const handleRemoveImage = useCallback(() => {
    setSelectedFile(null);
    setError(null);
    onImageSelect(null);

    // Reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [onImageSelect]);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const uploaderClasses = [
    'image-uploader',
    disabled && 'image-uploader-disabled',
    className
  ].filter(Boolean).join(' ');

  const uploadAreaClasses = [
    'upload-area',
    previewUrl && 'upload-area-has-image',
    isDragOver && 'upload-area-drag-over',
    disabled && 'upload-area-disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={uploaderClasses}>
      <div
        className={uploadAreaClasses}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-label="Upload image"
        onClick={!previewUrl ? handleBrowseClick : undefined}
        onKeyDown={(e) => {
          if ((e.key === 'Enter' || e.key === ' ') && !previewUrl && !disabled) {
            e.preventDefault();
            handleBrowseClick();
          }
        }}
      >
        {previewUrl ? (
          <div className="image-preview-container">
            <img
              src={previewUrl}
              alt="Selected image preview"
              className="image-preview"
            />
            <div className="image-preview-overlay">
              <Button
                variant="danger"
                size="small"
                onClick={handleRemoveImage}
                disabled={disabled}
              >
                Remove
              </Button>
            </div>
          </div>
        ) : (
          <div className="upload-placeholder">
            <div className="upload-icon">📁</div>
            <div className="upload-text">
              <p className="upload-primary-text">
                {isDragOver ? 'Drop image here' : 'Drag and drop an image here'}
              </p>
              <p className="upload-secondary-text">or</p>
              <Button
                variant="outline"
                size="medium"
                disabled={disabled}
                onClick={handleBrowseClick}
              >
                Browse Files
              </Button>
            </div>
            <div className="upload-constraints">
              <p>Max size: {formatFileSize(maxSize)}</p>
              <p>Supported: {acceptedTypes.map(type => type.split('/')[1].toUpperCase()).join(', ')}</p>
            </div>
          </div>
        )}

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleInputChange}
          accept={acceptedTypes.join(',')}
          className="file-input"
          disabled={disabled}
          aria-hidden="true"
        />
      </div>

      <ErrorMessage message={error} type="error" />

      {selectedFile && (
        <div className="file-info">
          <div className="file-info-item">
            <span className="file-info-label">File:</span>
            <span className="file-info-value">{selectedFile.name}</span>
          </div>
          <div className="file-info-item">
            <span className="file-info-label">Size:</span>
            <span className="file-info-value">{formatFileSize(selectedFile.size)}</span>
          </div>
          <div className="file-info-item">
            <span className="file-info-label">Type:</span>
            <span className="file-info-value">{selectedFile.type}</span>
          </div>
        </div>
      )}
    </div>
  );
};

ImageUploader.propTypes = {
  onImageSelect: PropTypes.func.isRequired,
  maxSize: PropTypes.number,
  acceptedTypes: PropTypes.arrayOf(PropTypes.string),
  disabled: PropTypes.bool,
  className: PropTypes.string
};

export default React.memo(ImageUploader);
