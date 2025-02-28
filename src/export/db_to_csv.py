import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime
from src.utility_functions import load_config, get_root
from src.export.columns_for_export import export_query

def export_db() -> None:
    """Export SQLite database to CSV file"""
    # Load configuration
    config = load_config()
    root = get_root()
    
    # Get database path from config
    db_path = Path(root) / config.get("db_filepath")
    
    # Create csv directory if it doesn't exist
    export_dir = Path(root) / config.get("exports_filepath")
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = export_dir / f"{timestamp}.csv"
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        cursor = conn.cursor()
        
        # Get the custom export query
        query = export_query()
        
        # Execute the query
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Get column names from the query results
        columns = [description[0] for description in cursor.description]
        
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
    export_db()
