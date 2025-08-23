import json

import streamlit as st
from snippet_processor import prompt_llm


def main():
    st.title("Vidur Portal: Story Snippet Processor")
    st.write(
        "Paste a story snippet below. The AI will extract structured character and event data."
    )

    snippet = st.text_area("Story Snippet", "", height=200)
    process = st.button("Process Snippet")

    if process and snippet.strip():
        with st.spinner("Processing with Hugging Face model..."):
            character_instruction = """
            Analyze this snippet and output JSON for `characters/`:
            - Name, faction, action, location
            - Link to existing characters (e.g., 'ally of King Thrain')
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
            try:
                char_obj = json.loads(extract_json(character_json))
                evt_obj = json.loads(extract_json(event_json))
                st.subheader("Character Data")
                st.json(char_obj)
                st.subheader("Event Data")
                st.json(evt_obj)
            except Exception as e:
                st.error(f"Error parsing model output: {e}")
                st.text("Raw character output:")
                st.code(character_json)
                st.text("Raw event output:")
                st.code(event_json)


if __name__ == "__main__":
    main()
