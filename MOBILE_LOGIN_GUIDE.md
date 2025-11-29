# Mobile App Login Guide

## Problem Solved: "No Authenticated Driver Found"

The error "no authenticated driver found" occurred because:
- You logged in with a Django user account (admin)
- But there was no corresponding **driver profile** in Firebase for that user
- The mobile app requires both a user account AND a driver profile

## Solution Implemented

### 1. Mobile Login API Endpoint
A new mobile login API endpoint has been created at:
```
POST /api/login/
```

This endpoint:
- Authenticates the user with email and password
- Verifies the user has a driver profile in Firebase
- Returns both user and driver information

### 2. Driver Account Created
A driver account has been automatically created and linked to the admin user:

**Admin User Account:**
```
Email:    admin@mobilefleet.local
Password: Admin123!
```

**Linked Driver Profile:**
```
Driver ID:     Uk6TlXPaADYncw3GfVIN
Driver Name:   Admin Driver
Email:         admin@mobilefleet.local
Contact:       +63-900-000-0000
License:       DL-2025-00001
Status:        Active
```

## How to Login to Mobile App

### Using the Mobile Login API
Make a POST request to `/api/login/`:

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@mobilefleet.local",
    "password": "Admin123!"
  }'
```

### Expected Response (Success)
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

### Web Dashboard Login
You can also login to the web dashboard at `/login/`:
```
Username: admin
Password: Admin123!
```

## Creating Additional Driver Accounts

### Option 1: Using the Web Dashboard
1. Login to web dashboard with admin credentials
2. Go to Drivers → Add Driver
3. Fill in driver details:
   - Name: e.g., "John Doe"
   - Email: e.g., "john.doe@fleet.local"
   - Password: Set a secure password
   - Contact: Driver phone number
   - License Number: Driver's license number

### Option 2: Using the Script
Create a `create_new_driver.py` script:

```python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobileFleet.settings')
django.setup()

from monitoring.firebase_service import firebase_service
from django.contrib.auth.models import User

# Create Django user
user = User.objects.create_user(
    username='john.doe@fleet.local',
    email='john.doe@fleet.local',
    password='SecurePassword123!',
    first_name='John',
    last_name='Doe'
)

# Create driver profile
driver_data = {
    'name': 'John Doe',
    'email': 'john.doe@fleet.local',
    'contact': '+63-900-123-4567',
    'license_number': 'DL-2025-00002',
    'is_active': True,
    'auth_uid': user.id
}

driver_id = firebase_service.create_driver(driver_data)
print(f"Driver created: {driver_id}")
```

## Mobile App Login Flow

1. **Mobile App** sends credentials to `/api/login/`
2. **Server** validates credentials against Django authentication
3. **Server** searches Firebase for driver profile matching email
4. **Server** returns driver information to mobile app
5. **Mobile App** stores driver_id and uses it for trip operations

## API Endpoints Using Driver ID

Once logged in, the mobile app can use:

- **Start Trip**: `POST /api/trips/start/`
- **Stop Trip**: `POST /api/trips/{trip_id}/stop/`
- **Update Passengers**: `POST /api/trips/{trip_id}/passengers/`
- **Get Active Trips**: `GET /api/trips/active/?driver_id={driver_id}`
- **Get Driver Info**: `GET /api/drivers/{driver_id}/`

## Troubleshooting

### Still Getting "No Driver Found" Error
1. Check that the driver email matches the login email exactly
2. Verify driver profile exists in Firebase
3. Make sure driver `is_active` is set to `true`

### Wrong Credentials Error
- Double-check email and password spelling
- Passwords are case-sensitive
- Make sure you're using the email, not username for mobile app

### Database Issues
If drivers don't appear in Firebase:
1. Check Firebase connection in settings
2. Review Firebase service account credentials
3. Check if Firebase database is accessible

## Security Notes

- Never hardcode credentials in mobile app
- Store tokens securely on device
- Use HTTPS in production
- Implement token expiration
- Add rate limiting to login endpoint
- Consider OAuth2 for production
