import psycopg
from psycopg import sql
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    # Database configuration from environment variables
    dbname = os.getenv("DB_NAME", "healthcare_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")

    # Connect to default postgres database to create the new one
    try:
        # Initialize connection using psycopg
        conn = psycopg.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port,
            autocommit=True
        )
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (dbname,))
        exists = cur.fetchone()
        if not exists:
            # psycopg v3 CREATE DATABASE needs to be handled carefully
            cur.execute(f"CREATE DATABASE {dbname}")
            print(f"Database {dbname} created successfully.")
        else:
            print(f"Database {dbname} already exists.")
            
        cur.close()
        conn.close()

        # Connect to the new database and run schema
        conn = psycopg.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cur = conn.cursor()
        
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
            cur.execute(schema_sql)
            
        conn.commit()
        print("Schema applied successfully.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        print("\nPlease ensure PostgreSQL is running and credentials in setup_db.py are correct.")

if __name__ == "__main__":
    setup_database()
