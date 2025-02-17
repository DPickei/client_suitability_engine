import json
import tiktoken
from pathlib import Path
from src.utility_functions import load_config

def count_json_tokens():
    """Count tokens in JSON file specified in config"""
    config = load_config()
    input_path = config.get("token_count_file")
    
    if not input_path:
        print("Error: No token_count_file specified in config.yml")
        return

    try:
        # Load JSON data
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get encoding and count tokens
        encoding = tiktoken.get_encoding("cl100k_base")
        json_str = json.dumps(data)
        token_count = len(encoding.encode(json_str))
        
        print(f"Token count for {input_path}: {token_count:,}")

        # New cost calculation
        cost_per_million_tokens = 0.10  # USD per million tokens
        cost = (token_count / 1_000_000) * cost_per_million_tokens
        print(f"Estimated Cost ({cost_per_million_tokens}/million tokens): ${cost:.6f}")
        
    except FileNotFoundError:
        print(f"Error: File not found - {input_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file - {input_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    count_json_tokens() 