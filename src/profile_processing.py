import asyncio
import json
from pathlib import Path
from typing import Dict, List
from . import utility_functions, database, json_parsing, nlp
import time

async def process_profiles(folder_path):
    tasks = []
    file_count = 0
    batch_size = 15
    flattened_profiles = []
    batch_start_time = time.time()  # Track when the current batch started
    
    # Get limit from config
    config = utility_functions.load_config()
    limit = config.get("limit", 0)  # Default to 0 (no limit) if not specified
    
    # Get list of already parsed names
    parsed_names = database.get_parsed_names()

    # Get total number of files to process
    all_files = [f for f in folder_path.glob("*.json") if not is_parsed_profile(parsed_names, f)]
    total_files = len(all_files) if not limit else min(len(all_files), limit)

    for json_file_path in folder_path.glob("*.json"):
        if is_parsed_profile(parsed_names, json_file_path): continue
            
        print(f"Scheduling processing for {json_file_path}...")
        tasks.append(asyncio.to_thread(get_user_info, json_file_path))
        file_count += 1
        
        # Check if we've hit the limit
        if limit and file_count >= limit:
            print(f"Reached processing limit of {limit} files")
            break
        
        # Process in batches of 40
        if len(tasks) >= batch_size:
            batch_profiles = await asyncio.gather(*tasks)
            flattened_profiles.extend([profile for file_profiles in batch_profiles for profile in file_profiles])
            database.insert_profiles(flattened_profiles)
            print(f"Processed batch: {file_count}/{total_files} complete")
            
            # Calculate time remaining to reach 60 seconds
            elapsed_time = time.time() - batch_start_time
            if elapsed_time < 60:
                wait_time = 60 - elapsed_time
                print(f"Waiting {wait_time:.1f} seconds to maintain rate limit...")
                await asyncio.sleep(wait_time)
            
            # Reset for next batch
            tasks = []
            batch_start_time = time.time()
    
    # Process any remaining files
    if tasks:
        batch_profiles = await asyncio.gather(*tasks)
        flattened_profiles.extend([profile for file_profiles in batch_profiles for profile in file_profiles])
        database.insert_profiles(flattened_profiles)
        print(f"Processed final batch: {file_count}/{total_files} complete")
    
    return flattened_profiles

def get_user_info(json_file: Path) -> List[Dict]:
    raw_json = json_parsing.open_file(json_file)
    if raw_json is False: return

    profiles = []
    for person in raw_json:
        if json_parsing.memorialized_account == True: continue
        nlp_response = nlp.send_request(json.dumps(person))

        profile_url = person.get("url")
        linkedin_id = get_linkedin_id(profile_url)
        
        profile_data = {
            "linkedin_id": linkedin_id,
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
        profiles.append(profile_data)
    
    return profiles

def get_linkedin_id(linkedin_url: str) -> str:
    if not linkedin_url: return ""
    return linkedin_url.strip('/').split('/')[-1]
    
def is_parsed_profile(parsed_names: List[str], json_file_path: str):
    """returns True if the profile has already been parsed"""
    filename_stem = json_file_path.stem
    if filename_stem in parsed_names:
        print(f"Skipping already parsed profile: {json_file_path}")
        return True
    return False