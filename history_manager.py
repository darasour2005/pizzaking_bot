# history_manager.py - NEURAL MEMORY ENGINE
import json
import os

HISTORY_FILE = "chat_memory.json"

def save_history(user_id, messages):
    """Saves chat history to a JSON database on the server."""
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try: history = json.load(f)
            except: history = {}
    
    # Keep only last 20 messages to save space/RAM
    history[str(user_id)] = messages[-20:]
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history(user_id):
    """Loads previous chat history for a specific Telegram ID."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
                return history.get(str(user_id), [])
            except: return []
    return []
