import os
import sqlite3
import configparser
from datetime import datetime

# Read config.ini to find PREFECT_HOME
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
prefect_home = config.get('Settings', 'PREFECT_HOME', fallback=r'C:\prefect\prefect_home')

# The Prefect 3.x SQLite database is always named prefect.db inside PREFECT_HOME
DB_PATH = os.path.join(prefect_home, 'prefect.db')

def query_recent_flow_runs(limit=5):
    """
    Connects directly to the Prefect SQLite database and retrieves the
    most recent flow runs, bypassing the API.
    """
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Has Prefect been started yet?")
        return

    print(f"Connecting to Prefect DB: {DB_PATH}")
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query the flow_run table
        # We join with the flow table to get the readable flow name
        import pandas as pd
        query = """
            SELECT 
                fr.id, 
                f.name as flow_name, 
                fr.name as run_name, 
                fr.state_name, 
                fr.start_time, 
                fr.end_time,
                fr.run_count
            FROM flow_run fr
            LEFT JOIN flow f ON fr.flow_id = f.id
            ORDER BY fr.expected_start_time DESC
            LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        
        print("\n--- Recent Flow Runs (via Pandas) ---")
        if df.empty:
            print("No runs found.")
        else:
            # Drop the raw ID for cleaner console display
            display_df = df.drop(columns=['id'], errors='ignore')
            # Fix timestamps visually by capping at the dot
            display_df['start_time'] = display_df['start_time'].astype(str).str.split('.').str[0].replace('None', 'Pending')
            display_df['end_time'] = display_df['end_time'].astype(str).str.split('.').str[0].replace('None', 'Active/None')
            
            print(display_df.to_string(index=False))
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Executing Native SQLite Query Script...")
    query_recent_flow_runs(limit=5)
