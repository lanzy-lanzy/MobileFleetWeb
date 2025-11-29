# Driver CRUD Workflow Diagram & Guide

## Complete User Journey

```
START
  |
  v
┌─────────────────────────┐
│ Driver Management Page  │ (driver_list)
│   GET /drivers/         │
│                         │
│ - View all drivers      │
│ - Grid layout           │
│ - Pagination (10/page)  │
│ - Status indicators     │
└────────┬─────────────────┘
         |
    ┌────┴──────┬──────────┬─────────┐
    |           |          |         |
    v           v          v         v
  [Add]      [View]     [Edit]   [Delete]
    |           |          |         |
    v           v          v         v
    A           B          C         D
```

### Path A: CREATE NEW DRIVER

```
START
  |
  v
┌─────────────────────────────────┐
│ Click "Add Driver" button       │
│ GET /drivers/create/            │
└─────────────────────────────────┘
  |
  v
┌─────────────────────────────────┐
│ Create Form                     │
│                                 │
│ [Full Name*]        [required]  │
│ [Contact Number]    [optional]  │
│ [License Number]    [optional]  │
│                                 │
│ [Cancel] [Add Driver]           │
└────────┬──────────────┬──────────┘
         |              |
      Cancel         Submit
         |              |
         v              v
    Driver List    Validate Input
                      |
                      +─ Empty Name? ─→ Error Message
                      |                 [Show form again]
                      |
                      v
                  Firebase CREATE
                      |
                      v
            ┌─────────────────────────┐
            │ Generate driver_id      │
            │ Set created_at          │
            │ Set updated_at          │
            │ Set is_active = true    │
            │ Save to Firestore       │
            └────────┬────────────────┘
                     |
                     v
            ┌─────────────────────────┐
            │ Success Message         │
            │ "Driver created..."     │
            └────────┬────────────────┘
                     |
                     v
            Driver List (with new driver)
                     |
                     v
                   END
```

### Path B: VIEW DRIVER DETAILS

```
START
  |
  v
┌──────────────────────────┐
│ Click "View" on driver   │
│ GET /drivers/{id}/       │
└──────────────────────────┘
  |
  v
Firebase GET driver_id
  |
  v
┌──────────────────────────────────────┐
│ Driver Detail Page                   │
│                                      │
│ [Back] [Edit] [Delete]               │
│                                      │
│ Name: Juan Dela Cruz                 │
│ Status: [Active Badge]               │
│ Contact: +63 912 345 6789            │
│ License: N01-12-345678               │
│ Joined: Nov 29, 2025                 │
│                                      │
│ Trip History:                        │
│ +─────────────────────────────────+  │
│ | Trip ID | Status | Date | Pass | │
│ +─────────────────────────────────+  │
│ | ABC123  | Comp.  | ...  | 5    | │
│ +─────────────────────────────────+  │
└──────────────────────────┘
  |
  v
END
```

### Path C: UPDATE DRIVER INFO

```
START
  |
  v
┌──────────────────────────┐
│ Click "Edit" on driver   │
│ GET /drivers/{id}/edit/  │
└──────────────────────────┘
  |
  v
Firebase GET driver_id
  |
  v
┌──────────────────────────────────────┐
│ Edit Form (Pre-filled)               │
│                                      │
│ [Full Name*]        [Juan Dela Cruz] │
│ [Contact Number]    [+63 912...]     │
│ [License Number]    [N01-12-...]     │
│ [Status Toggle]     [Active ON]      │
│                                      │
│ Driver ID: xyz123 (read-only)        │
│                                      │
│ [Cancel] [Save Changes]              │
└────────┬──────────────┬──────────────┘
         |              |
      Cancel         Submit
         |              |
         v              v
    Driver Detail   Validate Input
                      |
                      +─ Empty Name? ─→ Error
                      |
                      v
                  Firebase UPDATE
                      |
                      v
            ┌────────────────────────┐
            │ Update fields          │
            │ Update updated_at      │
            │ Save to Firestore      │
            └────────┬───────────────┘
                     |
                     v
            Success Message
            "Driver updated..."
                     |
                     v
            Driver Detail Page
                     |
                     v
                   END
```

### Path D: DELETE DRIVER

```
START
  |
  v
┌─────────────────────────┐
│ Click "Delete" button   │
│ (on list or detail)     │
└──────────┬──────────────┘
           |
           v
┌──────────────────────────────────┐
│ Confirmation Modal               │
│                                  │
│ Delete Driver?                   │
│                                  │
│ "Are you sure you want to       │
│  delete Juan Dela Cruz?"        │
│                                  │
│ [Cancel] [Delete]               │
└───────┬──────────────┬───────────┘
        |              |
     Cancel         Submit
        |              |
        v              v
   Close Modal    POST /drivers/{id}/delete/
        |              |
        v              v
   Same Page      Firebase DELETE
        |              |
        |              v
        |         ┌──────────────────┐
        |         │ Remove document  │
        |         │ from Firestore   │
        |         └────────┬─────────┘
        |                  |
        v                  v
   Back to List (with driver removed)
                  |
                  v
            Success Message
            "Driver deleted..."
                  |
                  v
                 END
```

