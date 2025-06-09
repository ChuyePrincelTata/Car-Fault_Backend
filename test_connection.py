import psycopg2
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("Error: DATABASE_URL environment variable not set")
    sys.exit(1)

print(f"Attempting to connect to database...")

try:
    # Parse the connection string
    conn_parts = db_url.replace("postgresql://", "").split("@")
    auth = conn_parts[0].split(":")
    host_port_db = conn_parts[1].split("/")
    host_port = host_port_db[0].split(":")
    
    username = auth[0]
    password = auth[1]
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    dbname = host_port_db[1]
    
    # Connect to the database
    conn = psycopg2.connect(
        dbname=dbname,
        user=username,
        password=password,
        host=host,
        port=port
    )
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute("SELECT version();")
    
    # Fetch the result
    version = cur.fetchone()
    print(f"Successfully connected to PostgreSQL database!")
    print(f"PostgreSQL version: {version[0]}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)
