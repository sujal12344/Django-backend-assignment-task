"""
One-time script to drop all Django tables from PostgreSQL.
Run this ONCE before running fresh migrations.
Usage: python reset_db.py
"""

import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "credit_system.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

# Tables to drop (in correct order to avoid FK constraint errors)
TABLES_TO_DROP = [
    "loans_loan",
    "loans_customer",
    "django_admin_log",
    "authtoken_token",
    "auth_user_groups",
    "auth_user_user_permissions",
    "auth_user",
    "auth_permission",
    "auth_group_permissions",
    "auth_group",
    "django_content_type",
    "django_session",
    "django_migrations",
]

with connection.cursor() as cursor:
    print("Dropping all tables from PostgreSQL...\n")
    cursor.execute("SET session_replication_role = replica;")  # Disable FK checks

    for table in TABLES_TO_DROP:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
            print(f"  ✓ Dropped: {table}")
        except Exception as e:
            print(f"  ✗ Failed: {table} → {e}")

    cursor.execute("SET session_replication_role = DEFAULT;")  # Re-enable FK checks

print("\nAll tables dropped. Now run:")
print("  python manage.py makemigrations")
print("  python manage.py migrate")
print("  python manage.py load_data")
