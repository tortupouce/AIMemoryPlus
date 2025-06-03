import os
import json
import requests

from memory_handler import (
    search_memory,
    add_memory,
    extract_facts,
    save_memory,
    load_memory,
)

from state_manager import (
    load_character_profile,
    update_character_memory,
    update_world_memory,
    extract_character_name,
    ensure_character_exists,
    get_character_summary,
)
SYSTEM_PROMPT = (
    "You are a fantasy roleplay AI guiding a dynamic world in an heroic fantasy setting with magic and swords.\n"
    "You NEVER speak directly as yourself — always through characters (via 'Character: \"Dialogue\"') or third-person narration.\n"
    "Each line should clearly indicate who is speaking or acting.\n"
    "Use the format:\n"
    "  Character: \"Direct dialogue here.\"\n"
    "  Narrator: Description of setting, action, or thoughts.\n"
    "If multiple characters speak in a single reply, label each line with their name.\n"
    "If it's unclear who is speaking, use 'Narrator'.\n"
    "Do not summarize or break character.\n"
    "If the user speaks using quotes or colons, treat it as a character speaking. Otherwise, assume they are acting in the world.\n"
    "Be immersive and concise, like a live game master.\n"
    "The user plays as the main character, named Tortupouce.\n"
    "Tortupouce is not an NPC. Never invent actions, thoughts, or speech for them.\n"
    "Treat any input from the user as things Tortupouce says or does.\n"
)




# Constants
API_URL = "http://localhost:1234/v1/chat/completions"
SESSION_DIR = "./sessions"
MAX_HISTORY_LENGTH = 12

# Ensure session directory exists
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

# Session helpers
def session_file_path(session_id):
    return os.path.join(SESSION_DIR, f"{session_id}.json")

def save_session(session_id, history):
    with open(session_file_path(session_id), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_session(session_id):
    path = session_file_path(session_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return [{"role": "system", "content": SYSTEM_PROMPT}]


def trim_history(history):
    sys_msgs = [m for m in history if m["role"] == "system"]
    convo = [m for m in history if m["role"] != "system"]
    return sys_msgs + convo[-MAX_HISTORY_LENGTH:]

def send_to_model(messages):
    payload = {
        "model": "yes",
        "messages": messages,
        "temperature": 0.9,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Main loop
def main():
    load_memory()

    current_session = "default"
    sessions = {current_session: load_session(current_session)}

    print("🧙 Fantasy Roleplay AI with dynamic world/character memory")
    print("Type 'exit' to quit or 'end session' to reset conversation.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            save_memory()
            break

        if user_input.lower() == "end session":
            sessions[current_session] = [{"role": "system", "content": SYSTEM_PROMPT}]
            save_session(current_session, sessions[current_session])
            print("🔁 Session reset.")
            continue


        # Get AI character from previous AI response, if any
        last_response = next((m["content"] for m in reversed(sessions[current_session]) if m["role"] == "assistant"), "")
        messages = sessions[current_session].copy()

        # Extract character names from both user and AI sides
        user_character = extract_character_name(user_input)
        ai_character = extract_character_name(last_response)

        # Fallback if no names detected
        user_character = user_character or current_session
        ai_character = ai_character or user_character

        # Ensure both character files exist
        ensure_character_exists(user_character)
        ensure_character_exists(ai_character)

        # Add character memory and relevant world memory
        character_memory = get_character_summary(ai_character)
        memory_context = "\n".join(f"- {m[0]}" for m in search_memory(user_input))

        if character_memory:
            messages.insert(1, {"role": "system", "content": character_memory})
        if memory_context:
            messages.insert(1, {"role": "system", "content": f"Relevant knowledge:\n{memory_context}"})

        # Add user message
        messages.append({"role": "user", "content": user_input})

        try:
            ai_response = send_to_model(messages)
        except Exception as e:
            print(f"Error: {e}")
            continue

        print(f"\nAI: {ai_response}\n")

        # Save to session
        sessions[current_session].append({"role": "user", "content": user_input})
        sessions[current_session].append({"role": "assistant", "content": ai_response})
        sessions[current_session] = trim_history(sessions[current_session])
        save_session(current_session, sessions[current_session])

        # Update memory for both characters
        #update_character_memory(user_character, user_input)
        #update_character_memory(ai_character, ai_response)
        update_world_memory(user_input + "\n" + ai_response)

        # Extract and store facts from both sides
        for text, character in [(user_input, user_character), (ai_response, ai_character)]:
            for fact in extract_facts(text).split("\n"):
                fact = fact.strip("- ").strip()
                if fact:
                    update_character_memory(character, fact)
                    update_world_memory(fact)

        save_memory()

if __name__ == "__main__":
    main()
