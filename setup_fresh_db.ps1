# Smart Nyuki Database Setup Script (PowerShell)
# This script will setup a fresh database with default superuser

Write-Host "🚀 Setting up Smart Nyuki Database..." -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Gray

# Check if we're in the right directory
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Error: manage.py not found. Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Run migrations
Write-Host "`n📋 Running migrations..." -ForegroundColor Yellow
try {
    $output = python manage.py migrate 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations completed successfully!" -ForegroundColor Green
        Write-Host "Output: $output" -ForegroundColor Gray
    } else {
        Write-Host "❌ Migrations failed!" -ForegroundColor Red
        Write-Host "Error: $output" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error running migrations: $_" -ForegroundColor Red
    exit 1
}

Write-Host ("`n" + "=" * 50) -ForegroundColor Gray
Write-Host "🎉 Database setup completed successfully!" -ForegroundColor Green
Write-Host "`n📝 Default superuser credentials:" -ForegroundColor Cyan
Write-Host "   Email: amazingjimmy44@gmail.com" -ForegroundColor White
Write-Host "   Password: Amazing44." -ForegroundColor White
Write-Host "`n🌐 You can now start the development server with:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host "`n🔗 Admin panel will be available at:" -ForegroundColor Cyan
Write-Host "   http://127.0.0.1:8000/admin/" -ForegroundColor White
