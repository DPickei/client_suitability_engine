import requests
import csv
import src
import src.utility_functions
import os
from dotenv import load_dotenv

load_dotenv()

def trigger_brightdata():
    url = (
        "https://api.brightdata.com/datasets/v3/trigger"
        "?dataset_id=gd_l1viktl72bvl7bjuj0"
        "&include_errors=true"
        "&type=discover_new"
        "&discover_by=name"
    )
    input_names = []
    config = src.utility_functions.load_config()
    input_names_filepath = config.get("input_names_filepath")
    with open(input_names_filepath, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        # Sanitize field names with BOM removal
        reader.fieldnames = [name.lstrip('\ufeff').strip().lower().replace('_', ' ').replace('-', ' ') 
                            for name in reader.fieldnames]
        
        print("Detected CSV columns after sanitization:", reader.fieldnames)  # Updated debug
        
        for row in reader:
            input_names.append({
                "first_name": row.get('first name', ''),
                "last_name": row.get('last name', '')
            })

    # The JSON payload with dynamic input
    payload = {
        "deliver": {
            "type": "s3",
            "filename": {
                "template": "{[snapshot_id]}",
                "extension": "json"
            },
            "bucket": "wealth-engine-name-list",
            "credentials": {
                "aws-access-key": os.getenv("AWS_ACCESS_KEY"),
                "aws-secret-key": os.getenv("AWS_SECRET_KEY")
            },
            "directory": "brightdata-uploads/"
        },
        "input": input_names
    }

    # Request headers
    headers = {
        "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_TOKEN')}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Request succeeded!")
        print("Response status code:", response.status_code)
        print("Response text:", response.text)
    except requests.exceptions.HTTPError as err:
        print("HTTP error occurred:", err)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    trigger_brightdata()
