import asyncio
from pathlib import Path
from src.database import operations
from src.export import db_to_csv
from src import utility_functions, metric_logging, profile_processing, nlp

"""
1. Get a profile of a name (one of the json files)
2. Break it up into individuals (one fine can have multiple people)
3. Add them to the all_profiles database
4. Tag profiles in all_profiles that meet basic qualification criteria for nlp analysis
5. Process these profiles with nlp, put the results in nlp_attributes
6. Finally, we tag profiles as qualified_nlp_review = TRUE for profiles that meet our selection criteria
"""

def main(folder_path: Path) -> None:
    start_time = metric_logging.start_timer()
    db = operations.DatabaseOps()

    basic_profile_data, full_profile_data = asyncio.run(profile_processing.get_basic_user_info(db, folder_path))
    db.insert_profiles("all_profiles", basic_profile_data)
    db.tag_qualified_basic_profiles()
    tagged_profile_ids = db.get_tagged_basic_profiles()
    
    profiles_for_nlp_review = profile_processing.match_ids(full_profile_data, tagged_profile_ids)
    nlp_profiles = asyncio.run(nlp.get_nlp_attributes(profiles_for_nlp_review))
    db.insert_profiles("nlp_attributes", nlp_profiles)
    db.tag_qualified_nlp_profiles()

    duration = metric_logging.duration(start_time)
    metric_logging.files_processed(duration, basic_profile_data)
    db_to_csv.export_db()

if __name__ == "__main__":
    folder_path = utility_functions.setup()
    main(folder_path)