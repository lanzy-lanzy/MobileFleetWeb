# Driver Authentication Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Mobile Fleet System                          │
└─────────────────────────────────────────────────────────────────┘

                     ┌──────────────────┐
                     │  Mobile App      │
                     │  (Driver)        │
                     └────────┬─────────┘
                              │
                    POST /api/login/
                    {email, password}
                              │
                              ↓
            ┌─────────────────────────────────────┐
            │   Django Backend (Server)           │
            │   ┌─────────────────────────────┐  │
            │   │ /api/login/ Endpoint        │  │
            │   │                             │  │
            │   │ 1. Authenticate User        │  │
            │   │    vs Django User DB        │  │
            │   │                             │  │
            │   │ 2. Find Driver Profile      │  │
            │   │    in Firestore             │  │
            │   │                             │  │
            │   │ 3. Return Driver Info       │  │
            │   │    + User Info              │  │
            │   └────────┬────────────────────┘  │
            │            │                        │
            │    ┌───────┴──────────┐             │
            │    │                  │             │
            │    ↓                  ↓             │
            │  ┌──────────────┐  ┌──────────┐    │
            │  │ Django User  │  │Firebase  │    │
            │  │ Database     │  │Firestore │    │
            │  │              │  │Database  │    │
            │  │ Users:       │  │          │    │
            │  │ - username   │  │Drivers:  │    │
            │  │ - email      │  │- email   │    │
            │  │ - password   │  │- name    │    │
            │  │ - first_name │  │- contact │    │
            │  │ - last_name  │  │- license │    │
            │  └──────────────┘  │- auth_id │    │
            │                     │-django_id    │
            │                     └──────────┘    │
            └─────────────────────────────────────┘
                              │
                    Response with driver_id
                              │
                              ↓
                     ┌──────────────────┐
                     │  Mobile App      │
                     │  Stores:         │
                     │  - driver_id     │
                     │  - name          │
                     │  - email         │
                     │  - contact       │
                     └──────────────────┘
```

## Driver Creation Flow

### OLD FLOW (Before Fix) ❌
```
Admin fills "Add Driver" form
         ↓
      Django Process
         ↓
    ┌────┴─────────────────┐
    │                      │
    ↓                      ↓
Firebase Auth User    Firestore Driver
✓ Created              ✓ Created
    │                      │
    └────┬──────────────────┘
         │
    ✗ No Django User!
         │
         ↓
Mobile Login fails!
"No authenticated driver found"
```

### NEW FLOW (After Fix) ✅
```
Admin fills "Add Driver" form
         ↓
      Django Process
         ↓
    ┌────┴──────┬──────────┬────────┐
    │           │          │        │
    ↓           ↓          ↓        ↓
Django User  Firebase  Firestore  Link All
Account      Auth      Driver      Three
Created      User      Profile     Together
✓            Created   Created     ✓
    │           │          │        │
    └───────────┴──────────┴────────┘
                │
                ↓
         All 3 Created!
                │
                ↓
         Mobile Login works
         ✓ Success!
```

## Database Synchronization

```
┌─────────────────────────────────────────────────────────────┐
│                    BEFORE (Broken)                          │
├─────────────────────────────────────────────────────────────┤

Django User Database:
  (empty)

Firebase Auth:
  email: maria.santos@mobilefleet.com
  password: hashed

Firestore Drivers:
  driver_id: lwh7duBz81DDz...
  name: Maria Santos
  email: maria.santos@mobilefleet.com

Problem:
  Mobile login → looks for Django user
  Django user → NOT FOUND
  Login fails! ✗

└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    AFTER (Fixed)                            │
├─────────────────────────────────────────────────────────────┤

Django User Database:
  id: 42
  username: maria.santos@mobilefleet.com
  email: maria.santos@mobilefleet.com
  password: hashed
  first_name: Maria
  last_name: Santos

Firebase Auth:
  uid: firebase_auth_uid_xxx
  email: maria.santos@mobilefleet.com
  password: hashed

Firestore Drivers:
  driver_id: lwh7duBz81DDz...
  name: Maria Santos
  email: maria.santos@mobilefleet.com
  auth_uid: firebase_auth_uid_xxx
  django_user_id: 42

Perfect Sync:
  Mobile login → finds Django user ✓
  Authenticates password ✓
  Finds driver profile ✓
  Returns driver info ✓
  Login succeeds! ✓

