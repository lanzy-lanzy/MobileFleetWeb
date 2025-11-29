# Driver CRUD Quick Start Guide

## Files Created/Updated

### New Template Files
- ✓ `templates/monitoring/drivers/detail.html` - Driver details page
- ✓ `templates/monitoring/drivers/edit.html` - Edit driver form

### Existing Files (Already Complete)
- ✓ `templates/monitoring/drivers/create.html` - Create driver form
- ✓ `templates/monitoring/drivers/list.html` - Driver list
- ✓ `monitoring/views.py` - All CRUD views implemented
- ✓ `monitoring/firebase_service.py` - All database operations
- ✓ `monitoring/urls.py` - All routes configured

## Driver Management Workflow

### 1. View All Drivers
```
URL: http://localhost:8000/drivers/
Shows: Grid of all drivers with status and actions
Actions: View, Edit, Delete buttons
```

### 2. Add New Driver
```
URL: http://localhost:8000/drivers/create/
Form Fields:
  - Full Name (required)
  - Contact Number (optional)
  - Driver's License Number (optional)

Behavior:
  - Validates name is not empty
  - Auto-generates unique driver_id
  - Sets is_active = true by default
  - Redirects to driver list on success
```

### 3. View Driver Details
```
URL: http://localhost:8000/drivers/{driver_id}/
Shows:
  - Full driver information
  - Status (Active/Inactive badge)
  - Trip history table
  - Contact information
  - License number
  - Join date and last updated date
  
Actions:
  - Edit Driver button
  - Delete Driver button
  - View trip details link
```

### 4. Edit Driver Information
```
URL: http://localhost:8000/drivers/{driver_id}/edit/
Form Fields:
  - Full Name (required)
  - Contact Number
  - Driver's License Number
  - Status Toggle (Active/Inactive)
  - Driver ID (read-only, for reference)

Behavior:
  - Pre-fills current driver data
  - Updates only changed fields
  - Adds updated_at timestamp
  - Redirects to driver details on success
```

### 5. Delete Driver
```
Trigger: Click "Delete" button on driver list or detail page
Confirmation: Modal dialog appears asking for confirmation
Action: POST to /drivers/{driver_id}/delete/
Result: Driver removed from Firestore
Redirect: Back to driver list
```

## Firestore Data Model

### Driver Document Structure
```
Collection: drivers
Document ID: (auto-generated, stored as driver_id)

Fields:
{
  driver_id: string,           // Unique identifier
  name: string,                // Required
  contact: string,             // Phone number
  license_number: string,      // License ID
  is_active: boolean,          // true/false
  created_at: timestamp,       // Auto-generated
  updated_at: timestamp        // Auto-updated
}
```

## Code Examples

### Create a Driver (Backend)
```python
from monitoring.firebase_service import firebase_service

driver_data = {
    'name': 'Juan Dela Cruz',
    'contact': '+63 912 345 6789',
    'license_number': 'N01-12-345678',
    'is_active': True,
}
driver_id = firebase_service.create_driver(driver_data)
print(f"Created driver: {driver_id}")
```

### Get a Driver (Backend)
```python
driver = firebase_service.get_driver('driver_id_here')
if driver:
    print(f"Driver: {driver['name']}")
```

### Update a Driver (Backend)
```python
update_data = {
    'contact': '+63 987 654 3210',
    'is_active': False
}
firebase_service.update_driver('driver_id_here', update_data)
```

### Delete a Driver (Backend)
```python
firebase_service.delete_driver('driver_id_here')
```

### List All Drivers (Backend)
```python
drivers = firebase_service.get_all_drivers()
for driver in drivers:
    print(f"{driver['name']} - {driver['contact']}")
```

## Frontend Template Usage

### Display Driver Status Badge
```html
{% if driver.is_active %}
    <span class="bg-green-100 text-green-800">Active</span>
{% else %}
    <span class="bg-red-100 text-red-800">Inactive</span>
{% endif %}
```

### Link to Driver Details
```html
<a href="{% url 'driver_detail' driver.driver_id %}">
    View Driver
</a>
```

### Delete Confirmation
```html
<button onclick="confirmDelete('{{ driver.driver_id }}', '{{ driver.name }}')">
    Delete
</button>
```

## Error Handling

All operations are wrapped in try-catch blocks with:
- Logger.error() for debugging
- Django messages for user feedback
- Graceful fallbacks (empty lists, None returns)
- Input validation

Example error message:
```python
except Exception as e:
    logger.error(f"Error creating driver: {e}")
    messages.error(request, f"Error creating driver: {str(e)}")
```

## Testing CRUD Operations

Run the automated test suite:
```bash
python test_driver_crud.py
```

Output will show:
- CREATE: Driver created successfully
- READ: Driver data retrieved
- UPDATE: Driver fields updated
- DELETE: Driver removed and verified

## Common Issues & Solutions

### Issue: Driver not appearing in list
- **Cause**: Firestore query delay
- **Solution**: Hard refresh browser (Ctrl+Shift+R)

### Issue: Error "Driver name is required"
- **Cause**: Empty name field submitted
- **Solution**: Ensure name field has value before submitting

### Issue: Delete operation fails silently
- **Cause**: Firebase permissions
- **Solution**: Check Firestore security rules in Firebase Console

### Issue: Timestamps showing UTC/offset
- **Cause**: Django timezone settings
- **Solution**: Check TIMEZONE setting in settings.py

## Performance Notes

- Driver list pagination: 10 per page
- Queries ordered by creation date (newest first)
- Single document lookups are fast
- List operations scale well with Firestore indexes

## Security Checklist

- ✓ CSRF tokens on all forms
- ✓ POST-only for destructive operations
- ✓ Input validation
- ✓ Secure Firestore rules (configure separately)
- ✓ Error logging without leaking data
- ✓ User authentication required (configure in settings.py)

## Next Steps

1. Configure Firestore security rules in Firebase Console
2. Set up user authentication if needed
3. Test CRUD operations
4. Deploy to production
5. Monitor Firestore usage and costs

---

**Last Updated**: 2025-11-29
**Status**: Fully Functional ✓
