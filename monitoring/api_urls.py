"""
API URLs for Mobile App Integration
"""

from django.urls import path
from . import api_views

urlpatterns = [
    # QR Code Scanning
    path('scan-qr/', api_views.scan_qr_code, name='api_scan_qr'),
    
    # Trip Management
    path('trips/start/', api_views.start_trip, name='api_start_trip'),
    path('trips/<str:trip_id>/stop/', api_views.stop_trip, name='api_stop_trip'),
    path('trips/<str:trip_id>/passengers/', api_views.update_trip_passengers, name='api_update_passengers'),
    path('trips/<str:trip_id>/', api_views.get_trip_details, name='api_trip_details'),
    path('trips/active/', api_views.get_active_trips_api, name='api_active_trips'),
    
    # Driver Information
    path('drivers/<str:driver_id>/', api_views.get_driver_info, name='api_driver_info'),
]
