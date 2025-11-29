"""
Fetch and display all driver information from Firebase Firestore
Shows complete driver details for management purposes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MobileFleet.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from monitoring.firebase_service import firebase_service
from datetime import datetime

def fetch_all_drivers():
    """Fetch all drivers from Firestore and display details"""
    try:
        drivers = firebase_service.get_all_drivers()
        
        if not drivers:
            print("\n[INFO] No drivers found in the system.")
            return
        
        print("\n" + "="*100)
        print("DRIVER MANAGEMENT SYSTEM - COMPLETE DRIVER DETAILS")
        print("="*100)
        
        # Prepare data for table display
        table_data = []
        for idx, driver in enumerate(drivers, 1):
            driver_id = driver.get('driver_id', driver.get('id', 'N/A'))[:8]
            table_data.append([
                idx,
                driver.get('name', 'N/A'),
                driver_id,
                driver.get('contact', 'N/A'),
                driver.get('license_number', 'N/A'),
                'Active' if driver.get('is_active', False) else 'Inactive',
                driver.get('created_at', 'N/A'),
            ])
        
        # Display table
        headers = ['#', 'Name', 'Driver ID', 'Contact', 'License', 'Status', 'Created At']
        col_widths = [3, 20, 10, 20, 15, 10, 20]
        
        # Print header
        header_str = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
        print(header_str)
        print("-" * len(header_str))
        
        # Print rows
        for row in table_data:
            row_str = " | ".join(f"{str(cell):<{w}}" for cell, w in zip(row, col_widths))
            print(row_str)
        
        # Display detailed information
        print("\n" + "="*100)
        print("DETAILED DRIVER INFORMATION")
        print("="*100)
        
        for idx, driver in enumerate(drivers, 1):
            driver_id = driver.get('driver_id', driver.get('id'))
            print(f"\n{idx}. {driver.get('name', 'Unknown Driver')}")
            print("-" * 100)
            print(f"   Driver ID:          {driver_id}")
            print(f"   Full Name:          {driver.get('name', 'N/A')}")
            print(f"   Contact Number:     {driver.get('contact', 'Not provided')}")
            print(f"   License Number:     {driver.get('license_number', 'Not provided')}")
            print(f"   Status:             {'Active' if driver.get('is_active', False) else 'Inactive'}")
            print(f"   Created Date:       {driver.get('created_at', 'N/A')}")
            print(f"   Last Updated:       {driver.get('updated_at', 'N/A')}")
            
            # Get driver trips
            try:
                trips = firebase_service.get_trips_by_driver(driver_id)
                print(f"   Total Trips:        {len(trips)}")
                if trips:
                    active_trips = [t for t in trips if t.get('status') == 'in_progress']
                    completed_trips = [t for t in trips if t.get('status') == 'completed']
                    print(f"   - Active Trips:     {len(active_trips)}")
                    print(f"   - Completed Trips:  {len(completed_trips)}")
            except:
                print(f"   Total Trips:        Unable to fetch")
        
        # Summary statistics
        print("\n" + "="*100)
        print("SUMMARY STATISTICS")
        print("="*100)
        active_drivers = [d for d in drivers if d.get('is_active', False)]
        inactive_drivers = [d for d in drivers if not d.get('is_active', False)]
        
        print(f"\nTotal Drivers:          {len(drivers)}")
        print(f"Active Drivers:         {len(active_drivers)}")
        print(f"Inactive Drivers:       {len(inactive_drivers)}")
        print(f"Active Rate:            {(len(active_drivers)/len(drivers)*100):.1f}%")
        
        # Export option
        print("\n" + "="*100)
        print("NOTES:")
        print("="*100)
        print("""
NOTE: Driver credentials/login information
  - Currently, drivers do NOT have login credentials stored in the system
  - This is a fleet management system (Admin panel)
  - For driver app authentication, Firebase Authentication is used separately
  - Driver contact numbers are for manual communication
  
To View Individual Driver:
  - Go to: http://localhost:8000/drivers/{driver_id}/
  - Or click 'View' button on driver list
  
To Edit Driver Information:
  - Click 'Edit' button on driver detail page
  - Or go to: http://localhost:8000/drivers/{driver_id}/edit/
  
To Create New Driver:
  - Go to: http://localhost:8000/drivers/create/
  - Or click 'Add Driver' button on driver list
  
To Delete Driver:
  - Click 'Delete' button on driver list or detail page
  - Confirm deletion in popup modal
        """)
        
        return drivers
        
    except Exception as e:
        print(f"\n[ERROR] Failed to fetch drivers: {e}")
        import traceback
        traceback.print_exc()
        return None

def fetch_driver_by_id(driver_id):
    """Fetch specific driver by ID"""
    try:
        driver = firebase_service.get_driver(driver_id)
        
        if not driver:
            print(f"\n[ERROR] Driver with ID '{driver_id}' not found.")
            return None
        
        print("\n" + "="*80)
        print(f"DRIVER DETAILS: {driver.get('name', 'Unknown')}")
        print("="*80)
        
        print(f"\nDriver ID:              {driver_id}")
        print(f"Full Name:              {driver.get('name', 'N/A')}")
        print(f"Contact Number:         {driver.get('contact', 'Not provided')}")
        print(f"License Number:         {driver.get('license_number', 'Not provided')}")
        print(f"Status:                 {'Active' if driver.get('is_active', False) else 'Inactive'}")
        print(f"Created Date:           {driver.get('created_at', 'N/A')}")
        print(f"Last Updated:           {driver.get('updated_at', 'N/A')}")
        
        # Get trips
        trips = firebase_service.get_trips_by_driver(driver_id)
        print(f"\nTrips Information:")
        print(f"  Total Trips:           {len(trips)}")
        
        if trips:
            print("\n  Recent Trips (last 10):")
            for trip in trips[:10]:  # Show last 10 trips
                print(f"    - Trip {trip.get('trip_id', 'N/A')[:8]} | Status: {trip.get('status', 'N/A')} | Passengers: {trip.get('passengers', 0)}")
        
        return driver
        
    except Exception as e:
        print(f"\n[ERROR] Failed to fetch driver: {e}")
        return None

def export_drivers_csv():
    """Export all drivers to CSV file"""
    try:
        import csv
        drivers = firebase_service.get_all_drivers()
        
        if not drivers:
            print("\n[INFO] No drivers to export.")
            return
        
        filename = 'drivers_export.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Driver ID', 'Contact', 'License Number', 'Status', 'Created At', 'Updated At']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for driver in drivers:
                writer.writerow({
                    'Name': driver.get('name', ''),
                    'Driver ID': driver.get('driver_id', driver.get('id', '')),
                    'Contact': driver.get('contact', ''),
                    'License Number': driver.get('license_number', ''),
                    'Status': 'Active' if driver.get('is_active', False) else 'Inactive',
                    'Created At': driver.get('created_at', ''),
                    'Updated At': driver.get('updated_at', ''),
                })
        
        print(f"\n[SUCCESS] Drivers exported to '{filename}'")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to export drivers: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'export':
            export_drivers_csv()
        else:
            fetch_driver_by_id(sys.argv[1])
    else:
        fetch_all_drivers()
