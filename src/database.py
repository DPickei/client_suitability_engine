import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from src import utility_functions

def get_db_path():
    config = utility_functions.load_config()
    db_relative_path = config.get("db_filepath")
    db_path = Path(utility_functions.get_root()) / db_relative_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path

def initialize_database() -> sqlite3.Connection:
    """Initialize SQLite database with schema"""
    db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            linkedin_id TEXT PRIMARY KEY,
            name TEXT,
            golfer TEXT,
            position TEXT,
            location TEXT,
            number_of_connections INTEGER,
            wealth_rating INTEGER,
            reasoning TEXT,
            profile_url TEXT UNIQUE,
            sent TEXT,
            discovery_input TEXT
        )
    ''')
    return conn

def insert_profiles(profiles: List[Dict]) -> int:
    """Insert profiles into database with conflict handling"""
    conn = initialize_database()
    cursor = conn.cursor()
    
    inserted_count = 0
    for profile in profiles:
        cursor.execute('''
            INSERT OR IGNORE INTO profiles (
                linkedin_id, 
                name,
                golfer,
                position,
                location,
                number_of_connections,
                wealth_rating,
                reasoning,
                profile_url,
                sent,
                discovery_input
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            profile.get('linkedin_id'),
            profile.get('name'),
            profile.get('golfer'),
            profile.get('position'),
            profile.get('location'),
            profile.get('number_of_connections'),
            profile.get('wealth_rating', 0),
            profile.get('reasoning', ''),
            profile.get('profile_url'),
            profile.get('sent'),
            profile.get('discovery_input')
        ))
        if cursor.rowcount == 1:  # Only count successful inserts
            inserted_count += 1
            
    conn.commit()
    return inserted_count

def get_parsed_names() -> List[str]:
    """Get list of discovery_inputs that have already been parsed.
    
    Returns:
        List[str]: List of lowercase discovery_input values from the database
    """
    try:
        conn = initialize_database()
        cursor = conn.cursor()
        
        # First check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profiles'")
        if not cursor.fetchone():
            return []  # Return empty list if table doesn't exist yet
            
        cursor.execute('SELECT DISTINCT LOWER(discovery_input) FROM profiles WHERE discovery_input IS NOT NULL')
        parsed_names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return parsed_names
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            return []  # Table doesn't exist yet, return empty list
        print(f"Database operational error: {e}")
        return []
    except sqlite3.Error as e:
        print(f"Error getting parsed names: {e}")
        return []
    