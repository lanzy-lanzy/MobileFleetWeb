# Mobile Authentication Fix - "No Authenticated Driver Found"

## Problem
When logging into the mobile app, you received an error:
```
No authenticated driver found
```

## Root Cause
The mobile app requires **two separate accounts**:
1. **User Account** - Django authentication (username/password)
2. **Driver Profile** - Firebase database record (driver details)

When you logged in with the admin account, only the User Account existed. The Driver Profile was missing from Firebase.

## Solution Implemented

### 1. Mobile Login API Endpoint
Created a new secure endpoint: `POST /api/login/`

**What it does:**
- Validates user credentials against Django authentication
- Searches Firebase for a driver profile with matching email
- Returns both user and driver information
- Returns proper error messages if either is missing

### 2. Driver Account Created
Automatically created a driver profile in Firebase linked to the admin user:

```
Email:           admin@mobilefleet.local
Driver ID:       Uk6TlXPaADYncw3GfVIN
Driver Name:     Admin Driver
Contact:         +63-900-000-0000
License Number:  DL-2025-00001
Status:          Active
```

### 3. Files Modified

**monitoring/api_views.py**
- Added `mobile_login()` function
- Imported authentication module
- Added proper error handling

**monitoring/api_urls.py**
- Added route: `path('login/', api_views.mobile_login, name='api_mobile_login')`

## How to Use

### Mobile App Login
Send a POST request to the `/api/login/` endpoint:

```json
{
  "email": "admin@mobilefleet.local",
  "password": "Admin123!"
}
```

### Success Response
```json
{
  "success": true,
  "driver": {
    "driver_id": "Uk6TlXPaADYncw3GfVIN",
    "name": "Admin Driver",
    "email": "admin@mobilefleet.local",
    "contact": "+63-900-000-0000",
    "license_number": "DL-2025-00001",
    "is_active": true
  },
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@mobilefleet.local",
    "first_name": "Admin"
  },
  "message": "Login successful"
}
```

### Error Responses

**Invalid Credentials:**
```json
{
  "error": "Invalid email or password",
  "status": 401
}
```

**No Driver Profile:**
```json
{
  "error": "No authenticated driver found",
  "user_authenticated": true,
  "message": "User account exists but no driver profile found. Please contact administrator.",
  "status": 404
}
```

## Login Credentials

### Admin Account (Web & Mobile)
```
Email:    admin@mobilefleet.local
Password: Admin123!
```

### Web Dashboard Login
- URL: `http://localhost:8000/login/`
- Username: `admin`
- Password: `Admin123!`

## Creating New Driver Accounts

### Via Web Dashboard
1. Login to web dashboard
2. Navigate to Drivers → Add Driver
3. Fill in:
   - Name: Driver full name
   - Email: Unique email address
   - Password: Secure password
   - Contact: Phone number
   - License Number: Driver license ID
4. Submit - this creates both User Account and Driver Profile

### Via Management Script
```python
from django.contrib.auth.models import User
from monitoring.firebase_service import firebase_service

# Create user account
user = User.objects.create_user(
    username='john@fleet.local',
    email='john@fleet.local',
    password='SecurePassword123!',
    first_name='John'
)

# Create driver profile
driver_data = {
    'name': 'John Doe',
    'email': 'john@fleet.local',
    'contact': '+63-900-123-4567',
    'license_number': 'DL-2025-00002',
    'is_active': True
}

driver_id = firebase_service.create_driver(driver_data)
```

## Testing the API

### Using curl
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@mobilefleet.local",
    "password": "Admin123!"
  }'
```

### Using Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/login/',
    json={
        'email': 'admin@mobilefleet.local',
        'password': 'Admin123!'
    }
)

print(response.json())
```

### Using Test Script
```bash
python test_mobile_login.py
```

## Next Steps

1. **Update Mobile App**
   - Change login endpoint to `/api/login/`
   - Send email and password (not username)
   - Store driver_id from response
   - Use driver_id for subsequent API calls

2. **Add More Drivers**
   - Create driver accounts via web dashboard
   - Each driver needs both User Account and Driver Profile
   - Email must match between Django and Firebase

3. **Implement Token/Session Management**
   - Consider implementing JWT tokens
   - Add token refresh mechanism
   - Store tokens securely on mobile device

## Files Created
- `create_driver_account.py` - Script to create driver accounts
- `test_mobile_login.py` - API endpoint test script
- `MOBILE_LOGIN_GUIDE.md` - Detailed guide for mobile app developers
- `MOBILE_AUTH_FIX.md` - This file

## Security Notes
- Email must match between Django and Firebase
- Use HTTPS in production
- Implement rate limiting on login endpoint
- Add account lockout after failed attempts
- Use secure password storage
- Consider OAuth2 for enterprise use
