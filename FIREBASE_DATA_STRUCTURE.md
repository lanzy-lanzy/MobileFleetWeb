# Firebase Data Structure for Driver Auto-Filter

## Required Fields in Driver Records

For the auto-filter to work, each driver in Firebase must have these fields:

### Example Driver Document
```json
{
  "driver_id": "driver_20241129_001",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "django_user_id": 5,
  "contact": "+1-555-0123",
  "license_number": "DL-2024-001",
  "is_active": true,
  "created_at": "2024-11-29T10:00:00Z"
}
```

### Critical Fields
| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `driver_id` | String | Unique identifier for driver | `driver_20241129_001` |
| `email` | String | Must match Django user email | `john.doe@example.com` |
| `django_user_id` | Number | Django user ID (optional but recommended) | `5` |
| `name` | String | Display name | `John Doe` |

## Required Fields in Trip Records

Each trip must have a `driver_id` field that matches a driver's `driver_id`:

### Example Trip Document
```json
{
  "trip_id": "trip_20241129_001",
  "driver_id": "driver_20241129_001",
  "start_terminal": "terminal_001",
  "destination_terminal": "terminal_002",
  "passengers": 15,
  "status": "in_progress",
  "created_at": "2024-11-29T10:30:00Z",
  "start_time": "2024-11-29T10:30:00Z",
  "arrival_time": null
}
```

### Critical Fields
| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `driver_id` | String | Must match driver's `driver_id` exactly | `driver_20241129_001` |
| `status` | String | Trip status | `in_progress`, `completed`, `cancelled` |
| Other fields | Various | Trip details | See full document above |

## Django User Linking

### Django User Record
```python
from django.contrib.auth.models import User

user = User(
    username="john.doe@example.com",
    email="john.doe@example.com",
    first_name="John",
    last_name="Doe",
    id=5  # This is what goes in driver.django_user_id
)
```

### Linking Process
When creating a driver for an existing user:

1. **Get Django user ID:**
   ```python
   user = User.objects.get(email="john.doe@example.com")
   django_user_id = user.id  # e.g., 5
   ```

2. **Create driver in Firebase with that ID:**
   ```python
   driver_data = {
       "name": "John Doe",
       "email": "john.doe@example.com",
       "driver_id": "driver_20241129_001",
       "django_user_id": 5,  # ← Link to Django user
   }
   ```

## How Matching Works

When a driver visits the Trip Monitoring page:

```
1. Django View Loads
   ├─ Gets current user: User(id=5, email="john.doe@example.com")
   └─ Gets all drivers from Firebase
   
2. Tries to Match (checks both conditions)
   ├─ If driver.django_user_id == user.id → MATCH! ✅
   └─ OR if driver.email.lower() == user.email.lower() → MATCH! ✅
   
3. If Matched
   ├─ Sets driver_filter = driver.driver_id
   ├─ Passes is_driver=True to template
   └─ Passes user_driver info to template
   
4. Frontend Loads
   ├─ Gets driver_filter from Django template
   └─ Filters trips where trip.driver_id == driver_filter
```

## Verification Checklist

### In Firebase Console

1. **Navigate to Firestore:**
   - Go to `drivers` collection
   - Click on a driver document

2. **Check these fields exist:**
   - [ ] `driver_id` - Unique string
   - [ ] `email` - Lowercase email
   - [ ] `name` - Driver name
   - [ ] `django_user_id` - Numeric ID

3. **Navigate to `trips` collection:**
   - Click on a trip document

4. **Check these fields exist:**
   - [ ] `driver_id` - Matches a driver's `driver_id` exactly
   - [ ] `status` - One of: `in_progress`, `completed`, `cancelled`
   - [ ] Other trip data fields

### In Django Admin

```bash
# In Django shell:
python manage.py shell

from django.contrib.auth.models import User
from monitoring.firebase_service import firebase_service

# List all drivers and users
users = User.objects.all()
drivers = firebase_service.get_all_drivers()

# Check for matches
for user in users:
    print(f"\nUser: {user.username} (ID: {user.id})")
    matched = False
    for driver in drivers:
        if driver.get('django_user_id') == user.id or driver.get('email').lower() == user.email.lower():
            print(f"  ✅ Matches driver: {driver.get('name')} (ID: {driver.get('driver_id')})")
            matched = True
            break
    if not matched:
        print(f"  ❌ No matching driver found")
```

## Common Data Issues

