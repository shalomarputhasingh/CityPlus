
import os
import dj_database_url
from django.db.backends.postgresql.base import DatabaseWrapper
import psycopg2
import sys

# Define regions to test
regions = [
    'ap-south-1', 
    'ap-southeast-1', 
    'us-east-1', 
    'eu-central-1', 
    'us-west-1', 
    'sa-east-1'
]

password = "Dhanush2710202"
project_ref = "dapxfzmrcoqofrnrrczb"
db_name = "postgres"

for region in regions:
    host = f"aws-0-{region}.pooler.supabase.com"
    conn_str = f"postgres://postgres.{project_ref}:{password}@{host}:5432/{db_name}"
    
    print(f"Testing region: {region} ({host})...")
    try:
        conn = psycopg2.connect(conn_str)
        print(f"SUCCESS! Connected to {region}")
        conn.close()
        break
    except Exception as e:
        print(f"Failed {region}: {e}")
