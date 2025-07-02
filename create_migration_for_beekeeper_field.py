#!/usr/bin/env python
"""
Script to create migration for adding beekeeper field to SmartDevices model
Run this script after making the model changes to generate the migration file.
"""

import subprocess
import sys

def create_migration():
    """Create migration for the beekeeper field addition"""
    try:
        # Create migration
        result = subprocess.run(
            ['python', 'manage.py', 'makemigrations', 'devices'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Migration created successfully!")
            print(f"Output: {result.stdout}")
        else:
            print(f"❌ Error creating migration: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("Creating migration for beekeeper field...")
    if create_migration():
        print("\n📝 Next steps:")
        print("1. Review the generated migration file")
        print("2. Run: python manage.py migrate")
        print("3. Update existing devices to have a beekeeper assigned")
        print("4. Run: python manage.py sync_hive_smart_device_status")
    else:
        sys.exit(1)
