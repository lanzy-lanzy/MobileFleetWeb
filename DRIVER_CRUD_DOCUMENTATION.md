# Driver CRUD Operations Documentation

## Overview
Complete CRUD (Create, Read, Update, Delete) functionality for managing drivers using Firebase Firestore database.

## Architecture

### Backend Components

#### 1. **Firebase Service** (`monitoring/firebase_service.py`)
Singleton service class that handles all Firestore operations.

**Create Driver**
```python
def create_driver(self, driver_data):
    """Create a new driver in Firestore"""
    # Adds created_at and updated_at timestamps
    # Generates unique driver_id
    # Returns driver_id on success
```

**Read Driver**
```python
def get_driver(self, driver_id):
    """Get a driver by ID"""
    # Returns driver data dictionary or None

def get_all_drivers(self):
    """Get all drivers"""
    # Returns list of all driver documents
```

**Update Driver**
```python
def update_driver(self, driver_id, update_data):
    """Update a driver"""
    # Updates specified fields
    # Adds updated_at timestamp
    # Returns True/False
```

**Delete Driver**
```python
def delete_driver(self, driver_id):
    """Delete a driver"""
    # Removes driver document from Firestore
    # Returns True/False
```

#### 2. **Views** (`monitoring/views.py`)

**driver_list** - List all drivers
- URL: `/drivers/`
- Method: GET
- Features: Pagination (10 drivers per page)

**driver_create** - Create new driver
- URL: `/drivers/create/`
- Method: GET/POST
- Fields: name (required), contact, license_number
- Redirects to: `driver_list` on success

**driver_detail** - View driver details
- URL: `/drivers/<driver_id>/`
- Method: GET
- Features: Displays driver info and trip history

**driver_edit** - Edit driver information
- URL: `/drivers/<driver_id>/edit/`
- Method: GET/POST
- Fields: name (required), contact, license_number, is_active

**driver_delete** - Delete driver
- URL: `/drivers/<driver_id>/delete/`
- Method: POST
- Features: Deletes driver and redirects to list

#### 3. **Templates**

**list.html** - Driver list with grid layout
- Displays all drivers in 4-column grid
- Shows: Name, Contact, License, Join date, Status
- Actions: View, Edit, Delete
- Empty state handling

**create.html** - Add new driver form
- Form fields for driver information
- Validation messages
- Responsive design with Tailwind CSS

**detail.html** - Driver details page
- Full driver information
- Trip history table
- Quick action buttons
- Status badge

**edit.html** - Edit driver form
- Pre-filled form fields
- Status toggle
- Driver ID display (read-only)
- Update button

#### 4. **URL Routing** (`monitoring/urls.py`)

```python
# Driver Management
path('drivers/', views.driver_list, name='driver_list')
path('drivers/create/', views.driver_create, name='driver_create')
path('drivers/<str:driver_id>/', views.driver_detail, name='driver_detail')
path('drivers/<str:driver_id>/edit/', views.driver_edit, name='driver_edit')
path('drivers/<str:driver_id>/delete/', views.driver_delete, name='driver_delete')
```

## Firestore Data Structure

### Collection: `drivers`

```json
{
  "driver_id": "unique-identifier",
  "name": "Juan Dela Cruz",
  "contact": "+63 912 345 6789",
  "license_number": "N01-12-345678",
  "is_active": true,
  "created_at": "2025-11-29T14:42:31.246616+00:00",
  "updated_at": "2025-11-29T14:42:31.246616+00:00"
}
```

## API Endpoints

### Create Driver
```
POST /drivers/create/
Content-Type: application/x-www-form-urlencoded

name=Juan Dela Cruz
contact=+63 912 345 6789
license_number=N01-12-345678

Response: Redirect to driver_list on success
```

### List Drivers
```
GET /drivers/?page=1

Response: HTML page with paginated driver list
```

### View Driver Details
```
GET /drivers/{driver_id}/

Response: HTML page with driver details and trip history
```

### Update Driver
```
POST /drivers/{driver_id}/edit/
Content-Type: application/x-www-form-urlencoded

name=Updated Name
contact=+63 987 654 3210
license_number=N02-34-567890
is_active=on

Response: Redirect to driver_detail on success
```

### Delete Driver
```
POST /drivers/{driver_id}/delete/

Response: Redirect to driver_list after deletion
```

## Error Handling

All operations include:
- Try-catch exception handling
- Logging for debugging
- User-friendly error messages via Django messages framework
- Fallback to empty lists on Firestore errors
- Validation of required fields

## Testing

Run the test suite:
```bash
python test_driver_crud.py
```

### Test Coverage
- ✓ Create driver
- ✓ Read driver (single and all)
- ✓ Update driver
- ✓ Delete driver
- ✓ List drivers
- ✓ Data persistence verification

## Security

- CSRF protection via Django templates
- POST-only deletion endpoint
- Input validation on create/update
- Error logging without exposing sensitive data
- Firestore security rules (configure in Firebase Console)

## Features

### Frontend
- Responsive Tailwind CSS styling
- Form validation with real-time feedback
- Pagination support
- Modal confirmation for delete operations
- Status indicators (Active/Inactive)
- Icon-based UI elements

### Backend
- Automatic timestamp management
- Unique driver ID generation
- Singleton Firebase service
- Transaction support via Firestore
- Comprehensive error logging

## Related Models

- **Trip**: Driver has many trips
- **Terminal**: Driver picks up/drops off at terminals

## Future Enhancements

1. Bulk operations (import/export)
2. Advanced filtering (by status, join date)
3. Driver rating/performance metrics
4. Document/certification uploads
5. Scheduled maintenance tracking
