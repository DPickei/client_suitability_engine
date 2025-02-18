import asyncio
import json
import sqlite3
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Any
from google import genai
from json import JSONDecodeError
from . import utility_functions, database, json_parsing, nlp
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
    
    config = utility_functions.load_config()
    root = utility_functions.get_root()

    # Replace nlp_processing_file with nlp_processing_folder
    nlp_processing_folder = config.get("nlp_processing_folder")
    folder_path = Path(root) / nlp_processing_folder

    tasks = []
    file_count = 0
    # Loop through each JSON file in the folder and schedule processing concurrently
    for json_file in folder_path.glob("*.json"):
        print(f"Scheduling processing for {json_file}...")
        # Run get_user_info in a separate thread since it's blocking
        tasks.append(asyncio.to_thread(get_user_info, json_file))
        file_count += 1
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nAsync processing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Processed {file_count} files")
    print(f"Average time per file: {(duration/file_count):.2f} seconds")

def get_user_info(json_file):
    # First validate the given JSON file
    raw_json = json_parsing.open_file(json_file)
    if raw_json is False: return

    for person in raw_json:
        if json_parsing.memorialized_account == True: continue
        nlp_response = nlp.send_request(json.dumps(person))
        
        profile_data = {
            "name": person.get("name"),
            "golfer": nlp_response.get("golfer"),
            "position": person.get("position"),
            "location": person.get("location"),
            "number_of_connections": person.get("connections"),
            "wealth_rating": nlp_response.get("wealth_rating"),
            "reasoning": nlp_response.get("reasoning"),
            "profile_url": person.get("url"),
            "sent": None,
            "discovery_input": json_parsing.get_discovery_input(person)
        }

if __name__ == "__main__":
    asyncio.run(process_profiles_async())
