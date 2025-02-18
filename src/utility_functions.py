import yaml
from pathlib import Path

def get_root() -> Path:
    """Get project root directory"""
    return Path(__file__).resolve().parent.parent

def load_config(config_file: str = None) -> dict:
    root = get_root()
    config_path = root / (config_file or "config.yml")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Config file not found at {config_path}")
    except yaml.YAMLError:
        raise RuntimeError(f"Invalid YAML in config file at {config_path}")