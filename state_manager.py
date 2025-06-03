import os
import json
import requests

from memory_handler import (
    extract_facts)


API_URL = "http://localhost:1234/v1/chat/completions"

WORLD_FILE = "./world/world.json"
CHAR_DIR = "./world/characters"



os.makedirs(CHAR_DIR, exist_ok=True)
if not os.path.exists(WORLD_FILE):
    with open(WORLD_FILE, "w") as f:
        json.dump({"weather": "clear", "events": []}, f)

def ensure_character_exists(character_id):
    path = os.path.join(CHAR_DIR, f"{character_id}.json")
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"id": character_id, "facts": [], "relations": {}}, f)

def load_character_profile(character_id):
    path = os.path.join(CHAR_DIR, f"{character_id}.json")
    with open(path, "r") as f:
        return json.load(f)

def save_character_profile(profile):
    path = os.path.join(CHAR_DIR, f"{profile['id']}.json")
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)


def update_character_memory(character_id, text):
    ensure_character_exists(character_id)
    profile = load_character_profile(character_id)
    facts = extract_facts(text).split("\n")
    for fact in facts:
        if fact.strip() and fact.strip() not in profile["facts"]:
            profile["facts"].append(fact.strip())
    save_character_profile(profile)

def update_world_memory(text):
    with open(WORLD_FILE, "r") as f:
        world = json.load(f)

    facts = extract_facts(text).split("\n")

    for fact in facts:
        if "weather" in fact.lower():
            world["weather"] = fact
        elif fact.strip() not in world["events"]:
            world["events"].append(fact.strip())

    with open(WORLD_FILE, "w") as f:
        json.dump(world, f, indent=2)

def get_character_summary(character_id):
    path = os.path.join(CHAR_DIR, f"{character_id}.json")
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        profile = json.load(f)
    summary = f"{character_id.replace('_', ' ').title()} is known as:\n"
    summary += "\n".join(f"- {fact}" for fact in profile["facts"])
    return summary

def extract_character_name(text):
    prompt = f"""
From the roleplay text, extract the character name the user is primarily talking to.

Respond only with an ID in snake_case. If no clear character, reply "default".

\"\"\"{text}\"\"\"
"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "indeed",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    result = response.json()["choices"][0]["message"]["content"].strip().lower()
    return None if "default" in result else result.replace(" ", "_")
