from pathlib import Path
import json
import pytest
from src.database import operations
from unittest.mock import patch
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename="tests/test.log"
)

@pytest.fixture(scope="session")
def db():
    """Fixture to create and cleanup database connection"""
    # Use a different database file for tests to avoid conflicts
    with patch('src.database.shared.get_db_path') as mock_get_db_path:
        # Use an in-memory database for testing
        mock_get_db_path.return_value = ':memory:'
        database = operations.DatabaseOps()
        
        # Initialize the database schema
        database.cursor.execute('''
        CREATE TABLE IF NOT EXISTS all_profiles (
            linkedin_id TEXT PRIMARY KEY,
            name TEXT,
            position TEXT,
            city_state_country TEXT,
            country_code TEXT,
            number_of_connections INTEGER,
            profile_url TEXT,
            discovery_input TEXT
        )
        ''')
        
        # Add any other tables your tests need
        database.cursor.execute('''
        CREATE TABLE IF NOT EXISTS nlp_attributes (
            linkedin_id TEXT PRIMARY KEY,
            FOREIGN KEY (linkedin_id) REFERENCES all_profiles (linkedin_id)
        )
        ''')
        
        database.cursor.execute('''
        CREATE TABLE IF NOT EXISTS qualified_profiles (
            linkedin_id TEXT PRIMARY KEY,
            qualified_basic_info BOOLEAN,
            FOREIGN KEY (linkedin_id) REFERENCES all_profiles (linkedin_id)
        )
        ''')
        
        database.conn.commit()
        
        yield database
        
        # No cleanup needed for in-memory database

@pytest.fixture
def json_folderpath():
    folder_path = Path(__file__).parent / "test_data" / "test_json"
    return folder_path

@pytest.fixture
def json_filepath():
    """filepath to a sample json file, for adam mayblum"""
    current_dir = Path(__file__).parent
    filepath = current_dir / "test_data" / "test_json" / "adam_mayblum.json"
    return filepath

def test_json_filepath(adam_mayblum_json):
    """test of our fixture"""
    print(f"Json file: {adam_mayblum_json}")
    assert adam_mayblum_json is not False

@pytest.fixture
def data_dir(tmp_path):
    """Create a temporary directory with test JSON files"""
    test_dir = tmp_path / "test_nlp_processing"
    test_dir.mkdir()
    
    # Create a sample JSON file
    test_file = test_dir / "test_profile.json"
    sample_data = [{
        "name": "Test Person",
        "position": "Software Engineer",
        "city": "New York, New York, United States",
        "connections": 500
    }]
    
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f)
    
    return test_dir   

@pytest.fixture
def test_profile_str():
    """Returns a string of the test profile data"""
    current_dir = Path(__file__).parent
    filepath = current_dir / "test_data" / "test_profile.txt"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        profile_data = f.read()
    
    return profile_data 

@pytest.fixture
def sample_user_url():
    return "https://www.linkedin.com/in/gabe-braun-04b1973"

@pytest.fixture
def sample_profiles():
    return [{
        'linkedin_id': 'test123',
        'name': 'Test User',
        'position': 'Developer',
        'city_state_country': 'New York, New York, United States',
        'country_code': 'US',
        'number_of_connections': 500,
        'profile_url': 'https://linkedin.com/test123',
        'discovery_input': 'Test input'
    }]

@pytest.fixture(autouse=True)
def cleanup_test_data(db):
    yield  # Run the test
    
    # We need to check if the table exists before trying to delete from it
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='all_profiles'")
    if db.cursor.fetchone():
        # Table exists, safe to delete
        db.cursor.execute('DELETE FROM all_profiles WHERE linkedin_id = ? OR linkedin_id = ?', 
                         ('test123', 'adam-mayblum-0586501',))
        db.conn.commit()