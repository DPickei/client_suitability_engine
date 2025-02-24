from pathlib import Path
from src import profile_processing
import json
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_process_profiles(db, json_folderpath):
    """Test the async profile processing function"""
    # Process profiles from our test_json directory
    profiles = await profile_processing.process_profiles(db, json_folderpath)
    
    # Assert that profiles were processed
    assert len(profiles) > 0, "No profiles were processed"
    
    # Assert that each profile has the expected structure
    for profile in profiles:
        assert isinstance(profile, dict), "Each profile should be a dictionary"
        assert "linkedin_id" in profile, "Each profile should have a linkedin_id"
        assert "name" in profile, "Each profile should have a name"
        assert "position" in profile, "Each profile should have a position"

def test_get_user_info(json_filepath):
    result = profile_processing.get_user_info(json_filepath)
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, dict)
        assert "name" in item
        assert "position" in item
    
def test_get_linkedin_id(sample_user_url):
    result = profile_processing.get_linkedin_id(sample_user_url)
    assert result == "gabe-braun-04b1973"