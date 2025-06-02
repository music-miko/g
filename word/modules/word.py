import os
import json

WORDS_FILE = "words.txt"


def load_words():
    if not os.path.exists(WORDS_FILE):
        return set()
    with open(WORDS_FILE, "r") as file:
        words = {line.strip().lower() for line in file if line.strip()}
    return words

COMMON_WORDS_FILE = "common.txt"

def load_common_words():
    if not os.path.exists(COMMON_WORDS_FILE):
        return set()
    with open(COMMON_WORDS_FILE, "r") as file:
        common_words = {line.strip().lower() for line in file if line.strip()}
    return common_words

def load_state_city_countries():
    countries = []
    states = []
    cities = []
    
    if os.path.exists("countries+states+cities.json"):
        with open("countries+states+cities.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            
            for country in data:
                if "name" in country:
                    countries.append(country["name"])
                
                if "states" in country and country["states"]:
                    for state in country["states"]:
                        if "name" in state:
                            states.append(state["name"])
                        
                        if "cities" in state and state["cities"]:
                            for city in state["cities"]:
                                if "name" in city:
                                    cities.append(city["name"])
    
    return {
        "countries": countries,
        "states": states,
        "cities": cities
    }