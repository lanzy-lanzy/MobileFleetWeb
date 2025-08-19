from django.core.management.base import BaseCommand
from monitoring.firebase_service import firebase_service
from datetime import datetime

class Command(BaseCommand):
    help = 'Test Firebase Firestore connection and operations'

    def handle(self, *args, **options):
        self.stdout.write("🔥 Testing Firebase Connection...")
        self.stdout.write("=" * 50)

        try:
            # Test Firebase initialization
            self.stdout.write("1. Testing Firebase initialization...")
            if firebase_service.db is None:
                self.stdout.write(self.style.ERROR("❌ Firebase initialization failed!"))
                return
            self.stdout.write(self.style.SUCCESS("✅ Firebase initialized successfully!"))

            # Test terminal operations
            self.stdout.write("\n2. Testing terminal operations...")
            test_terminal = {
                'name': 'Test Terminal - Management Command',
                'latitude': 8.1234,
                'longitude': 123.5678,
                'is_active': True,
            }

            terminal_id = firebase_service.create_terminal(test_terminal)
            if terminal_id:
                self.stdout.write(self.style.SUCCESS(f"✅ Terminal created! ID: {terminal_id}"))

                # Test retrieval
                terminal = firebase_service.get_terminal(terminal_id)
                if terminal:
                    self.stdout.write(self.style.SUCCESS(f"✅ Terminal retrieved: {terminal['name']}"))

                # Clean up
                firebase_service.delete_terminal(terminal_id)
                self.stdout.write(self.style.SUCCESS("✅ Terminal cleaned up"))

            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("🎉 Firebase is working correctly!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))