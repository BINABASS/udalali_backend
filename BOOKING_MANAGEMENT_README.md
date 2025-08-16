# Property Booking Management System

## Overview
This system allows sellers to view and manage bookings for their properties. Sellers can confirm or reject pending bookings, view booking details, and track the status of all bookings.

## New Backend Endpoints

### 1. Confirm Booking
- **Endpoint**: `POST /api/bookings/{id}/confirm/`
- **Description**: Allows sellers to confirm a pending booking
- **Permissions**: Only the property seller can confirm bookings
- **Response**: Returns confirmation status and message

### 2. Reject Booking
- **Endpoint**: `POST /api/bookings/{id}/reject/`
- **Description**: Allows sellers to reject a pending booking
- **Permissions**: Only the property seller can reject bookings
- **Response**: Returns rejection status and message

### 3. Get Seller Bookings
- **Endpoint**: `GET /api/bookings/seller_bookings/`
- **Description**: Retrieves all bookings for properties owned by the current seller
- **Permissions**: Only sellers can access this endpoint
- **Query Parameters**:
  - `status`: Filter by booking status (pending, confirmed, cancelled, completed)
  - `property`: Filter by specific property ID

## Frontend Components

### 1. PropertyBookings Component
- **Location**: `udalali_front/src/components/dashboard/seller/PropertyBookings.js`
- **Features**:
  - View all property bookings with detailed information
  - Filter bookings by status and property
  - Confirm or reject pending bookings
  - View customer details, dates, pricing, and special requests
  - Real-time status updates

### 2. Enhanced SellerDashboard
- **Location**: `udalali_front/src/components/dashboard/seller/SellerDashboard.js`
- **New Features**:
  - Tab navigation between Properties and Bookings
  - Integrated PropertyBookings component
  - Seamless switching between property management and booking management

## API Service Functions

### 1. confirmBooking(bookingId)
- Confirms a pending booking
- Returns success/error messages

### 2. rejectBooking(bookingId)
- Rejects a pending booking
- Returns success/error messages

### 3. getSellerBookings(params)
- Retrieves seller's property bookings
- Supports filtering by status and property

## User Experience Features

### 1. Smart Date Handling
- Automatically adjusts end dates if same as start date
- Provides helpful suggestions for date selection
- Clear validation messages

### 2. Real-time Updates
- Immediate status changes after confirm/reject actions
- Automatic refresh of booking lists
- Success/error notifications

### 3. Comprehensive Information Display
- Property details with images
- Customer information
- Booking dates and duration
- Pricing breakdown
- Special requests and notes

### 4. Status Management
- **Pending**: Waiting for seller response
- **Confirmed**: Approved by seller
- **Cancelled**: Rejected by seller
- **Completed**: Finished stay

## Security Features

### 1. Role-Based Access Control
- Only sellers can access booking management
- Sellers can only manage bookings for their own properties
- Proper permission validation on all endpoints

### 2. Data Validation
- Input validation for all booking operations
- Status transition validation
- Date range validation

## Usage Instructions

### For Sellers:

1. **Access Booking Management**:
   - Navigate to Seller Dashboard
   - Click on "Property Bookings" tab

2. **View Bookings**:
   - See all bookings for your properties
   - Filter by status or specific property
   - View detailed information for each booking

3. **Manage Bookings**:
   - **Confirm**: Click "Confirm" button for pending bookings
   - **Reject**: Click "Reject" button for pending bookings
   - **View Details**: See customer info, dates, pricing, and requests

4. **Monitor Status**:
   - Track booking status changes
   - View confirmation/rejection history
   - Monitor completed bookings

### For Buyers:

1. **Submit Bookings**:
   - Select property and dates
   - Add special requests if needed
   - Submit booking request

2. **Track Status**:
   - View booking status (Pending → Confirmed/Rejected)
   - Receive confirmation emails
   - Monitor booking progress

## Technical Implementation

### Backend Changes:
- Added new actions to `BookingViewSet`
- Enhanced permission checking
- Added seller-specific endpoints

### Frontend Changes:
- Created new `PropertyBookings` component
- Enhanced `SellerDashboard` with tab navigation
- Added new API service functions
- Improved user experience with smart validation

## Future Enhancements

1. **Email Notifications**: Send confirmation/rejection emails to buyers
2. **SMS Notifications**: Text message updates for urgent bookings
3. **Calendar Integration**: Sync with external calendar systems
4. **Analytics Dashboard**: Booking trends and performance metrics
5. **Automated Responses**: Auto-confirm bookings based on rules
6. **Payment Integration**: Handle deposits and payments
7. **Review System**: Post-stay reviews and ratings

## Testing

### Backend Testing:
```bash
# Test seller bookings endpoint
curl -X GET "http://localhost:8000/api/bookings/seller_bookings/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test confirm booking
curl -X POST "http://localhost:8000/api/bookings/{id}/confirm/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test reject booking
curl -X POST "http://localhost:8000/api/bookings/{id}/reject/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend Testing:
1. Start React development server: `npm start`
2. Navigate to Seller Dashboard
3. Switch to "Property Bookings" tab
4. Test filtering and booking management features

## Support

For technical support or questions about the booking management system, please refer to the main project documentation or contact the development team. 