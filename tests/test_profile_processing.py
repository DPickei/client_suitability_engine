from src import profile_processing
import logging
import pytest

@pytest.mark.asyncio
async def test_get_basic_user_info(db, json_folderpath):
    """Test the async profile processing function"""
    # Process profiles from our test_json directory
    profiles = await profile_processing.get_basic_user_info(db, json_folderpath)
    
    # Assert that profiles were processed
    assert len(profiles) > 0, "No profiles were processed"
    
    # Assert that each profile has the expected structure
    for profile in profiles:
        assert isinstance(profile, dict), "Each profile should be a dictionary"
        assert "position" in profile, "Each profile should have a position"

def test_parse_person_in_file(json_filepath):
    result = profile_processing.parse_person_in_file(json_filepath)
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, dict)
        assert "position" in item
    
def test_get_linkedin_id(sample_user_url):
    result = profile_processing.get_linkedin_id(sample_user_url)
    assert result == "gabe-braun-04b1973"

def test_strip_profile(sample_profiles):
    logging.info(f"Test profile before stripping: {sample_profiles[0]}")
    result = profile_processing.strip_profile(sample_profiles[0])
    logging.info(f"Test profile after stripping: {result}")
    assert 'linkedin_id' not in result