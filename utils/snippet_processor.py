import json
import os

from ollama import Client

ollama_client = Client()
MODEL = "gemma3n"  # Or llama3, phi3, etc.


def prompt_llm(snippet: str, instruction: str) -> str:
    prompt = f"{instruction.strip()}\n\nSnippet: {snippet.strip()}"
    response = ollama_client.chat(
        model=MODEL, messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


def extract_and_save(snippet_path: str):
    with open(snippet_path) as f:
        snippet = f.read()

    character_instruction = """
    Analyze this snippet and output JSON for `characters/`:
    - Name, faction, action, location
    - Link to existing characters (e.g., "ally of King Thrain")
    - Add `traits` if they’re implied (e.g., brave, secretive)
    Output JSON only.
    """

    event_instruction = """
    Convert this event to timeline JSON:
    - Year, event_type (war/alliance/discovery/etc), participants
    - Label the file as `timeline/year_*.json`
    Output JSON only.
    """

    character_json = prompt_llm(snippet, character_instruction)
    event_json = prompt_llm(snippet, event_instruction)

    # Save character
    char_obj = json.loads(character_json)
    os.makedirs("characters", exist_ok=True)
    with open(char_obj["file"], "w") as f:
        json.dump(char_obj, f, indent=2)

    # Save timeline
    evt_obj = json.loads(event_json)
    os.makedirs("timeline", exist_ok=True)
    with open(evt_obj["file"], "w") as f:
        json.dump(evt_obj, f, indent=2)

    print("✅ Snippet processed and saved.")


if __name__ == "__main__":
    extract_and_save("snippets/inbox/queen_envoy.txt")