### Issue 1: Email Mismatch
**Problem:** Driver email doesn't match user email

**Fix:**
```python
# Update driver document in Firebase
driver_data = {
    "email": user.email  # Use exact email from Django user
}
firebase_service.update_driver(driver_id, driver_data)
```

### Issue 2: Missing django_user_id
**Problem:** Driver doesn't have `django_user_id` field

**Fix:**
```python
# Add the field to existing driver
user = User.objects.get(email="john.doe@example.com")
driver_data = {
    "django_user_id": user.id
}
firebase_service.update_driver(driver_id, driver_data)
```

### Issue 3: Trips Missing driver_id
**Problem:** Existing trips don't have `driver_id` field

**Fix:**
```python
# Batch update trips to add driver_id
from monitoring.firebase_service import firebase_service
db = firebase_service.db

trips = db.collection('trips').stream()
for trip_doc in trips:
    trip_data = trip_doc.to_dict()
    if not trip_data.get('driver_id'):
        # Add driver_id (you need to know which driver this trip belongs to)
        trip_doc.reference.update({
            'driver_id': 'driver_20241129_001'  # Set appropriate driver_id
        })
```

### Issue 4: driver_id Type Mismatch
**Problem:** `driver_id` is stored as number instead of string

**Fix:**
```javascript
// In JavaScript, convert to string for comparison
const tripDriverId = String(trip.driver_id || '').trim();
const filterDriverId = String(currentDriverFilter).trim();
```

This is already handled in the code, but ensure Firebase stores `driver_id` as string.

## Sample Data

### Complete Driver Example
```json
{
  "contact": "+1-555-0100",
  "django_user_id": 3,
  "driver_id": "driver_20241129_gerland_dorona",
  "email": "gerland.dorona@fleetmanagement.com",
  "is_active": true,
  "license_number": "DL-2024-003",
  "name": "Gerland Dorona"
}
```

### Complete Trip Example
```json
{
  "arrival_time": "2024-11-29T15:39:00Z",
  "created_at": "2024-11-29T15:18:00Z",
  "destination_terminal": "terminal_pagadian",
  "driver_id": "driver_20241129_gerland_dorona",
  "passengers": 23,
  "start_terminal": "terminal_duminagag",
  "start_time": "2024-11-29T15:18:00Z",
  "status": "completed"
}
```

## Testing Data Creation

To ensure you have correct data structure:

```python
# Create test driver
driver_data = {
    "driver_id": "driver_test_001",
    "name": "Test Driver",
    "email": "test.driver@example.com",
    "contact": "+1-555-0199",
    "license_number": "TEST-001",
    "is_active": True,
    "django_user_id": <get_from_user_id>  # Replace with actual user ID
}
firebase_service.create_driver(driver_data)

# Create test trip
trip_data = {
    "driver_id": "driver_test_001",  # Must match driver's driver_id
    "start_terminal": "terminal_001",
    "destination_terminal": "terminal_002",
    "passengers": 10,
    "status": "in_progress"
}
firebase_service.create_trip(trip_data)
```

## Data Validation Script

Run in Django shell to validate structure:

```python
from monitoring.firebase_service import firebase_service

drivers = firebase_service.get_all_drivers()
trips = firebase_service.get_all_trips()

print("=== DRIVER VALIDATION ===")
for driver in drivers:
    required = ['driver_id', 'email', 'name']
    missing = [f for f in required if not driver.get(f)]
    if missing:
        print(f"❌ {driver.get('name')}: missing {missing}")
    else:
        print(f"✅ {driver.get('name')}")

print("\n=== TRIP VALIDATION ===")
for trip in trips[:5]:  # Check first 5
    if not trip.get('driver_id'):
        print(f"❌ Trip {trip.get('id')}: missing driver_id")
    else:
        # Check if driver exists
        driver_exists = any(d.get('driver_id') == trip.get('driver_id') for d in drivers)
        if driver_exists:
            print(f"✅ Trip {trip.get('id')[:8]}: driver exists")
        else:
            print(f"❌ Trip {trip.get('id')}: driver_id {trip.get('driver_id')} not found")

print(f"\n=== STATISTICS ===")
print(f"Total Drivers: {len(drivers)}")
print(f"Total Trips: {len(trips)}")
print(f"Trips with driver_id: {sum(1 for t in trips if t.get('driver_id'))}")
print(f"Drivers with django_user_id: {sum(1 for d in drivers if d.get('django_user_id'))}")
```
