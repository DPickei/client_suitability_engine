import asyncio
import json
import sqlite3
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Any
from google import genai
from dotenv import load_dotenv
from json import JSONDecodeError
from src.utility_functions import load_config, get_root
from src.database import initialize_database, insert_contacts
from datetime import datetime

"""
1. Take in json file of a particular person
2. System prompt for how gemini should process
3. Give gemini the file
4. Gemini should output a list of dictionaries
5. Call on database functions to upload to db
"""
async def process_profiles_async():
    start_time = time.time()
    print(f"Starting async profile processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    config = load_config()
    root = get_root()

    # Replace nlp_processing_file with nlp_processing_folder
    nlp_processing_folder = config.get("nlp_processing_folder")
    folder_path = Path(root) / nlp_processing_folder

    tasks = []
    file_count = 0
    # Loop through each JSON file in the folder and schedule processing concurrently
    for json_file in folder_path.glob("*.json"):
        print(f"Scheduling processing for {json_file}...")
        # Run execute_nlp in a separate thread since it's blocking
        tasks.append(asyncio.to_thread(execute_nlp, json_file))
        file_count += 1
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nAsync processing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Processed {file_count} files")
    print(f"Average time per file: {(duration/file_count):.2f} seconds")

def execute_nlp(json_file):
    # First validate the input JSON file
    try:
        with open(json_file, "r", encoding='utf-8') as f:
            file_content = f.read()
            # Validate JSON before sending to Gemini
            input_json = json.loads(file_content)
    except JSONDecodeError as e:
        print(f"Invalid input JSON in {json_file.name}")
        print(f"Error at position {e.pos}: {file_content[max(0,e.pos-50):e.pos+50]}")
        return
        
    api_key = os.getenv("GEMINI_API_KEY")

    prompt = """Analyze these LinkedIn profiles and extract these EXACT fields:
    1. first_name: From "name" field (first part before space)
    2. last_name: From "name" field (remaining after first space)
    3. location: Prefer "city" field, fallback to "location"
    4. wealth_rating: estimate of the individuals net worth, 1 being less than $100K, 10 being over $10M
    5. reasoning: justification for wealth rating, no more than 15 words.
    6. title: Use "position" field if exists, else "current_company.title"
    7. number_of_connections: Direct value from "connections" field
    8. linkedin_url: From "url" field

    Example input snippet:
    {
        "name": "Adam Mayblum",
        "connections": 224,
        "position": "Entrepreneur",
        "city": "New Rochelle, New York, United States",
        "url": "https://linkedin.com/in/adam-mayblum-0586501"
    }

    Example output:
    {
        "first_name": "Adam",
        "last_name": "Mayblum",
        "location": "New Rochelle, New York, United States",
        "wealth_rating": 7,
        "reasoning": "Partner at a private equity firm. Harvard business school",
        "title": "Entrepreneur",
        "number_of_connections": 495,
        "linkedin_url": "https://linkedin.com/in/adam-mayblum-0586501"
    }

    Return JSON list with these exact keys. No markdown formatting."""

    # Send validated JSON to Gemini
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[json.dumps(input_json), "\n\n", prompt]  # Use dumps to ensure valid JSON
    )
    
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
        conn = initialize_database()
        inserted_count = insert_contacts(conn, response_json, json_file.name)
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

if __name__ == "__main__":
    asyncio.run(process_profiles_async())
