#!/usr/bin/env python
"""
Fix trip driver_ids to match driver records
This ensures filtering will work correctly

Run: python manage.py shell
Then: exec(open('FIX_TRIP_DRIVER_IDS.py').read())
"""

from monitoring.firebase_service import firebase_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("FIX TRIP DRIVER_IDS")
print("="*70)

# Get all drivers and create mapping
try:
    drivers = firebase_service.get_all_drivers()
    print(f"\n✅ Loaded {len(drivers)} drivers")
    
    # Create a mapping of driver names to driver_ids
    driver_map = {}
    for driver in drivers:
        driver_id = driver.get('driver_id') or driver.get('id')
        name = driver.get('name', '').lower()
        email = driver.get('email', '').lower()
        
        driver_map[name] = driver_id
        driver_map[email] = driver_id
        
        print(f"  {driver.get('name')}: {driver_id}")
    
except Exception as e:
    print(f"❌ Error loading drivers: {e}")
    exit()

# Get all trips
try:
    trips = firebase_service.get_all_trips()
    print(f"\n✅ Loaded {len(trips)} trips")
    
except Exception as e:
    print(f"❌ Error loading trips: {e}")
    exit()

# Check which trips need fixing
print(f"\n" + "="*70)
print("ANALYZING TRIPS")
print("="*70)

trips_need_fix = []
for trip in trips:
    trip_id = trip.get('id') or trip.get('trip_id')
    driver_id = trip.get('driver_id')
    
    # Check if this driver_id is not in our driver list
    is_valid = any(d.get('driver_id') == driver_id or d.get('id') == driver_id for d in drivers)
    
    if not is_valid:
        trips_need_fix.append({
            'trip_id': trip_id,
            'current_driver_id': driver_id,
            'trip_doc': trip
        })

print(f"\nTrips with invalid driver_ids: {len(trips_need_fix)}")

if trips_need_fix:
    print(f"\n⚠️  These trips have driver_ids that don't match any driver:")
    for item in trips_need_fix[:5]:
        print(f"  Trip: {item['trip_id']}")
        print(f"    Current driver_id: {item['current_driver_id']}")

# Ask user what to do
print(f"\n" + "="*70)
print("OPTIONS")
print("="*70)

print(f"""
Option 1: Use driver name from trip to find correct driver_id
Option 2: Manually specify mapping
Option 3: Just show the mismatches

What would you like to do?
""")

# For now, let's just show what needs to be fixed
print(f"\n" + "="*70)
print("WHAT TO DO")
print("="*70)

if trips_need_fix:
    print(f"""
The following trips have driver_ids that don't match:

HOW TO FIX (in Firebase Console):
1. Go to Firestore Database
2. Open 'trips' collection
3. For each trip below, update its driver_id to match a valid driver

TRIPS TO FIX:
""")
    
    for item in trips_need_fix[:10]:
        print(f"  Trip: {item['trip_id']}")
        print(f"    Change driver_id from: '{item['current_driver_id']}'")
        print(f"    To one of these valid IDs:")
        for driver in drivers[:3]:
            valid_id = driver.get('driver_id') or driver.get('id')
            driver_name = driver.get('name')
            print(f"      - '{valid_id}' ({driver_name})")
        print()

else:
    print(f"✅ All trips have valid driver_ids!")
    print(f"   Filtering should work correctly.")

print("="*70 + "\n")
