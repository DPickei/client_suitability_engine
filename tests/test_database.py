import pytest
from src.database import all_profiles

def test_insert_profiles(sample_profiles):
    # Test inserting profiles
    inserted = all_profiles.insert_profiles(sample_profiles)
    assert inserted == 1
    
    # Test duplicate handling (should not insert)
    inserted = all_profiles.insert_profiles(sample_profiles)
    assert inserted == 0

def test_initialize_database():
    conn = all_profiles.initialize_database()
    cursor = conn.cursor()
    
    # Check if table exists and has correct schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profiles'")
    assert cursor.fetchone() is not None