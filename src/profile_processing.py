import asyncio
import logging
from pathlib import Path
import json
from typing import Dict, List
from src.database.operations import DatabaseOps
from . import json_parsing
from src.logging_config import setup_logging

async def get_basic_user_info(db: DatabaseOps, folder_path: Path) -> tuple[List[Dict], List[Dict]]:
    """ Returns profiles of people. Expects a directory of json files with individuals names as each file name """
    parsed_names = db.get_parsed_names()
    all_results = []
    tasks = []
    for file_path in folder_path.glob("*.json"):
        if is_parsed_profile(parsed_names, file_path): continue # Skip already parsed profiles
        print(f"Scheduling processing for {file_path}...")
        tasks.append(asyncio.to_thread(parse_person_in_file, file_path))
    
    if tasks:
        all_results = await asyncio.gather(*tasks)
        # Filter out None values
        all_results = [result for result in all_results if result]
    
    # Separate basic profiles and full profiles
    basic_profiles = []
    full_profiles = []
    for result in all_results:
        if result:
            basic_result, full_result = result
            basic_profiles.extend(basic_result)
            full_profiles.extend(full_result)
    
    return basic_profiles, full_profiles

def parse_person_in_file(file_path: Path) -> List[Dict] | None:
    """ Iterates through json files of profiles not yet processed into all_profiles """
    raw_json = json_parsing.open_file(file_path)
    if raw_json is False: return
    basic_profiles = []
    full_profiles = []
    for person in raw_json:
        if json_parsing.memorialized_account(person): continue
        profile_url = person.get("url")
        linkedin_id = get_linkedin_id(profile_url)
        basic_profile_data = {
            "linkedin_id": linkedin_id,
            "name": person.get("name"),
            "position": person.get("position"),
            "city_state_country": person.get("city"),
            "country_code": person.get("country_code"),
            "number_of_connections": person.get("connections"),
            "profile_url": profile_url,
            "discovery_input": json_parsing.get_discovery_input(person)
        }
        basic_profiles.append(basic_profile_data)
        full_profiles.append(person)
    return basic_profiles, full_profiles

def match_ids(full_profile_data: List[Dict], tagged_profile_ids: List[str]) -> List[Dict]:
    matched_profiles = []
    for profile in full_profile_data:
        profile_id = profile.get("linkedin_id")
        if profile_id in tagged_profile_ids:
            matched_profiles.append(profile)
    setup_logging()
    logging.info(f"matched profiles: {json.dumps(matched_profiles, indent=2)}")
    return matched_profiles

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

def strip_profile(profile: dict) -> dict:
    """ Remove values from a profile we don't need when processing it for NLP """
    setup_logging()
    logging.info(f"Real profile before stripping: {json.dumps(profile, indent=2)}")
    attributes_to_remove = {
    "avatar",
    "banner_image", 
    "connections",
    "default_avatar",
    "discovery_input",
    "followers",
    "id",
    "input",
    "input_url",
    "linkedin_num_id",
    "memorialized_account",
    "people_also_viewed",
    "similar_profiles",
    "timestamp",
    "url"
    }
    for attribute in attributes_to_remove:
        profile.pop(attribute, None)
    logging.info(f"Real profile after stripping: {json.dumps(profile, indent=2)}")
    return profile