import os
import json
from google import genai
from . import utility_functions
from pydantic import BaseModel
import requests

class ProfileAnalysis(BaseModel):
    wealth_rating: int
    reasoning: str
    golfer: str

def send_request(person) -> dict:
    prompts = utility_functions.load_config("prompts.yml")
    profile_parsing_prompt = prompts.get("profile_parsing_prompt")

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[person, "\n\n", profile_parsing_prompt],
        config={
            'response_mime_type': 'application/json',
            'response_schema': ProfileAnalysis,
        }
    )
    
    response_data = json.loads(response.text)
    return {
        "wealth_rating": response_data.get("wealth_rating"),
        "reasoning": response_data.get("reasoning"),
        "golfer": response_data.get("golfer")
    }