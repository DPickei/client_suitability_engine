import json
import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
from src.utility_functions import load_config, get_root

# Configure logging at the start
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def partition_profiles():
    """Orchestrate the JSON partitioning workflow"""
    try:
        config = load_config()
        input_path = validate_partition_config(config)
        output_dir = prepare_output_directory()
        
        profiles = load_profiles(input_path)
        logging.info(f"Loaded {len(profiles)} total profiles from {input_path}")
        
        grouped_data, skipped_profiles = group_by_discovery_input(profiles)
        save_partitioned_files(grouped_data, output_dir)
        
        logging.info(f"Successfully partitioned into {len(grouped_data)} files")
        if skipped_profiles:
            logging.warning(f"Skipped {skipped_profiles} profiles with invalid/missing discovery_input")

    except Exception as e:
        logging.error(f"Partitioning failed: {str(e)}", exc_info=True)

def validate_partition_config(config: Dict) -> Path:
    """Validate configuration and return input path"""
    input_path = config.get("partition_input_file")
    if not input_path:
        raise ValueError("No partition_input_file specified in config.yml")
    return Path(input_path)

def prepare_output_directory() -> Path:
    """Create and return the partitioned files directory"""
    output_dir = get_root() / "data" / "json" / "partitioned_files"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def load_profiles(input_path: Path) -> List[Dict]:
    """Load profiles from JSON file"""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def group_by_discovery_input(profiles: List[Dict]) -> tuple[Dict[str, List[Dict]], int]:
    """Group profiles by normalized discovery input names with logging"""
    grouped = defaultdict(list)
    skipped = 0
    
    for idx, profile in enumerate(profiles):
        try:
            key = get_discovery_key(profile)
            grouped[key].append(profile)
            logging.debug(f"Processed profile {idx}: {key}")
            
        except ValueError as e:
            skipped += 1
            profile_id = profile.get('id', 'no-id')
            logging.warning(
                f"Skipping profile {idx} (ID: {profile_id}): {str(e)}\n"
                f"Profile snippet: {json.dumps(profile, indent=2)[:300]}..."
            )
    
    return dict(grouped), skipped

def get_discovery_key(profile: Dict) -> str:
    """Create normalized filename key from discovery input"""
    discovery = profile.get("discovery_input", {})
    
    if not discovery:
        raise ValueError("Missing discovery_input section")
        
    first_name = discovery.get("first_name", "").strip().lower()
    last_name = discovery.get("last_name", "").strip().lower()
    
    missing = []
    if not first_name:
        missing.append("first_name")
    if not last_name:
        missing.append("last_name")
        
    if missing:
        raise ValueError(f"Missing fields in discovery_input: {', '.join(missing)}")
    
    return f"{first_name}_{last_name}"

def save_partitioned_files(grouped_data: Dict[str, List[Dict]], output_dir: Path):
    """Save grouped data to individual JSON files"""
    for key, profiles in grouped_data.items():
        output_path = output_dir / f"{key}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2)
        print(f"Saved {len(profiles)} profiles to {output_path.name}")

if __name__ == "__main__":
    partition_profiles()