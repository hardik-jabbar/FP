# FarmPower API Documentation

## Table of Contents
1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Equipment Marketplace](#equipment-marketplace)
4. [Field Management](#field-management)
5. [Crop Management](#crop-management)
6. [Service Booking](#service-booking)
7. [Parts Marketplace](#parts-marketplace)
8. [Messaging System](#messaging-system)
9. [Notifications](#notifications)
10. [Admin Operations](#admin-operations)
11. [Crop Calculator](#crop-calculator)
12. [Data Models](#data-models)

## Authentication

### Base URL
```
Production: https://fp-mipu.onrender.com/api
Development: http://localhost:8000/api
```

### Environment Configuration
The application requires the following environment variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://[username]:[password]@[host]:[port]/[database]
DB_HOST=[your-database-host]
DB_PORT=5432
DB_NAME=postgres
DB_USER=[your-database-user]
DB_PASSWORD=[your-database-password]

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://[your-project].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[your-anon-key]
SUPABASE_SERVICE_ROLE_KEY=[your-service-role-key]

# Application Configuration
ENVIRONMENT=production  # or 'development'
ALLOWED_ORIGINS=https://celebrated-crumble-e25621.netlify.app
```

### Security Features
- All endpoints are served over HTTPS
- CORS is configured to allow requests only from trusted origins
- Rate limiting is enabled to prevent abuse
- Security headers are enforced for all responses
- Structured logging and monitoring is enabled

### Authentication Headers
```
Authorization: Bearer <jwt_token>
```

## User Management

### Endpoints

#### Register User
```http
POST /api/users/register
Content-Type: application/json

{
    "email": "string",
    "password": "string",
    "full_name": "string",
    "role": "farmer" | "dealer" | "service_provider" | "admin"
}
```

#### Login
```http
POST /api/users/login
Content-Type: application/json

{
    "email": "string",
    "password": "string"
}
```

#### Get User Profile
```http
GET /api/users/me
```

#### Update User Profile
```http
PUT /api/users/me
Content-Type: application/json

{
    "full_name": "string",
    "email": "string"
}
```

#### Verify Email
```http
POST /api/users/verify-email
Content-Type: application/json

{
    "email": "string",
    "otp": "string"
}
```

## Equipment Marketplace

### Endpoints

#### List Tractors
```http
GET /api/tractors
Query Parameters:
- page: int
- limit: int
- brand: string
- model: string
- price_min: float
- price_max: float
- location: string
```

#### Create Tractor Listing
```http
POST /api/tractors
Content-Type: application/json

{
    "name": "string",
    "brand": "string",
    "model": "string",
    "year": int,
    "price": float,
    "description": "string",
    "location": "string",
    "images": ["string"]  // Base64 encoded images
}
```

#### Get Tractor Details
```http
GET /api/tractors/{tractor_id}
```

#### Update Tractor Listing
```http
PUT /api/tractors/{tractor_id}
Content-Type: application/json

{
    "name": "string",
    "price": float,
    "description": "string"
}
```

#### Delete Tractor Listing
```http
DELETE /api/tractors/{tractor_id}
```

## Field Management

### Endpoints

#### List Fields
```http
GET /api/fields
Query Parameters:
- page: int
- limit: int
```

#### Create Field
```http
POST /api/fields
Content-Type: application/json

{
    "name": "string",
    "area": float,
    "crop_type": "string",
    "soil_type": "string",
    "coordinates": {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[float, float], ...]]
        }
    }
}
```

#### Get Field Details
```http
GET /api/fields/{field_id}
```

#### Update Field
```http
PUT /api/fields/{field_id}
Content-Type: application/json

{
    "name": "string",
    "crop_type": "string",
    "soil_type": "string"
}
```

#### Delete Field
```http
DELETE /api/fields/{field_id}
```

## Crop Management

### Endpoints

#### List Crops
```http
GET /api/crops
Query Parameters:
- page: int
- limit: int
- field_id: int
```

#### Create Crop Entry
```http
POST /api/crops
Content-Type: application/json

{
    "name": "string",
    "field_id": int,
    "planting_date": "date",
    "expected_harvest_date": "date",
    "expected_yield": float,
    "costs": {
        "seeds": float,
        "fertilizer": float,
        "pesticides": float,
        "labor": float,
        "equipment": float
    }
}
```

#### Get Crop Details
```http
GET /api/crops/{crop_id}
```

#### Update Crop Entry
```http
PUT /api/crops/{crop_id}
Content-Type: application/json

{
    "name": "string",
    "expected_harvest_date": "date",
    "expected_yield": float
}
```

#### Delete Crop Entry
```http
DELETE /api/crops/{crop_id}
```

## Service Booking

### Endpoints

#### List Service Bookings
```http
GET /api/services
Query Parameters:
- page: int
- limit: int
- status: string
```

#### Create Service Booking
```http
POST /api/services
Content-Type: application/json

{
    "tractor_id": int,
    "service_type": "string",
    "scheduled_date": "datetime",
    "description": "string"
}
```

#### Get Service Booking Details
```http
GET /api/services/{booking_id}
```

#### Update Service Booking
```http
PUT /api/services/{booking_id}
Content-Type: application/json

{
    "scheduled_date": "datetime",
    "status": "string"
}
```

#### Cancel Service Booking
```http
DELETE /api/services/{booking_id}
```

## Parts Marketplace

### Endpoints

#### List Parts
```http
GET /api/parts
Query Parameters:
- page: int
- limit: int
- category: string
- tractor_brand: string
- condition: string
- price_min: float
- price_max: float
```

#### Create Part Listing
```http
POST /api/parts
Content-Type: application/json

{
    "name": "string",
    "category": "string",
    "tractor_brand": "string",
    "condition": "string",
    "price": float,
    "quantity": int,
    "description": "string",
    "images": ["string"]  // Base64 encoded images
}
```

#### Get Part Details
```http
GET /api/parts/{part_id}
```

#### Update Part Listing
```http
PUT /api/parts/{part_id}
Content-Type: application/json

{
    "price": float,
    "quantity": int,
    "description": "string"
}
```

#### Delete Part Listing
```http
DELETE /api/parts/{part_id}
```

## Messaging System

### Endpoints

#### List Conversations
```http
GET /api/messages/conversations
```

#### Get Conversation Messages
```http
GET /api/messages/conversations/{conversation_id}
Query Parameters:
- page: int
- limit: int
```

#### Send Message
```http
POST /api/messages
Content-Type: application/json

{
    "recipient_id": int,
    "content": "string"
}
```

#### Mark Messages as Read
```http
PUT /api/messages/conversations/{conversation_id}/read
```

## Notifications

### Endpoints

#### List Notifications
```http
GET /api/notifications
Query Parameters:
- page: int
- limit: int
- unread_only: boolean
```

#### Mark Notification as Read
```http
PUT /api/notifications/{notification_id}/read
```

#### Mark All Notifications as Read
```http
PUT /api/notifications/read-all
```

## Admin Operations

### Endpoints

#### List Users
```http
GET /api/admin/users
Query Parameters:
- page: int
- limit: int
- role: string
```

#### Ban User
```http
PUT /api/admin/users/{user_id}/ban
```

#### Unban User
```http
PUT /api/admin/users/{user_id}/unban
```

#### Delete User
```http
DELETE /api/admin/users/{user_id}
```

## Crop Calculator

### Endpoints

#### Calculate Profitability
```http
POST /api/crop-profit/calculate
Content-Type: application/json

{
    "crop_type": "string",
    "area": float,
    "expected_yield": float,
    "market_price": float,
    "costs": {
        "seeds": float,
        "fertilizer": float,
        "pesticides": float,
        "labor": float,
        "equipment": float
    }
}
```

#### Get Calculation History
```http
GET /api/crop-profit/history
Query Parameters:
- page: int
- limit: int
```

## Data Models

### User
```python
class User:
    id: int
    email: str
    hashed_password: str
    full_name: str
    role: UserRole
    is_active: bool
    is_banned: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
```

### Tractor
```python
class Tractor:
    id: int
    name: str
    brand: str
    model: str
    year: int
    price: float
    description: str
    location: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
```

### Field
```python
class Field:
    id: int
    name: str
    area: float
    crop_type: str
    soil_type: str
    coordinates: GeoJSON
    owner_id: int
    created_at: datetime
    updated_at: datetime
```

### Crop
```python
class Crop:
    id: int
    name: str
    field_id: int
    planting_date: date
    expected_harvest_date: date
    expected_yield: float
    costs: JSON
    owner_id: int
    created_at: datetime
    updated_at: datetime
```

### ServiceBooking
```python
class ServiceBooking:
    id: int
    tractor_id: int
    service_type: str
    scheduled_date: datetime
    status: str
    description: str
    user_id: int
    service_provider_id: int
    created_at: datetime
    updated_at: datetime
```

### Part
```python
class Part:
    id: int
    name: str
    category: str
    tractor_brand: str
    condition: str
    price: float
    quantity: int
    description: str
    seller_id: int
    created_at: datetime
    updated_at: datetime
```

### Message
```python
class Message:
    id: int
    sender_id: int
    recipient_id: int
    content: str
    is_read: bool
    created_at: datetime
```

### Notification
```python
class Notification:
    id: int
    recipient_id: int
    title: str
    content: str
    type: str
    is_read: bool
    created_at: datetime
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
    "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
    "detail": "Not authorized"
}
```

### 404 Not Found
```json
{
    "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## Pagination

List endpoints support pagination with the following query parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)

Response format:
```json
{
    "items": [],
    "total": 0,
    "page": 1,
    "limit": 10,
    "pages": 1
}
```

## File Upload

For image uploads, use multipart/form-data with the following constraints:
- Maximum file size: 5MB
- Allowed formats: JPEG, PNG
- Maximum dimensions: 1920x1080

## WebSocket Events

The API supports real-time updates via WebSocket connections:

### Connection
```
ws://localhost:8000/ws
```

### Events
- `message_received`: New message notification
- `notification`: New notification
- `service_status_update`: Service booking status change
- `tractor_status_update`: Tractor status change

## Security

- All endpoints require HTTPS
- JWT tokens expire after 24 hours
- Passwords are hashed using bcrypt
- API keys are required for external services
- CORS is enabled for specified origins
- Rate limiting is implemented
- Input validation is enforced
- SQL injection protection is in place
- XSS protection is implemented 