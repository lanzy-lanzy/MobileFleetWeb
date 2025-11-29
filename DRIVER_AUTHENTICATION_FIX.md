# Driver Authentication Fix

## Problem
When creating a driver through the "Add Driver" form, the driver appeared in Firebase but couldn't login to the mobile app with "not authenticated" error.

## Root Cause
The old driver creation process was missing a critical step:

**Before (incomplete):**
1. ✓ Create Firebase Auth user
2. ✓ Create Driver profile in Firestore
3. ✗ **Missing: Create Django User Account**

The mobile app's `/api/login/` endpoint requires:
1. A valid Django User (for authentication)
2. A matching Driver profile in Firebase

Without both, login fails.

## Solution
Updated `driver_create` view to create **THREE accounts** in the correct order:

**After (complete):**
1. ✓ Create Django User Account (username = email)
2. ✓ Create Firebase Auth user
3. ✓ Create Driver profile in Firestore (linked to both)

## How It Works Now

### Step 1: Fill Add Driver Form
```
Full Name:       Maria Santos
Email:           maria.santos@mobilefleet.com
Password:        SecurePass123!
Contact:         +63 923 456 7890
License:         NO2-13-456789
```

### Step 2: Submit Form
The system automatically creates:

**Django User Account:**
```
Username: maria.santos@mobilefleet.com
Email:    maria.santos@mobilefleet.com
Password: SecurePass123!
```

**Firebase Auth User:**
```
Email: maria.santos@mobilefleet.com
Password: SecurePass123!
```

**Driver Profile in Firestore:**
```
{
  "name": "Maria Santos",
  "email": "maria.santos@mobilefleet.com",
  "contact": "+63 923 456 7890",
  "license_number": "NO2-13-456789",
  "is_active": true,
  "auth_uid": "firebase_uid_xxx",
  "django_user_id": 42
}
```

### Step 3: Driver Can Login
Driver can now successfully login to mobile app:
```
Email:    maria.santos@mobilefleet.com
Password: SecurePass123!
```

## Changes Made

**File: monitoring/views.py**

### Imports Added
```python
from django.contrib.auth.models import User
```

### driver_create() Function Updated
- Creates Django User first (for `/api/login/` to work)
- Validates email doesn't already exist
- Parses name into first_name and last_name
- Links Django user to Driver profile
- Cleans up on failure (deletes Django user if Firebase fails)
- Better error messages for users

## Error Handling

The system now handles:
- ✓ Duplicate email addresses
- ✓ Failed Django user creation
- ✓ Failed Firebase auth creation
- ✓ Failed driver profile creation
- ✓ Automatic cleanup if any step fails

## Testing

### Test Creating a New Driver
1. Login to web dashboard: `http://localhost:8000/login/`
2. Go to Drivers → Add Driver
3. Fill in form with unique email
4. Submit
5. See success message with email address
6. Login to mobile app with that email and password
7. Should work without "not authenticated" error

### Verify in Django Admin
```bash
python manage.py shell
from django.contrib.auth.models import User
User.objects.all()  # Should see the new driver user
```

### Verify in Firebase Console
Go to Firestore Database:
- drivers collection
- Look for the new driver
- Should have `django_user_id` field

## Database Schema

Now drivers have:
```
Django User Account:
- id
- username (email)
- email
- password (hashed)
- first_name
- last_name

Firebase Driver Profile:
- driver_id
- name
- email
- contact
- license_number
- is_active
- auth_uid (Firebase Auth UID)
- django_user_id (Link to Django User)
```

## Mobile App Login Flow

```
1. Mobile App → POST /api/login/
   {
     "email": "maria.santos@mobilefleet.com",
     "password": "SecurePass123!"
   }

2. Server → Authenticate against Django User
   ✓ User found and password matches

3. Server → Search Firestore for driver with email
   ✓ Driver found with matching email

4. Server → Return driver info
   {
     "success": true,
     "driver": { ... },
     "user": { ... }
   }

5. Mobile App → Store driver_id and proceed
```

## Migration for Existing Drivers

Existing drivers created before this fix:
1. Have Firebase driver profile
2. Don't have Django user account
3. Can't login to mobile app

**To fix existing drivers:**

### Option 1: Recreate Driver
1. Delete old driver in Firebase
2. Create new driver via "Add Driver" form
3. Driver can now login

### Option 2: Manual Django User Creation
```python
from django.contrib.auth.models import User
from monitoring.firebase_service import firebase_service

# Get existing driver from Firebase
drivers = firebase_service.get_all_drivers()
driver = drivers[0]  # Example driver

# Create corresponding Django user
user = User.objects.create_user(
    username=driver['email'],
    email=driver['email'],
    password='TemporaryPassword123!',  # Ask driver to reset
    first_name=driver['name'].split()[0]
)

# Update driver with Django user ID
firebase_service.update_driver(
    driver['driver_id'],
    {'django_user_id': user.id}
)
```

## Best Practices

1. **Always use "Add Driver" form** for creating new drivers
2. **Never manually create drivers** in Firebase console
3. **Email must match** between Django and Firebase
4. **Test login** immediately after creating driver
5. **Share credentials securely** with driver (not in chat/email)

## Future Enhancements

Consider:
- Email verification for new drivers
- Password reset functionality
- Bulk driver import
- Auto-generate temporary passwords
- Email notification to new drivers
