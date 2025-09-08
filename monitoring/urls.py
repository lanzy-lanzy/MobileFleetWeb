from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),
    path('firebase-config/', views.firebase_config, name='firebase_config'),

    # Terminal Management
    path('terminals/', views.terminal_list, name='terminal_list'),
    path('terminals/create/', views.terminal_create, name='terminal_create'),
    path('terminals/<str:terminal_id>/', views.terminal_detail, name='terminal_detail'),
    path('terminals/<str:terminal_id>/edit/', views.terminal_edit, name='terminal_edit'),
    path('terminals/<str:terminal_id>/delete/', views.terminal_delete, name='terminal_delete'),

    # Driver Management
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/create/', views.driver_create, name='driver_create'),
    path('drivers/<str:driver_id>/', views.driver_detail, name='driver_detail'),
    path('drivers/<str:driver_id>/edit/', views.driver_edit, name='driver_edit'),
    path('drivers/<str:driver_id>/delete/', views.driver_delete, name='driver_delete'),

    # Trip Management
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/create/', views.trip_create, name='trip_create'),
    path('trips/<str:trip_id>/', views.trip_detail, name='trip_detail'),
    path('trips/<str:trip_id>/update-status/', views.trip_update_status, name='trip_update_status'),
]
