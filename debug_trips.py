#!/usr/bin/env python3
"""
Debug script to check trip data and passenger tracking in Firebase
This will help identify why passenger counts aren't being reflected properly
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

def debug_trips():
    """Debug trip data in Firebase"""
    
    # Initialize Firebase (adjust the path to your service account key)
    try:
        # If already initialized, get the existing app
        app = firebase_admin.get_app()
    except ValueError:
        # Initialize if not already done
        cred = credentials.Certificate("mobile_fleet_services.json")
        app = firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    print("🔍 Debugging Trip Data in Firebase")
    print("=" * 50)
    
    try:
        # Get all trips
        trips_ref = db.collection('trips')
        trips = trips_ref.stream()
        
        trip_count = 0
        in_progress_count = 0
        completed_count = 0
        cancelled_count = 0
        total_passengers = 0
        
        print("\n📋 TRIP DETAILS:")
        print("-" * 50)
        
        for trip_doc in trips:
            trip_count += 1
            trip_data = trip_doc.to_dict()
            trip_id = trip_doc.id
            
            status = trip_data.get('status', 'unknown')
            passengers = trip_data.get('passengers', 0)
            driver_id = trip_data.get('driver_id', 'unknown')
            start_terminal = trip_data.get('start_terminal', 'unknown')
            destination_terminal = trip_data.get('destination_terminal', 'unknown')
            start_time = trip_data.get('start_time')
            arrival_time = trip_data.get('arrival_time')
            created_at = trip_data.get('created_at')
            updated_at = trip_data.get('updated_at')
            
            # Count by status
            if status == 'in_progress':
                in_progress_count += 1
            elif status == 'completed':
                completed_count += 1
            elif status == 'cancelled':
                cancelled_count += 1
            
            total_passengers += passengers
            
            print(f"\n{trip_count}. Trip ID: {trip_id}")
            print(f"   Status: {status}")
            print(f"   Passengers: {passengers}")
            print(f"   Driver ID: {driver_id}")
            print(f"   Start Terminal: {start_terminal}")
            print(f"   Destination Terminal: {destination_terminal}")
            print(f"   Start Time: {start_time}")
            print(f"   Arrival Time: {arrival_time}")
            print(f"   Created: {created_at}")
            print(f"   Updated: {updated_at}")
            
            # Show all fields for debugging
            print(f"   All fields: {list(trip_data.keys())}")
            
            # Show raw data for first few trips
            if trip_count <= 3:
                print(f"   Raw data: {json.dumps(trip_data, indent=2, default=str)}")
        
        print(f"\n" + "=" * 50)
        print(f"📊 TRIP SUMMARY:")
        print(f"   Total trips: {trip_count}")
        print(f"   In Progress: {in_progress_count}")
        print(f"   Completed: {completed_count}")
        print(f"   Cancelled: {cancelled_count}")
        print(f"   Total passengers across all trips: {total_passengers}")
        
        # Check for recent updates
        print(f"\n🕒 RECENT ACTIVITY:")
        print("-" * 30)
        
        # Get trips ordered by updated_at
        recent_trips = trips_ref.order_by('updated_at', direction=firestore.Query.DESCENDING).limit(5).stream()
        
        for i, trip_doc in enumerate(recent_trips, 1):
            trip_data = trip_doc.to_dict()
            updated_at = trip_data.get('updated_at')
            status = trip_data.get('status')
            passengers = trip_data.get('passengers', 0)
            
            print(f"{i}. Trip {trip_doc.id[:8]}... - {status} - {passengers} passengers")
            print(f"   Last updated: {updated_at}")
        
        # Test dashboard data retrieval
        print(f"\n🎯 DASHBOARD DATA TEST:")
        print("-" * 30)
        
        # Simulate what the dashboard does
        active_trips = trips_ref.where('status', '==', 'in_progress').stream()
        completed_trips = trips_ref.where('status', '==', 'completed').stream()
        
        active_list = list(active_trips)
        completed_list = list(completed_trips)
        
        print(f"Active trips query result: {len(active_list)} trips")
        print(f"Completed trips query result: {len(completed_list)} trips")
        
        # Check if there are any trips with missing passenger data
        print(f"\n⚠️  DATA VALIDATION:")
        print("-" * 30)
        
        trips_missing_passengers = 0
        trips_with_zero_passengers = 0
        
        all_trips = trips_ref.stream()
        for trip_doc in all_trips:
            trip_data = trip_doc.to_dict()
            passengers = trip_data.get('passengers')
            
            if passengers is None:
                trips_missing_passengers += 1
                print(f"❌ Trip {trip_doc.id} missing 'passengers' field")
            elif passengers == 0:
                trips_with_zero_passengers += 1
                print(f"⚠️  Trip {trip_doc.id} has 0 passengers")
        
        print(f"\nTrips missing passenger field: {trips_missing_passengers}")
        print(f"Trips with zero passengers: {trips_with_zero_passengers}")
        
        if trips_missing_passengers > 0 or trips_with_zero_passengers > 0:
            print(f"\n💡 RECOMMENDATIONS:")
            if trips_missing_passengers > 0:
                print(f"   - Some trips are missing the 'passengers' field")
                print(f"   - This could cause dashboard counting issues")
            if trips_with_zero_passengers > 0:
                print(f"   - Some trips have 0 passengers")
                print(f"   - Check if this is intentional or a data entry issue")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Make sure you have:")
        print(f"1. Correct Firebase credentials")
        print(f"2. Firebase Admin SDK installed: pip install firebase-admin")
        print(f"3. Proper service account key file path")

if __name__ == "__main__":
    debug_trips()
