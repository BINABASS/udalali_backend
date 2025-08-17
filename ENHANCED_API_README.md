# Enhanced DigiDalali API

This document describes the enhanced API for the DigiDalali property marketplace, with a focus on seller and buyer functionality.

## Overview

The enhanced API provides a robust set of endpoints for managing properties, bookings, and communications between sellers and buyers. It includes improved validation, error handling, and security features.

## Key Features

### For Sellers
- List, create, update, and delete properties
- Upload and manage property images
- View and manage bookings for their properties
- Confirm or reject booking requests
- Communicate with potential buyers

### For Buyers
- Browse and search available properties
- Check property availability
- Make booking requests
- Communicate with property sellers
- Manage their own bookings

## Setup and Configuration

### Prerequisites
- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+
- Django REST Framework Simple JWT
- Other dependencies listed in requirements.txt

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd udalali_back
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Using the Enhanced API

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. To authenticate:

1. Obtain a token:
   ```bash
   curl -X POST http://localhost:8000/api/v1/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
   ```

2. Use the token in subsequent requests:
   ```bash
   curl -H "Authorization: Bearer your_token_here" http://localhost:8000/api/v1/properties/
   ```

### Available Endpoints

#### Properties
- `GET /api/v1/properties/` - List all properties (filterable)
- `POST /api/v1/properties/` - Create a new property (seller only)
- `GET /api/v1/properties/{id}/` - Get property details
- `PUT /api/v1/properties/{id}/` - Update property (owner or admin only)
- `DELETE /api/v1/properties/{id}/` - Delete property (owner or admin only)
- `GET /api/v1/properties/my_properties/` - List current user's properties (seller only)
- `GET /api/v1/properties/{id}/availability/` - Check property availability

#### Property Images
- `POST /api/v1/properties/{property_pk}/images/` - Upload an image
- `GET /api/v1/properties/{property_pk}/images/` - List property images
- `GET /api/v1/properties/{property_pk}/images/{id}/` - Get image details
- `PUT /api/v1/properties/{property_pk}/images/{id}/` - Update image
- `DELETE /api/v1/properties/{property_pk}/images/{id}/` - Delete image

#### Bookings
- `GET /api/v1/bookings/` - List user's bookings
- `POST /api/v1/bookings/` - Create a new booking
- `GET /api/v1/bookings/{id}/` - Get booking details
- `PUT /api/v1/bookings/{id}/` - Update booking
- `DELETE /api/v1/bookings/{id}/` - Cancel booking
- `POST /api/v1/bookings/{id}/confirm/` - Confirm booking (seller only)
- `POST /api/v1/bookings/{id}/reject/` - Reject booking (seller only)
- `GET /api/v1/bookings/seller/` - Get bookings for seller's properties

#### Messages
- `GET /api/v1/messages/` - List user's messages
- `POST /api/v1/messages/` - Send a new message
- `GET /api/v1/messages/{id}/` - Get message details
- `PUT /api/v1/messages/{id}/` - Update message (sender only)
- `DELETE /api/v1/messages/{id}/` - Delete message
- `POST /api/v1/messages/{id}/mark_read/` - Mark message as read
- `GET /api/v1/messages/unread_count/` - Get count of unread messages

### Testing the API

A test script is provided to verify the enhanced API functionality:

1. Make sure the development server is running:
   ```bash
   python manage.py runserver
   ```

2. Run the test script:
   ```bash
   python test_enhanced_api.py --username your_username --password your_password
   ```

   This will test both seller and buyer flows.

3. For testing public endpoints only (no authentication required):
   ```bash
   python test_enhanced_api.py
   ```

## Deployment Notes

For production deployment, make sure to:

1. Set `DEBUG = False` in `settings.py`
2. Configure proper database settings
3. Set up a production web server (e.g., Gunicorn with Nginx)
4. Configure HTTPS with a valid SSL certificate
5. Set appropriate CORS and security headers

## Troubleshooting

### Common Issues

1. **Authentication errors**:
   - Verify the token is correctly included in the Authorization header
   - Check that the token hasn't expired
   - Ensure the user account is active

2. **Permission denied**:
   - Verify the user has the correct permissions
   - Check that the user is a seller for seller-only endpoints

3. **Validation errors**:
   - Check the request payload matches the expected schema
   - Verify all required fields are provided

## Support

For support, please contact the development team at [support@digidalali.com](mailto:support@digidalali.com).
