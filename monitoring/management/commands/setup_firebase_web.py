"""
Management command to help set up Firebase web configuration
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import json


class Command(BaseCommand):
    help = 'Display Firebase web configuration setup instructions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Firebase Web Configuration Setup'))
        self.stdout.write('=' * 50)
        
        self.stdout.write(f'\nProject ID: {settings.FIREBASE_PROJECT_ID}')
        
        self.stdout.write('\n📋 To get your Firebase web configuration:')
        self.stdout.write('1. Go to Firebase Console: https://console.firebase.google.com/')
        self.stdout.write(f'2. Select your project: {settings.FIREBASE_PROJECT_ID}')
        self.stdout.write('3. Click the gear icon (Project Settings)')
        self.stdout.write('4. Scroll down to "Your apps" section')
        self.stdout.write('5. If you don\'t have a web app, click "Add app" and select Web')
        self.stdout.write('6. Copy the config object from the Firebase SDK snippet')
        
        self.stdout.write('\n🔧 Current configuration in views.py:')
        current_config = {
            'apiKey': 'AIzaSyBvOoM5xgOJYhZlXQZ8fJ9X2nY3kL4mP6Q',
            'authDomain': f'{settings.FIREBASE_PROJECT_ID}.firebaseapp.com',
            'projectId': settings.FIREBASE_PROJECT_ID,
            'storageBucket': f'{settings.FIREBASE_PROJECT_ID}.appspot.com',
            'messagingSenderId': '123456789012',
            'appId': '1:123456789012:web:abcdef123456789012345678'
        }
        
        self.stdout.write(json.dumps(current_config, indent=2))
        
        self.stdout.write('\n⚠️  Note: The apiKey, messagingSenderId, and appId are placeholders.')
        self.stdout.write('Replace them with actual values from Firebase Console.')
        
        self.stdout.write('\n🚀 For testing purposes, you can also use the current configuration')
        self.stdout.write('as Firestore security rules may allow read access.')
        
        self.stdout.write('\n✅ Once configured, the dashboard will show real-time data from:')
        self.stdout.write('- Mobile app trip starts')
        self.stdout.write('- Passenger count updates')
        self.stdout.write('- Trip completions')
        self.stdout.write('- Live statistics')
