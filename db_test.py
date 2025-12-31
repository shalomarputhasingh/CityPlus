
import os
import django
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cityplus.settings')
django.setup()

try:
    conn = connections['default']
    conn.ensure_connection()
    print("Successfully connected to the database!")
except OperationalError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
