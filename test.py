import os
import time
import sys

WORDS_FILE = "common.txt"
SAMPLE_LOOKUP_WORD = "example"  
def load_as_list():
    if not os.path.exists(WORDS_FILE):
        return []
    with open(WORDS_FILE, "r") as file:
        return [line.strip().lower() for line in file if line.strip()]

def load_as_set():
    if not os.path.exists(WORDS_FILE):
        return set()
    with open(WORDS_FILE, "r") as file:
        return {line.strip().lower() for line in file if line.strip()}

def load_as_dict():
    if not os.path.exists(WORDS_FILE):
        return {}
    with open(WORDS_FILE, "r") as file:
        return {line.strip().lower(): True for line in file if line.strip()}

def measure_loading_and_lookup(load_func, structure_name):
    print(f"\n--- Testing {structure_name} ---")
    
    start_time = time.time()
    data = load_func()
    load_time = time.time() - start_time
    print(f"{structure_name} Load Time: {load_time:.4f} seconds")

    size = sys.getsizeof(data)
    print(f"{structure_name} Memory Size (shallow): {size} bytes")
    print(f"Total Items Loaded: {len(data)}")

    start_lookup = time.time()
    exists = SAMPLE_LOOKUP_WORD in data
    lookup_time = time.time() - start_lookup
    print(f"{structure_name} Lookup Time: {lookup_time:.8f} seconds")
    print(f"Word '{SAMPLE_LOOKUP_WORD}' Found: {exists}")

if __name__ == "__main__":
    print("Reading word list from:", WORDS_FILE)
    
    measure_loading_and_lookup(load_as_list, "List")
    measure_loading_and_lookup(load_as_set, "Set")
    measure_loading_and_lookup(load_as_dict, "Dict")
