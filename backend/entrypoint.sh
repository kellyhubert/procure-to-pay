#!/bin/bash

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell -c "
from procurement.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='finance')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Start server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
