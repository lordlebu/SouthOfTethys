# Vidur Portal

An independent web application for story snippet processing and worldbuilding, powered by Hugging Face AI.

## About the Name
Vidur is a wise seer from Indian mythology, renowned for his remote vision and insight. The Norse deity Mimir, similarly, is famed for his wisdom and ability to see beyond the present—his head was consulted for advice after his death, and he guarded the Well of Wisdom. Both figures symbolize deep knowledge and remote perception, making "Vidur Portal" a fitting name for a tool that extracts hidden structure from stories.

## Features
- Paste or upload story snippets
- AI-powered extraction of character and event data using our Hugging Face model (`lordlebu/4000BCSaraswaty`)
- Modular, standalone architecture
- Can be integrated with SouthOfTethys or used independently

## Getting Started
1. Install requirements: `pip install -r requirements.txt`
2. Run the app: `streamlit run app.py`

## Model Management & Integration Strategy

- The Vidur Portal uses the Hugging Face model (`lordlebu/4000BCSaraswaty`) for extracting structured data from story snippets.
- Model pushes and updates are performed manually/local only; CI/CD does not push models or expose credentials.
- Always validate your model locally before pushing to Hugging Face (see `utils/test_hf_push.py` in the main repo).
- The portal is designed to be modular and can be integrated with SouthOfTethys or used independently for worldbuilding tasks.

## Trivia
- **Mimir (Norse):** Keeper of the Well of Wisdom, advisor to gods, his severed head continued to offer counsel.
- **Vidur (Indian):** Sage and advisor in the Mahabharata, famed for his impartiality and foresight.

---
This portal is designed for creative worldbuilders and storytellers seeking structured insights from their narratives.

## How to use

- Paste your story snippet into the portal and click "Process Snippet".
- The portal uses our Hugging Face model to extract structured data (characters, events, timeline).
- Review and export the results for integration into SouthOfTethys.

To test Vidur Portal locally:

Open a terminal and navigate to the vidur_portal directory.
Install dependencies:
pip install -r requirements.txt
Run the Streamlit app:
python -m streamlit run app.py
Open the provided local URL in your browser (usually http://localhost:8501).
Paste a story snippet and click "Process Snippet" to test the Hugging Face model integration.