# Test Driver Authentication - Step by Step

## Prerequisites

- Django development server running
- Firebase project configured
- Access to web dashboard

## Test Scenario 1: Create New Driver and Login

### Step 1: Login to Web Dashboard

```
URL: http://localhost:8000/login/
Username: admin
Password: Admin123!
```

Expected: Dashboard loads successfully ✓

### Step 2: Navigate to Add Driver

```
Path: Dashboard → Drivers (left menu)
      → Add Driver (green button)
URL: http://localhost:8000/drivers/create/
```

Expected: "Add New Driver" form appears ✓

### Step 3: Fill Driver Form

```
Full Name:              John Doe
Email:                  john.doe@fleet.com
Password:               JohnPass123!
Contact Number:         +63 923 456 7890
Driver's License:       JD-2025-001234
```

Expected: All fields highlighted, ready to submit ✓

### Step 4: Submit Form

```
Click: "Add Driver" button
```

Expected: 
- Green success message appears
- Message says: "Driver 'John Doe' created successfully. Can now login with email: john.doe@fleet.com"
- Redirects to drivers list
- New driver appears in list

✓ Django User Account created
✓ Firebase Auth User created
✓ Firestore Driver Profile created

### Step 5: Logout from Dashboard

```
Top right corner → User avatar → "Sign out"
```

Expected: Logged out, redirected to login page ✓

### Step 6: Test Mobile App Login (Simulation)

#### Option A: Using curl

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@fleet.com",
    "password": "JohnPass123!"
  }'
```

Expected Response:
```json
{
  "success": true,
  "driver": {
    "driver_id": "abc123def456...",
    "name": "John Doe",
    "email": "john.doe@fleet.com",
    "contact": "+63 923 456 7890",
    "license_number": "JD-2025-001234",
    "is_active": true,
    "django_user_id": 2
  },
  "user": {
    "id": 2,
    "username": "john.doe@fleet.com",
    "email": "john.doe@fleet.com",
    "first_name": "John"
  },
  "message": "Login successful"
}
```

Status: 200 OK ✓

#### Option B: Using Python

```python
import requests

response = requests.post(
    'http://localhost:8000/api/login/',
    json={
        'email': 'john.doe@fleet.com',
        'password': 'JohnPass123!'
    }
)

print(response.status_code)  # Should be 200
print(response.json())
```

Expected: Returns driver info as above ✓

#### Option C: Using Postman/Insomnia

1. Create new POST request
2. URL: `http://localhost:8000/api/login/`
3. Headers tab:
   ```
   Content-Type: application/json
   ```
4. Body tab (raw JSON):
   ```json
   {
     "email": "john.doe@fleet.com",
     "password": "JohnPass123!"
   }
   ```
5. Click Send

Expected: Status 200, response shows driver info ✓

## Test Scenario 2: Wrong Password

### Test Invalid Password

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@fleet.com",
    "password": "WrongPassword"
  }'
```

Expected Response:
```json
{
  "error": "Invalid email or password"
}
```

Status: 401 Unauthorized ✓

## Test Scenario 3: Non-existent Email

### Test Email That Doesn't Exist

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@fleet.com",
    "password": "SomePassword123!"
  }'
```

Expected Response:
```json
{
  "error": "Invalid email or password"
}
```

Status: 401 Unauthorized ✓

## Test Scenario 4: Duplicate Email

### Try Creating Driver with Existing Email

1. Go to: `http://localhost:8000/drivers/create/`
2. Fill form:
   ```
   Full Name: Jane Doe
   Email: john.doe@fleet.com (SAME AS BEFORE)
   Password: AnyPass123!
   ...
   ```
3. Click: "Add Driver"

Expected:
- Red error message
- Message: "A user with email 'john.doe@fleet.com' already exists"
- Form stays on page with data cleared
- No duplicate created

✓ Duplicate prevention works ✓

## Test Scenario 5: Verify Django User Created

### Check Django Admin

```
URL: http://localhost:8000/admin/
Username: admin
Password: Admin123!
```

Path: Admin → Authentication and Authorization → Users

Expected: 
- "john.doe@fleet.com" user exists
- Username: john.doe@fleet.com
- Email: john.doe@fleet.com
- First Name: John
- Last Name: Doe

✓ Django User Account verified ✓

## Test Scenario 6: Verify Firestore Records

### Check Firebase Console

1. Go to: https://console.firebase.google.com
2. Select your project
3. Go to: Firestore Database → Data tab
4. Navigate to: drivers collection

Expected:
- Document with driver_id exists
- Data includes:
  ```
  name: "John Doe"
  email: "john.doe@fleet.com"
  contact: "+63 923 456 7890"
  license_number: "JD-2025-001234"
  is_active: true
  auth_uid: "firebase_uid_xxx"
  django_user_id: 2
  ```

✓ Firestore Record verified ✓

## Test Scenario 7: Login with Web Dashboard

### Logout and Login as Driver (if desired)

```
1. Logout: Top right → Sign out
2. Login URL: http://localhost:8000/login/
3. Username: john.doe@fleet.com
4. Password: JohnPass123!
```

Expected:
- Dashboard loads
- User menu shows "John" (first name)
- Can access all driver features

✓ Web login works ✓

## Verification Checklist

After completing all tests:

- [ ] Driver created successfully via "Add Driver" form
- [ ] Success message shows correct email
- [ ] Django user exists in admin panel
- [ ] Firebase user exists (can check in Firebase Auth)
- [ ] Firestore driver document exists with all fields
- [ ] Mobile API login returns 200 with driver info
- [ ] Wrong password returns 401 error
- [ ] Non-existent email returns 401 error
- [ ] Duplicate email prevented
- [ ] Web dashboard login works with driver account

## Troubleshooting

### Issue: "Invalid email or password" for correct credentials

**Solution**: Check that:
1. Email exists in Django admin → Users
2. Email exists in Firebase → Firestore → drivers
3. Email matches exactly (case-sensitive)
4. Password is correct

### Issue: Driver exists in Firebase but login fails

**Solution**: 
1. Run: `python fix_existing_drivers.py`
2. This creates missing Django user

### Issue: Can't create duplicate (good!) but error message is wrong

**Solution**: This is correct behavior! The system prevents duplicates.

### Issue: Firebase credentials not working

**Solution**:
1. Check `.env` file has correct Firebase credentials
2. Verify Firebase project is accessible
3. Check Firestore database rules allow access

## Performance Testing

### Load Time Test

```bash
time curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@fleet.com", "password": "JohnPass123!"}'
```

Expected: Response time < 1 second

### Multiple Login Attempts

Create 5 drivers and test login for each:

```bash
for i in {1..5}; do
  email="driver$i@fleet.com"
  curl -X POST http://localhost:8000/api/login/ \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$email\", \"password\": \"Pass123!\"}"
done
```

Expected: All return 200 status ✓

## Security Testing

### Test Password Hashing

```python
from django.contrib.auth.models import User

user = User.objects.get(email='john.doe@fleet.com')
print(user.password)
# Should NOT be plain text, should be hashed
```

Expected: Password starts with `pbkdf2_sha256$...` (hashed) ✓

### Test SQL Injection Prevention

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin\"; DROP TABLE users; --",
    "password": "anything"
  }'
```

Expected: 401 error, no database damage ✓

## Final Sign-off

Once all tests pass, mark as: **✓ READY FOR PRODUCTION**

Driver authentication system is fully functional and secure.

---

**Test Date**: ___________
**Tester**: ___________
**Status**: ___________
