import json
import os
import argparse

def pretty_print_json(input_path):
    # Split filename and extension
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_pretty{ext}"
    
    try:
        # Read original file with UTF-8 encoding
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Write pretty-printed version with UTF-8 encoding
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            
        print(f"Created pretty-printed version at: {output_path}")
    
    except FileNotFoundError:
        print(f"Error: File not found - {input_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file - {input_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create pretty-printed version of JSON file')
    parser.add_argument('file_path', help='Path to JSON file')
    args = parser.parse_args()
    
    pretty_print_json(args.file_path) 