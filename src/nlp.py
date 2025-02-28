import os
import json
from google import genai
from . import utility_functions
from pydantic import BaseModel
import asyncio
import time
from typing import Dict, List
from src import profile_processing

class ProfileAnalysis(BaseModel):
    wealth_rating: int
    wealth_reasoning: str
    golfer: bool
    golfer_reasoning: str
    lawyer: bool
    active_ceo: bool
    nationality: str
    sex: str
    lives_in_preferred_states: bool
    retired: bool
    age_estimate: int

def send_request(profile) -> dict:
    prompts = utility_functions.load_config("prompts.yml")
    profile_parsing_prompt = prompts.get("profile_parsing_prompt")

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[profile, "\n\n", profile_parsing_prompt],
        config={
            'response_mime_type': 'application/json',
            'response_schema': ProfileAnalysis,
        }
    )
    
    # Parse the response and add the linkedin_id from the profile
    response_data = json.loads(response.text)
    
    # Extract linkedin_id from the profile
    profile_data = json.loads(profile) if isinstance(profile, str) else profile
    linkedin_id = profile_data.get("linkedin_id", "")
    
    # Add linkedin_id to the response data
    response_data["linkedin_id"] = linkedin_id
    
    return response_data

async def get_nlp_attributes(profiles: List[Dict]) -> List[Dict]:
    """ This will populate the nlp_attributes table with user values """
    print(f"Parsing attributes of {len(profiles)} profiles")
    flattened_profiles = []
    config = utility_functions.load_config()
    batch_size = config.get("batch_size", 400)

    # Process profiles in batches
    for i in range(0, len(profiles), batch_size):
        batch = profiles[i:i+batch_size]
        start_time = time.time()
        
        # Process each profile in the batch concurrently
        batch_results = []
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(profile_nlp_processing(profile)) for profile in batch]
        
        # Collect results from completed tasks
        for task in tasks:
            batch_results.append(task.result())
        
        flattened_profiles.extend(batch_results)
        
        # Only enforce rate limiting if we're processing a full batch
        # This avoids unnecessary waiting for small or final partial batches
        if len(batch) == batch_size:
            elapsed_time = time.time() - start_time
            if elapsed_time < 60:  # 60 seconds = 1 minute
                wait_time = 60 - elapsed_time
                print(f"Full batch completed in {elapsed_time:.2f} seconds. Waiting {wait_time:.2f} seconds...")
                await asyncio.sleep(wait_time)
            else:
                print(f"Batch processing took {elapsed_time:.2f} seconds (more than 1 minute)")
        else:
            elapsed_time = time.time() - start_time
            print(f"Partial batch ({len(batch)}/{batch_size}) completed in {elapsed_time:.2f} seconds")
    
    return flattened_profiles

async def profile_nlp_processing(profile):
    """Async wrapper for the synchronous send_request function"""
    # Use run_in_executor to run the blocking send_request in a thread pool
    loop = asyncio.get_running_loop()
    stripped_profile = profile_processing.strip_profile(profile)
    profile_str = json.dumps(stripped_profile, indent=2)
    return await loop.run_in_executor(None, send_request, profile_str)