from src import nlp
import json

def test_send_request(monkeypatch, test_profile_str):
    # 1. We create a fake response that mimics what Gemini would return
    def mock_generate_content(*args, **kwargs):
        class MockResponse:
            text = json.dumps({
                "wealth_rating": 5,
                "reasoning": "Test reasoning",
                "golfer": True
            })
        return MockResponse()
    
    # 2. We create a fake config function that returns what we need
    def mock_config(*args):
        return {"profile_parsing_prompt": "test prompt"}
    
    # 3. Create a mock Client class that matches your actual usage
    class MockClient:
        def __init__(self, api_key=None):
            self.models = MockModels()
    
    class MockModels:
        def generate_content(self, *args, **kwargs):
            return mock_generate_content()
    
    # 4. Match how nlp.py actually creates the client
    monkeypatch.setattr('google.genai.Client', MockClient)
    monkeypatch.setattr('src.utility_functions.load_config', mock_config)
    
    result = nlp.send_request(test_profile_str)
    
    assert result is not None
    assert isinstance(result, dict)