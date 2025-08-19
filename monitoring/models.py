from django.db import models
from django.utils import timezone

# These models are optional for local caching since we're using Firebase as primary storage

class Terminal(models.Model):
    """Local cache model for terminals (optional)"""
    terminal_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    qr_code_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Driver(models.Model):
    """Local cache model for drivers (optional)"""
    driver_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Trip(models.Model):
    """Local cache model for trips (optional)"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    trip_id = models.CharField(max_length=100, unique=True)
    driver_id = models.CharField(max_length=100)
    start_terminal = models.CharField(max_length=100)
    destination_terminal = models.CharField(max_length=100)
    passengers = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trip {self.trip_id} - {self.status}"

    @property
    def travel_duration(self):
        """Calculate travel duration if both start and arrival times are set"""
        if self.start_time and self.arrival_time:
            return self.arrival_time - self.start_time
        return None

    class Meta:
        ordering = ['-created_at']
