# Driver Auto-Filter Debugging Guide

## Problem
Drivers logging in should automatically see only their own trips without needing to select a filter.

## How It Should Work

### 1. Backend (Django View)
When a driver logs in and visits the Trip Monitoring page:
1. `trip_list` view checks if current user is a driver
2. Matches by `django_user_id` or email (case-insensitive)
3. Automatically sets `driver_filter` to that driver's ID
4. Passes to template with `is_driver=True` and `user_driver` object

### 2. Frontend (JavaScript)
1. Django template initializes `currentDriverFilter` with the driver's ID
2. Page shows "My Trips" title and driver name badge
3. Firebase loads all trips from Firestore
4. JavaScript filters trips to show only matching `driver_id`
5. Display updates in real-time

## Debugging Steps

### Step 1: Check Django User is Linked to Driver
```bash
# In Django shell:
from django.contrib.auth.models import User
from monitoring.firebase_service import firebase_service

user = User.objects.get(username='driver_email@example.com')
print(f"User ID: {user.id}")
print(f"User Email: {user.email}")

drivers = firebase_service.get_all_drivers()
for driver in drivers:
    print(f"Driver: {driver.get('name')}")
    print(f"  - ID: {driver.get('driver_id')}")
    print(f"  - Email: {driver.get('email')}")
    print(f"  - django_user_id: {driver.get('django_user_id')}")
```

### Step 2: Check Browser Console (Open F12)

#### Expected Console Output When Page Loads:

```
🔧 Page Configuration:
   Status Filter: 'all'
   Driver Filter: 'driver_id_12345'
   Is Driver: true
   User Driver Name: 'John Doe'

✅ Status filter listener attached
✅ Driver filter listener attached
🚀 Trip monitoring page loaded
   Initial filters: status='all', driver='driver_id_12345'
   Waiting for Firebase connection...
```

#### When Firebase Connects:

```
Firebase config loaded for trip monitoring
Setting up Firebase real-time listeners for trip monitoring...
📥 Loaded 25 trips from Firebase
   Unique drivers in trips: driver_id_12345, driver_id_67890, driver_id_11111
   🎯 Filtering for driver: 'driver_id_12345'
📊 Total trips: 25, Filtered trips: 12
   Status filter: 'all', Driver filter: 'driver_id_12345'
Connected
```

### Step 3: Verify Django View Logic

**Check the view passes correct context:**
```python
# monitoring/views.py line 441-459
# Should log something like:
"Auto-filtering trips for driver john_doe (ID: driver_id_12345)"
```

Look for this in Django console output when page loads.

### Step 4: Check Trip Data Structure in Firebase

Go to Firebase Console → Firestore → trips collection.

Each trip should have:
```json
{
  "driver_id": "driver_id_12345",
  "start_terminal": "...",
  "destination_terminal": "...",
  "status": "in_progress",
  ...
}
```

**Common Issue:** If trips don't have `driver_id` field, filtering won't work.

### Step 5: Manual Console Test

Open browser DevTools console and run:

```javascript
// Check what the page thinks the driver filter is
console.log("Current Driver Filter:", currentDriverFilter);

// Check all trips data
console.log("All Trips:", allTripsData);

// Manually test the filter function
const testTrip = allTripsData[0];
console.log("Test Trip:", testTrip);
console.log("Trip Driver ID:", testTrip.driver_id);
console.log("Filter Driver ID:", currentDriverFilter);
console.log("Match:", testTrip.driver_id === currentDriverFilter);

// Check matching trips
const matchingTrips = allTripsData.filter(t => t.driver_id === currentDriverFilter);
console.log("Matching Trips:", matchingTrips.length);
```

## Common Issues and Solutions

### Issue 1: `driver_filter` is Empty
**Symptom:** Shows all trips, not filtered

**Causes:**
- User not linked to driver record
- Firebase service not finding driver
- Email/ID mismatch

**Solution:**
1. Check Django shell output above
2. Verify `django_user_id` field in driver record matches user ID
3. Verify email matches (case-insensitive)

### Issue 2: `driver_filter` Has Value But Still Shows All Trips
**Symptom:** Console shows correct filter, but no filtering

**Causes:**
- Trip `driver_id` doesn't match filter value
- String type mismatch (one is integer, one is string)
- Whitespace differences

**Solution:**
1. Check Firebase trip data structure
2. Compare exact values in console:
```javascript
console.log(typeof currentDriverFilter, currentDriverFilter);
console.log(allTripsData.map(t => typeof t.driver_id, t.driver_id));
```

### Issue 3: Firebase Not Connected
**Symptom:** Console shows "Disconnected" or timeout

**Causes:**
- Invalid Firebase credentials
- Network issue
- Firebase not initialized

**Solution:**
1. Check `/admin/firebase_config` endpoint response
2. Verify Firebase project settings
3. Check network tab for failed requests

### Issue 4: Driver Dropdown Shows But Doesn't Disappear for Drivers
**Symptom:** Drivers see driver selection dropdown instead of driver badge

**Causes:**
- `is_driver` context variable not passed to template
- Template conditional not working

**Solution:**
1. Check template has `{% if not is_driver %}` at line 67
2. Verify `is_driver=True` in view context (line 510 in views.py)

## Testing Workflow

1. **As Admin User:**
   - Login as admin
   - Visit Trip Monitoring
   - Console should show `Is Driver: false`
   - Can select any driver from dropdown
   - Trips filter properly

2. **As Driver User:**
   - Logout
   - Login as driver (email: driver's email address)
   - Visit Trip Monitoring
   - Console should show:
     - `Is Driver: true`
     - `User Driver Name: 'Driver Name'`
     - `Driver Filter: 'driver_id_xxxxx'`
   - Should see only own trips
   - No driver dropdown (shows badge instead)

## Logs to Watch

### Backend (Django)
```
# Check your Django development server output
Auto-filtering trips for driver john_doe (ID: driver_id_12345)
```

### Frontend (Browser Console)
```
🔧 Page Configuration:     // Initial setup
📥 Loaded X trips          // Firebase connection
🎯 Filtering for driver    // Filter being applied
📊 Total trips: X, Filtered trips: Y  // Result of filtering
```

## Data Validation Checklist

- [ ] Django user exists with email
- [ ] Driver record exists in Firebase
- [ ] Driver has `django_user_id` field set to user ID
- [ ] Driver has `email` field matching user email
- [ ] Driver has `driver_id` field
- [ ] Trips have `driver_id` field matching driver record
- [ ] No whitespace in driver IDs
- [ ] Email comparison is case-insensitive

## Still Not Working?

1. **Check Django logs** for auto-filter message
2. **Check browser console** for all 🔧, 📥, 🎯, 📊 logs
3. **Compare values** in console using code snippets above
4. **Verify Firebase data** in Firebase Console
5. **Try clearing browser cache** (Ctrl+Shift+Delete)
6. **Check network tab** for failed requests to `/firebase_config/`

## Quick Test Script

Paste this in browser console to test everything:

```javascript
console.clear();
console.log("=== DRIVER AUTO-FILTER DIAGNOSTIC ===");
console.log("Is Driver:", isDriver);
console.log("User Driver:", userDriverName);
console.log("Current Driver Filter:", currentDriverFilter);
console.log("All Trips Count:", allTripsData.length);
console.log("Trips for this driver:", allTripsData.filter(t => t.driver_id === currentDriverFilter).length);
console.log("Sample trip:", allTripsData[0]);
if (currentDriverFilter) {
  console.log("Does first trip match filter?", allTripsData[0]?.driver_id === currentDriverFilter);
}
```
