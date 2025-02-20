import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime
from src.utility_functions import load_config, get_root

def db_to_csv():
    """Export SQLite database to CSV file"""
    # Load configuration
    config = load_config()
    root = get_root()
    
    # Get database path from config
    db_path = Path(root) / config.get("db_filepath")
    
    # Create csv directory if it doesn't exist
    csv_dir = root / "data" / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = csv_dir / f"profiles_export_{timestamp}.csv"
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get column names
        cursor.execute("PRAGMA table_info(profiles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get all data from profiles table
        cursor.execute("SELECT * FROM profiles")
        rows = cursor.fetchall()
        
        # Write to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            # Write header
            writer.writerow(columns)
            # Write data rows
            writer.writerows(rows)
            
        print(f"Successfully exported {len(rows)} records to {csv_path}")
        
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    db_to_csv()