## State Diagram

```
┌──────────────┐
│  NO DRIVERS  │
│  (Empty)     │
└────────┬─────┘
         |
         | User clicks "Add First Driver"
         v
┌──────────────────┐
│ CREATE FORM      │ ◄──────┐
│ (driver_create)  │        │
└────────┬─────────┘        │
         |                  │
         | Submit with      │ Click
         | valid data       │ Cancel
         v                  │
    Validate ─────→ Error ──┘
         |
         ✓ Valid
         |
         v
    Firebase CREATE
         |
         v
┌──────────────────┐
│  DRIVER EXISTS   │
│  (in Firestore)  │
└────────┬─────────┘
         |
         | List page shown
         v
┌──────────────────┐
│  LIST VIEW       │ ◄──────────┐
│  (driver_list)   │            │
└────┬───┬───┬─────┘            │
     |   |   |                  |
   View Edit Delete ────────────┘
     |   |   |
     |   |   | (confirmation + POST)
     |   |   v
     |   |  Firebase DELETE
     |   |   |
     |   |   v
     |   |  Redirect to LIST
     |   |
     |   └──→ EDIT FORM
     |        │
     |        v
     |      Validate
     |        │
     |        ├─ Invalid ──→ Show errors
     |        │
     |        ✓ Valid
     |        │
     |        v
     |      Firebase UPDATE
     |        │
     |        v
     |      Redirect to DETAIL
     |
     └──→ DETAIL VIEW
          (driver_detail)
          │
          └─ Contains Edit & Delete
               buttons
```

## Data Flow Diagram

```
┌──────────────┐
│   Browser    │
│   (Template) │
└───────┬──────┘
        |
        | GET/POST
        v
┌──────────────────┐
│   Django View    │
│  (monitoring)    │
│  driver_create   │
│  driver_list     │
│  driver_detail   │
│  driver_edit     │
│  driver_delete   │
└───────┬──────────┘
        |
        | Call methods
        v
┌──────────────────────────┐
│  Firebase Service        │
│  (Singleton)             │
│                          │
│ - create_driver()        │
│ - get_driver()           │
│ - get_all_drivers()      │
│ - update_driver()        │
│ - delete_driver()        │
└───────┬──────────────────┘
        |
        | Firestore API
        v
┌──────────────────────────┐
│  Firebase Firestore      │
│  (Cloud Database)        │
│                          │
│ Collection: drivers      │
│   - driver_id            │
│   - name                 │
│   - contact              │
│   - license_number       │
│   - is_active            │
│   - created_at           │
│   - updated_at           │
└──────────────────────────┘
```

## Form Fields Mapping

```
CREATE FORM                UPDATE FORM
┌─────────────────┐      ┌─────────────────┐
│ name (req)      │      │ name (req)      │
│ contact (opt)   │      │ contact (opt)   │
│ license_number  │      │ license_number  │
│ (opt)           │      │ (opt)           │
│                 │      │ is_active       │
│                 │      │ (toggle)        │
│ [Cancel]        │      │ driver_id       │
│ [Add Driver]    │      │ (read-only)     │
│                 │      │                 │
│                 │      │ [Cancel]        │
│                 │      │ [Save Changes]  │
└─────────────────┘      └─────────────────┘
```

## Status Transitions

```
        ┌─────────────┐
        │   CREATE    │
        │  is_active  │
        │  = true     │
        └──────┬──────┘
               |
               v
        ┌─────────────┐
        │   ACTIVE    │ ◄───┐
        │             │     │
        │ Visible in  │     │
        │ driver list │     │
        └──────┬──────┘     │
               |            |
            [Edit]          | Toggle
            is_active       | is_active
            to false        |
               |            |
               v            |
        ┌─────────────┐     │
        │  INACTIVE   │─────┘
        │             │
        │ Hidden from │
        │ trip assign │
        └──────┬──────┘
               |
            [Delete]
               |
               v
        ┌─────────────┐
        │   DELETED   │
        │             │
        │ Removed from│
        │ Firestore   │
        └─────────────┘
```

## Timeline Example

```
Time    Action                  Firestore State
────────────────────────────────────────────────────
10:00   User clicks "Add"       -
10:01   Form submitted          created_at: 10:01
        Driver created
        
10:05   User clicks "Edit"      -
10:06   Updates contact         updated_at: 10:06
        Form submitted
        
10:10   User clicks "View"      Shows driver
        Displays details        with all fields
        
10:15   User clicks "Delete"    Confirms deletion
10:15   Confirms deletion       
        Driver removed          Document deleted
```

---

This workflow diagram provides a complete visual representation of how the Driver CRUD system works from user interaction to database operations.
