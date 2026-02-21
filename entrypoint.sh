#!/bin/sh

# entrypoint.sh — Runs when the Docker container starts

echo ">>> Waiting for PostgreSQL to be ready..."

while ! nc -z db 5432; do
  echo "    PostgreSQL is not ready yet... retrying in 1 second"
  sleep 1
done

echo ">>> PostgreSQL is ready!"

echo ">>> Running database migrations..."
python manage.py migrate --no-input

echo ">>> Collecting static files..."
python manage.py collectstatic --no-input

# Load data only if Customer table is empty (avoid duplicate loading on restart)
CUSTOMER_COUNT=$(python manage.py shell -c "from loans.models import Customer; print(Customer.objects.count())" 2>/dev/null)
if [ "$CUSTOMER_COUNT" = "0" ] || [ -z "$CUSTOMER_COUNT" ]; then
  echo ">>> Loading initial data from Excel files..."
  python manage.py load_data
else
  echo ">>> Data already loaded ($CUSTOMER_COUNT customers) — skipping load_data"
fi

echo ">>> Starting Django server..."
exec gunicorn credit_system.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120

