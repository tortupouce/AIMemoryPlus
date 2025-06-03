
# Dynamic Memory AI (Fantasy setting but you can easely change that)

⚠️⚠️⚠️ It's Ai and I'm tired, so the saving of data works relatively well in the correct characters and use other ai instances to save the data related to them so runs slow but doesn't save full chats everywhere
it's more an exercise about coding with AI than a full thing,
and I have no proof it's using the character data correctly but it should, I'll try again later when i have more time
(Also Pierouge I know you're gonna stalk this so I used you in my test chat and yes I'm making an AI Memory system instead of studying what are you gonna do about it, fieu)

---

## Features

- 💬 Natural fantasy roleplay dialogue
- 🧠 Memory for characters & world facts using embeddings (FAISS + sentence-transformers)
- 🧍 Persistent NPC profiles
- 🌍 Dynamic world state (weather, events)
- 🗂️ Session-based conversation history

---

## Getting Started

### 1. Install Dependencies

```bash
pip install sentence-transformers faiss-cpu requests
````

---

### 2. Set Up a Local Language Model with LM Studio

#### 📦 Download LM Studio

* [https://lmstudio.ai](https://lmstudio.ai)

#### 🧠 Load a Model

1. Launch LM Studio.
2. Go to the **"Models"** tab.
3. Search for a **chat-capable** model (e.g., `mythomax-l2-13b`).
4. Download it, then open the **"Chat"** tab and activate the model.

#### 🌐 Activate the API Server

1. Go to **Settings** (gear icon).
2. Enable: **"OpenAI-compatible API server"**
3. Leave base URL as:

   ```
   http://localhost:1234/v1
   ```

> Keep LM Studio running while you use this app.

---

### 3. Run the App

```bash
python main.py
```

You can now roleplay as the protagonist and interact with dynamic NPCs.

---

## Resetting the World for a New Playthrough

To start a fresh session:

1. Delete everything in the `./world/` directory **except**:

   * `tortupouce.json` (or your player character file)

2. Delete these files (if they exist):

   * `memory.index`
   * `memory_data.json`
   * Anything in the `./sessions/` folder

---

## Changing the Player Character

1. Create a new character file in `./world/characters/` named `<your_name>.json`. Example:

   ```json
   {
     "id": "eloria",
     "facts": [],
     "relations": {}
   }
   ```

2. Open `main.py` and update the player name in the `SYSTEM_PROMPT` string:

```python
SYSTEM_PROMPT = (
    ...
    "The user plays as the main character, named Eloria.\n"
    "Eloria is not an NPC. Never invent actions, thoughts, or speech for them.\n"
    "Treat any input from the user as things Eloria says or does.\n"
)
```

---

## Memory Structure

* `./world/characters/*.json`: character memories (facts & relationships)
* `./world/world.json`: global facts and world state
* `memory_data.json` / `memory.index`: semantic memory using embeddings
* `./sessions/*.json`: saved conversation histories

---

## Notes

* User inputs are treated as actions or dialogue from the protagonist.
* The AI will always respond in-character or with narration (or it should).

---
