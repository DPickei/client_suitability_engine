import pytest
from src import database

def test_insert_profiles(sample_profiles):
    # Test inserting profiles
    inserted = database.insert_profiles(sample_profiles)
    assert inserted == 1
    
    # Test duplicate handling (should not insert)
    inserted = database.insert_profiles(sample_profiles)
    assert inserted == 0

def test_initialize_database():
    conn = database.initialize_database()
    cursor = conn.cursor()
    
    # Check if table exists and has correct schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profiles'")
    assert cursor.fetchone() is not None