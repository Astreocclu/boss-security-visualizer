# Homescreen Visualizer API Documentation

## Overview

The Homescreen Visualizer API provides endpoints for managing screen types, visualization requests, and generated images. The API uses JWT authentication and follows RESTful principles.

## Base URL

```
Production: https://your-domain.com/api
Development: http://localhost:8000/api
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

#### POST /auth/login/
Login with username and password.

**Request:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /auth/refresh/
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /auth/register/
Register a new user account.

**Request:**
```json
{
  "username": "new_user",
  "email": "newuser@example.com",
  "password": "secure_password",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 2,
    "username": "new_user",
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### POST /auth/logout/
Logout and blacklist refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## Screen Types

### GET /screentypes/
List all available screen types.

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Security",
      "description": "Security camera screens",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

### GET /screentypes/{id}/
Retrieve a specific screen type.

**Response:**
```json
{
  "id": 1,
  "name": "Security",
  "description": "Security camera screens",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## Visualization Requests

### GET /visualizations/
List visualization requests for the authenticated user.

**Query Parameters:**
- `status`: Filter by status (pending, processing, completed, failed)
- `screen_type`: Filter by screen type ID
- `ordering`: Order by field (created_at, updated_at, status)
- `page`: Page number for pagination

**Response:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/visualizations/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "testuser"
      },
      "original_image_url": "http://example.com/image.jpg",
      "screen_type_name": "Security",
      "status": "completed",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z",
      "result_count": 3,
      "generated_images": [
        {
          "id": 1,
          "image_url": "http://example.com/generated-1.jpg",
          "created_at": "2023-01-01T00:00:00Z"
        }
      ]
    }
  ]
}
```

### POST /visualizations/
Create a new visualization request.

**Request (multipart/form-data):**
```
image: <file>
screen_type: 1
```

**Response:**
```json
{
  "id": 2,
  "user": {
    "id": 1,
    "username": "testuser"
  },
  "original_image_url": "http://example.com/uploaded-image.jpg",
  "screen_type_name": "Security",
  "status": "pending",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "result_count": 0,
  "generated_images": []
}
```

### GET /visualizations/{id}/
Retrieve a specific visualization request.

**Response:**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "testuser"
  },
  "original_image_url": "http://example.com/image.jpg",
  "screen_type_name": "Security",
  "status": "completed",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "result_count": 3,
  "generated_images": [
    {
      "id": 1,
      "image_url": "http://example.com/generated-1.jpg",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

### DELETE /visualizations/{id}/
Delete a visualization request (only if owned by authenticated user).

**Response:** 204 No Content

## Generated Images

### GET /generated-images/
List generated images for the authenticated user.

**Query Parameters:**
- `visualization`: Filter by visualization request ID
- `ordering`: Order by field (created_at)
- `page`: Page number for pagination

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "visualization_request": 1,
      "image_url": "http://example.com/generated-1.jpg",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

### GET /generated-images/{id}/
Retrieve a specific generated image.

**Response:**
```json
{
  "id": 1,
  "visualization_request": 1,
  "image_url": "http://example.com/generated-1.jpg",
  "created_at": "2023-01-01T00:00:00Z"
}
```

## Error Responses

The API returns standard HTTP status codes and error messages:

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": {
    "field_name": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
  "detail": "Too many requests. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error. Please try again later."
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Login attempts**: 5 per minute per IP
- **Registration**: 3 per hour per IP
- **API requests**: 100 per minute per authenticated user

## File Upload Constraints

- **Maximum file size**: 10MB
- **Supported formats**: JPEG, PNG, GIF, WebP
- **Image dimensions**: Minimum 100x100px, Maximum 4096x4096px

## Status Codes

### Visualization Request Status
- `pending`: Request received, waiting for processing
- `processing`: Currently being processed
- `completed`: Processing completed successfully
- `failed`: Processing failed due to an error

## Pagination

List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 20, max: 100)

## Filtering and Ordering

Most list endpoints support filtering and ordering:
- Use query parameters for filtering
- Use `ordering` parameter for sorting (prefix with `-` for descending)

Example: `/api/visualizations/?status=completed&ordering=-created_at`