└─────────────────────────────────────────────────────────────┘
```

## Mobile App Login Sequence Diagram

```
Mobile App              Server                Django User      Firestore
   (Client)           (Backend)               Database         Database
     │                   │                      │                 │
     │ POST /api/login/  │                      │                 │
     │─email             │                      │                 │
     │─password          │                      │                 │
     ├──────────────────→│                      │                 │
     │                   │ authenticate()       │                 │
     │                   │──────────────────────→│                 │
     │                   │                      │ verify email     │
     │                   │                      │ check password   │
     │                   │←──────────────────────│                 │
     │                   │ ✓ User authenticated │                 │
     │                   │                      │                 │
     │                   │ search drivers       │                 │
     │                   │─────────────────────────────────────→│
     │                   │                      │                 │
     │                   │                      │   find by email  │
     │                   │                      │←─────────────────│
     │                   │                      │ driver document  │
     │                   │                      │                 │
     │ {success: true,   │                      │                 │
     │  driver: {...},   │                      │                 │
     │  user: {...}}     │                      │                 │
     │←──────────────────│                      │                 │
     │ Login Successful! │                      │                 │
     │                   │                      │                 │
```

## Error Cases

### Case 1: Wrong Password
```
/api/login/ receives: {email: maria@fleet.com, password: wrong}
                ↓
Django User found with email ✓
Password check                ✗ FAIL
                ↓
Response: {"error": "Invalid email or password"}
Status: 401 Unauthorized
```

### Case 2: No Django User (Old Data)
```
/api/login/ receives: {email: maria@fleet.com, password: correct}
                ↓
Django User lookup        ✗ NOT FOUND
                ↓
Response: {"error": "Invalid email or password"}
Status: 401 Unauthorized
Note: Driver profile exists but user can't login
Solution: Run fix_existing_drivers.py
```

### Case 3: No Driver Profile
```
/api/login/ receives: {email: admin@django.com, password: correct}
                ↓
Django User found ✓
Password check ✓
Firestore lookup ✗ NOT FOUND
                ↓
Response: {
  "error": "No authenticated driver found",
  "user_authenticated": true,
  "message": "User exists but no driver profile"
}
Status: 404 Not Found
Note: User account exists but driver profile missing
```

## Implementation Details

### Driver Creation Steps (Code)

```python
1. Validate input
   - Check: name, email, password provided
   - Check: email not already in database

2. Create Django User
   user = User.objects.create_user(
       username=email,          # Email as username
       email=email,             # Same email
       password=password,       # Hashed
       first_name=name_parts[0],
       last_name=name_parts[1]
   )
   → Saves to Django User DB

3. Create Firebase Auth
   auth_uid = firebase_service.create_auth_user(
       email, password, name
   )
   → Saves to Firebase Auth

4. Create Driver Profile
   driver_data = {
       'name': name,
       'email': email,
       'contact': contact,
       'license_number': license,
       'is_active': True,
       'auth_uid': auth_uid,        # Link to Firebase
       'django_user_id': user.id    # Link to Django
   }
   driver_id = firebase_service.create_driver(driver_data)
   → Saves to Firestore

5. Cleanup on failure
   - If step 2 fails: Nothing to cleanup
   - If step 3 fails: Delete user from step 2
   - If step 4 fails: Delete user from step 2
```

### Mobile Login Steps (Code)

```python
1. Receive request
   email, password = request.body

2. Authenticate Django User
   user = authenticate(username=email, password=password)
   if user is None:
       return 401 Unauthorized

3. Find Driver in Firestore
   drivers = firebase_service.get_all_drivers()
   driver = find driver with matching email
   if not driver:
       return 404 Not Found

4. Return Success
   return {
       'success': True,
       'driver': driver,
       'user': {id, username, email, first_name},
       'message': 'Login successful'
   }
```

## Summary

**Key Insight**: Driver authentication requires THREE synchronized accounts:

1. **Django User** - for `/api/login/` endpoint authentication
2. **Firebase Auth** - for Firebase security rules
3. **Driver Profile** - for trip and driver management

All three must exist and reference each other for the system to work.

**The Fix**: Updated driver creation to ensure all three are created together and properly linked.

**Result**: Drivers can now login seamlessly to mobile app! ✓
