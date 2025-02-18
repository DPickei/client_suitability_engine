import os
import re
import json
from json import JSONDecodeError
from google import genai
from . import utility_functions, database
from pydantic import BaseModel

class ProfileAnalysis(BaseModel):
    wealth_rating: int
    reasoning: str
    golfer: str

def send_request(person):
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

def clean_response(response):
    try:
        # Clean and validate response
        raw_text = response.text.strip()
        raw_text = re.sub(r'^```(json)?|```$', '', raw_text, flags=re.MULTILINE)
        raw_text = raw_text.strip()
        
        try:
            response_json = json.loads(raw_text)
        except JSONDecodeError as e:
            # Try to repair truncated JSON arrays
            if raw_text.startswith('['):
                # Find last complete object by looking for "}," or "}"
                last_object = max(raw_text.rfind('},'), raw_text.rfind('}'))
                if last_object > 0:
                    raw_text = raw_text[:last_object+1] + ']'
                    response_json = json.loads(raw_text)
                else:
                    raise  # Re-raise if we can't find a valid endpoint

        # Database insertion
        conn = database.initialize_database()
        inserted_count = database.insert_contacts(conn, response_json, json_file.name)
        print(f"Successfully processed {inserted_count} contacts from {json_file.name}")

    except JSONDecodeError as e:
        print(f"JSON parsing failed for {json_file.name}: {str(e)}")
        print(f"Error context: {raw_text[max(0,e.pos-30):e.pos+30]}")
        print(f"Full response: {response.text[:500]}...")  # Print start of response for debugging
    except Exception as e:
        print(f"Failed to process {json_file.name}: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()