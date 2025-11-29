#!/usr/bin/env python
"""
Debug script to find driver_id mismatches
Run: python manage.py shell < DEBUG_DRIVER_IDS.py
"""

from monitoring.firebase_service import firebase_service

print("\n" + "="*70)
print("DRIVER ID MISMATCH DIAGNOSTIC")
print("="*70)

# Get all drivers
try:
    drivers = firebase_service.get_all_drivers()
    print(f"\n✅ Found {len(drivers)} drivers in Firebase:")
    print("-" * 70)
    
    for driver in drivers[:10]:  # Show first 10
        driver_id = driver.get('driver_id') or driver.get('id')
        name = driver.get('name', 'Unknown')
        email = driver.get('email', 'No email')
        print(f"\nDriver: {name}")
        print(f"  Email: {email}")
        print(f"  driver_id: {driver_id}")
        
except Exception as e:
    print(f"\n❌ Error loading drivers: {e}")
    drivers = []

# Get all trips
try:
    trips = firebase_service.get_all_trips()
    print(f"\n\n✅ Found {len(trips)} trips in Firebase:")
    print("-" * 70)
    
    # Group trips by driver_id
    trips_by_driver = {}
    for trip in trips:
        trip_driver_id = trip.get('driver_id')
        if trip_driver_id not in trips_by_driver:
            trips_by_driver[trip_driver_id] = 0
        trips_by_driver[trip_driver_id] += 1
    
    # Show unique driver IDs in trips
    print(f"\nUnique driver_ids in trips: {len(trips_by_driver)}")
    for trip_driver_id, count in sorted(trips_by_driver.items(), key=lambda x: x[1], reverse=True):
        print(f"  '{trip_driver_id}': {count} trips")
        
except Exception as e:
    print(f"\n❌ Error loading trips: {e}")
    trips = []

# Now find MISMATCHES
print("\n\n" + "="*70)
print("CHECKING FOR MISMATCHES")
print("="*70)

driver_ids = set(d.get('driver_id') or d.get('id') for d in drivers)
trip_driver_ids = set(t.get('driver_id') for t in trips if t.get('driver_id'))

print(f"\nDriver record IDs: {driver_ids}")
print(f"Trip record IDs:   {trip_driver_ids}")

# Find mismatches
missing_from_drivers = trip_driver_ids - driver_ids
missing_from_trips = driver_ids - trip_driver_ids

if missing_from_drivers:
    print(f"\n❌ MISMATCH: These driver_ids are in TRIPS but NOT in DRIVERS:")
    for driver_id in missing_from_drivers:
        count = trips_by_driver.get(driver_id, 0)
        print(f"   '{driver_id}' ({count} trips)")
else:
    print(f"\n✅ All trip driver_ids exist in driver records")

if missing_from_trips:
    print(f"\n⚠️  WARNING: These driver_ids are in DRIVERS but NOT in any trip:")
    for driver_id in missing_from_trips:
        driver_name = next((d.get('name') for d in drivers if (d.get('driver_id') or d.get('id')) == driver_id), 'Unknown')
        print(f"   '{driver_id}' ({driver_name})")
else:
    print(f"\n✅ All drivers have at least one trip")

# Find matching issues
print(f"\n\n" + "="*70)
print("MATCHING ANALYSIS")
print("="*70)

for driver in drivers[:5]:  # Check first 5 drivers
    driver_id = driver.get('driver_id') or driver.get('id')
    name = driver.get('name')
    
    # Find trips for this driver
    matching_trips = [t for t in trips if t.get('driver_id') == driver_id]
    
    print(f"\nDriver: {name}")
    print(f"  ID: '{driver_id}'")
    print(f"  Matching trips: {len(matching_trips)}")
    
    if not matching_trips:
        print(f"  ⚠️  NO TRIPS FOUND FOR THIS DRIVER!")
        # Try to find similar IDs
        similar = [t.get('driver_id') for t in trips if driver_id.lower() in str(t.get('driver_id', '')).lower()]
        if similar:
            print(f"     Similar IDs in trips: {set(similar)}")

print("\n\n" + "="*70)
print("SOLUTION")
print("="*70)

if missing_from_drivers:
    print("\n❌ THE PROBLEM:")
    print("   The trips have driver_ids that don't exist in the drivers collection.")
    print("\n✅ TO FIX:")
    print("   1. Update trip records to use correct driver_id values")
    print("   2. Or update driver records to have the IDs that trips reference")
    print("   3. Ensure one-to-one mapping between driver.driver_id and trip.driver_id")
    
    print("\n📝 COMMAND TO FIX (in Firebase Console):")
    print("   For each trip with incorrect driver_id, update it to match a driver record")
else:
    print("\n✅ Driver IDs match correctly!")
    print("   The filtering should work.")
    print("   If it still doesn't work, check:")
    print("   1. Console logs (F12)")
    print("   2. JavaScript filter logic")
    print("   3. Firebase connection")

print("\n" + "="*70 + "\n")
