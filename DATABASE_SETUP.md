# Database Setup Guide

This guide explains how to set up a fresh database for the Smart Nyuki Django backend.

## Automatic Setup (Recommended)

### Option 1: Using Python Script
```bash
python setup_fresh_db.py
```

### Option 2: Using PowerShell Script (Windows)
```powershell
.\setup_fresh_db.ps1
```

Both scripts will:
1. Run all database migrations
2. Automatically create a default superuser
3. Display setup completion information

## Manual Setup

If you prefer to set up the database manually:

### 1. Run Migrations
```bash
python manage.py migrate
```

### 2. Verify Superuser Creation
The superuser should be automatically created during migrations. You can verify with:
```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists:', User.objects.filter(email='amazingjimmy44@gmail.com').exists())"
```

### 3. Alternative: Create Superuser Manually
If needed, you can also create the superuser using the management command:
```bash
python manage.py create_default_superuser
```

Or force update an existing one:
```bash
python manage.py create_default_superuser --force
```

## Default Superuser Credentials

After setup, you can access the admin panel with these credentials:

- **Email**: `amazingjimmy44@gmail.com`
- **Password**: `Amazing44.`
- **Admin URL**: http://127.0.0.1:8000/admin/

## How It Works

The automatic superuser creation is implemented through:

1. **Data Migration**: `accounts/migrations/0003_auto_20250703_1242.py`
   - Automatically runs when you execute `python manage.py migrate`
   - Creates the superuser if it doesn't already exist
   - Safe to run multiple times (won't create duplicates)

2. **Management Command**: `accounts/management/commands/create_default_superuser.py`
   - Provides manual control over superuser creation
   - Supports `--force` flag to update existing users
   - Useful for development and testing

## Database Configuration

The system works with any database backend supported by Django:
- SQLite (default for development)
- PostgreSQL (recommended for production)
- MySQL
- Oracle

The superuser creation process is database-agnostic and will work with any configured backend.

## Security Notes

- The default credentials are intended for development only
- Change the superuser password before deploying to production
- Consider using environment variables for production credentials
- The migration checks for existing users to prevent duplicates

## Troubleshooting

### Migration Issues
If you encounter migration issues:
```bash
# Check migration status
python manage.py showmigrations

# Reset migrations (careful - this will lose data)
python manage.py migrate accounts zero
python manage.py migrate accounts
```

### Superuser Already Exists
If you get an error about the superuser already existing:
```bash
# Force update the existing superuser
python manage.py create_default_superuser --force
```

### Database Connection Issues
Ensure your database is properly configured in `settings.py` and accessible before running migrations.
