#!/usr/bin/env python
"""
Setup script for fresh database initialization
This script will:
1. Run all migrations
2. Create default superuser
3. Display setup completion message
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle output"""
    print(f"\n📋 {description}...")
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Smart Nyuki Database...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running migrations"):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\n📝 Default superuser credentials:")
    print("   Email: amazingjimmy44@gmail.com")
    print("   Password: Amazing44.")
    print("\n🌐 You can now start the development server with:")
    print("   python manage.py runserver")
    print("\n🔗 Admin panel will be available at:")
    print("   http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main()
