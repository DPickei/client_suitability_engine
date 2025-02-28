# Shared utilities (your shared_db_functions.py)

from src import utility_functions
from pathlib import Path

def get_db_path():
    config = utility_functions.load_config()
    db_relative_path = config.get("db_filepath")
    db_path = Path(utility_functions.get_root()) / db_relative_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path