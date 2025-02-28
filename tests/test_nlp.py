import pytest
import json
import asyncio
from src import nlp

def test_send_request(monkeypatch, test_profile_str):
    # Ensure test_profile_str is actually a string
    assert isinstance(test_profile_str, str)
    
    # Mock the response from Gemini
    class MockResponse:
        text = json.dumps({
            "wealth_rating": 5,
            "wealth_reasoning": "Test reasoning",
            "golfer": True,
            "golfer_reasoning": "Test golfer reasoning",
            "lawyer": False,
            "active_ceo": True,
            "nationality": "US",
            "sex": "Male",
            "lives_in_preferred_states": True,
            "retired": False,
            "age_estimate": 45
        })
    
    # Mock the client and config
    class MockModels:
        def generate_content(self, *args, **kwargs):
            return MockResponse()
            
    class MockClient:
        def __init__(self, api_key=None):
            self.models = MockModels()
    
    def mock_config(*args):
        return {"profile_parsing_prompt": "test prompt"}
    
    # Apply mocks
    monkeypatch.setattr('google.genai.Client', MockClient)
    monkeypatch.setattr('src.utility_functions.load_config', mock_config)
    
    # Test the function
    result = nlp.send_request(test_profile_str)
    
    assert result is not None
    assert isinstance(result, dict)
    assert result["wealth_rating"] == 5
    assert result["golfer"] == True

@pytest.mark.asyncio
async def test_profile_nlp_processing(monkeypatch):
    # Create a test profile dictionary directly
    test_profile = {
        "linkedin_id": "test-user",
        "name": "Test User",
        "position": "Software Engineer",
        "city_state_country": "New York, NY, USA",
        "country_code": "US",
        "number_of_connections": 500,
        "profile_url": "https://linkedin.com/in/test-user"
    }
    
    # Mock send_request to return a simple result
    def mock_send_request(profile_str):
        # Verify that profile_str is a string
        assert isinstance(profile_str, str)
        return {"wealth_rating": 4, "golfer": False}
    
    monkeypatch.setattr('src.nlp.send_request', mock_send_request)
    
    # Test the async wrapper with a dictionary directly
    result = await nlp.profile_nlp_processing(test_profile)
    
    assert result is not None
    assert result["wealth_rating"] == 4
    assert result["golfer"] == False

@pytest.mark.asyncio
async def test_get_nlp_attributes(monkeypatch, sample_profiles):
    # Mock profile_nlp_processing to return test data
    async def mock_profile_nlp_processing(profile):
        return {"wealth_rating": 3, "golfer": True}
    
    # Mock config to use small batch size
    def mock_config(*args):
        return {"batch_size": 2}
    
    monkeypatch.setattr('src.nlp.profile_nlp_processing', mock_profile_nlp_processing)
    monkeypatch.setattr('src.utility_functions.load_config', mock_config)
    
    # Test with a small sample
    results = await nlp.get_nlp_attributes(sample_profiles)
    
    assert len(results) == len(sample_profiles)
    assert results[0]["wealth_rating"] == 3
    assert results[0]["golfer"] == True