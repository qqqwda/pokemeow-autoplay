import os
import json

# Define the path to the file where you want to store catch_counter
CATCH_COUNTER_FILE = "catch_counter.json"

def save_catch_counter(catch_counter):
    # Save catch_counter to a file
    with open(CATCH_COUNTER_FILE, 'w') as f:
        json.dump({'catch_counter': catch_counter}, f)

def load_catch_counter():
    # Load catch_counter from a file
    if os.path.exists(CATCH_COUNTER_FILE):
        with open(CATCH_COUNTER_FILE, 'r') as f:
            data = json.load(f)
            return data.get('catch_counter', 0)
    else:
        return 0