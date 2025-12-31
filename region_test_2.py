
import psycopg2
import sys

# Additional regions to test
regions = [
    'eu-west-1', 
    'eu-west-2', 
    'eu-west-3', 
    'ap-northeast-1', 
    'ap-northeast-2',
    'ca-central-1',
    'af-south-1' 
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
