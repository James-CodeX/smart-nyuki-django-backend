web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn smart_nyuki_backend.wsgi:application --bind 0.0.0.0:$PORT
