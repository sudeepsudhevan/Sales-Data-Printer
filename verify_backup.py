import os
import django
from django.test import RequestFactory
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sale_printer.settings")
django.setup()

from sales.views import backup_database

def verify_backup():
    # Ensure backup dir exists or is created by view
    backup_dir = os.path.join(os.getcwd(), 'backup')
    print(f"Checking backup logic. Backup dir: {backup_dir}")
    
    # Mock Request
    factory = RequestFactory()
    request = factory.get('/backup/')
    request.META['HTTP_REFERER'] = '/' # Mock referrer
    
    # Check initial backup count
    initial_backups = len([f for f in os.listdir(backup_dir)]) if os.path.exists(backup_dir) else 0
    print(f"Initial backups: {initial_backups}")
    
    # Call View
    print("Calling backup_database view...")
    response = backup_database(request)
    
    # Check status (302 redirect expected)
    print(f"Response status: {response.status_code}")
    
    # Check if new file exists
    if not os.path.exists(backup_dir):
        print("FAILURE: Backup directory not created.")
        return
        
    final_backups = len([f for f in os.listdir(backup_dir)])
    print(f"Final backups: {final_backups}")
    
    if final_backups > initial_backups:
        print("SUCCESS: New backup file created.")
        # List the new file
        files = sorted(os.listdir(backup_dir))
        print(f"Newest file: {files[-1]}")
    else:
        print("FAILURE: No new backup file created.")

if __name__ == "__main__":
    verify_backup()
