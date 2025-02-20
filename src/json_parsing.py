# Purpose: Abstracts json handling from main.py

import json

def open_file(json_file: str):
    try:
        with open(json_file, "r", encoding='utf-8') as f:
            file_content = f.read()
            return json.loads(file_content)
            
    except json.JSONDecodeError as e:
        print(f"Invalid input JSON in {json_file.name}")
        print(f"Error at position {e.pos}: {file_content[max(0,e.pos-50):e.pos+50]}")
        return False
    
def get_discovery_input(raw_json: dict) -> str:
    first_name = raw_json["discovery_input"]["first_name"]
    last_name = raw_json["discovery_input"]["last_name"]
    discovery_input = first_name + "_" + last_name
    return discovery_input

def memorialized_account(raw_json: dict) -> bool:
    return raw_json.get("memorialized_account")