from pathlib import Path
import json
import pytest
from src.database import operations, shared
import sqlite3

@pytest.fixture
def db():
    """Fixture to create and cleanup database connection"""
    database = operations.DatabaseOps()
    yield database
    # Cleanup will happen automatically via __del__

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
        "location": "New York",
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
        'golfer': 'Yes',
        'position': 'Developer',
        'location': 'New York',
        'number_of_connections': 500,
        'wealth_rating': 4,
        'reasoning': 'Test reasoning',
        'profile_url': 'https://linkedin.com/test123',
        'sent': None,
        'discovery_input': 'Test input'
    }]

@pytest.fixture(autouse=True)
def cleanup_test_data():
    yield  # Run the test
    # Cleanup after test completes
    db_path = shared.get_db_path()
    conn = sqlite3.Connection(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM all_profiles WHERE linkedin_id = ? OR linkedin_id = ?', ('test123', 'adam-mayblum-0586501',))
    conn.commit()
    conn.close()