import asyncio
from pathlib import Path

from .database import all_profiles
from . import utility_functions, metric_logging, profile_processing, db_to_csv

"""
1. Take in json file of a particular person
2. System prompt for how gemini should process
3. Give gemini the file
4. Gemini should output a list of dictionaries
5. Call on database functions to upload to db
"""

def main(folder_path):
    start_time = metric_logging.start_timer()
    profiles = asyncio.run(profile_processing.process_profiles(folder_path))
    duration = metric_logging.duration(start_time)
    metric_logging.files_processed(duration, profiles)
    all_profiles.insert_profiles(profiles)
    db_to_csv.db_to_csv()

def setup():
    config = utility_functions.load_config()
    processing_folder = config.get("processing_folder")
    root = utility_functions.get_root()
    folder_path = Path(root) / processing_folder
    return folder_path

if __name__ == "__main__":
    folder_path = setup()
    main(folder_path)