import time
from datetime import datetime

def start_timer():
    start_time = time.time()
    print(f"Starting profile processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return start_time

def duration(start_time):
    end_time = time.time()
    duration = end_time - start_time
    print(f"\\processing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {duration:.2f} seconds")
    return duration

def files_processed(duration, profiles):
    print(f"Total profiles processed: {len(profiles)}")
    if len(profiles) > 0:
        print(f"Average time per file: {(duration/len(profiles)):.2f} seconds")
    else:
        print("No profiles were processed")