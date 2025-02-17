import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from src.utility_functions import get_root

def initialize_database() -> sqlite3.Connection:
    """Initialize SQLite database with schema"""
    db_path = get_root() / "data" / "db" / "contacts.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            location TEXT,
            wealth_rating INTEGER,
            reasoning TEXT,
            title TEXT,
            number_of_connections INTEGER,
            linkedin_url TEXT UNIQUE,
            sent TEXT
        )
    ''')
    return conn

def insert_contacts(conn: sqlite3.Connection, contacts: List[Dict], json_file_name: str) -> int:
    """Insert contacts into database with conflict handling"""
    inserted_count = 0
    cursor = conn.cursor()
    
    for contact in contacts:
        cursor.execute('''
            INSERT OR IGNORE INTO contacts (
                first_name,
                last_name,
                location,
                wealth_rating,
                reasoning,
                title,
                number_of_connections,
                linkedin_url
            ) VALUES (?,?,?,?,?,?,?,?)
        ''', (
            contact.get('first_name'),
            contact.get('last_name'),
            contact.get('location'),
            contact.get('wealth_rating', 0),
            contact.get('reasoning', ''),
            contact.get('title', ''),
            contact.get('number_of_connections', 0),
            contact.get('linkedin_url')
        ))
        if cursor.rowcount == 1:  # Only count successful inserts
            inserted_count += 1
            
    conn.commit()
    return inserted_count