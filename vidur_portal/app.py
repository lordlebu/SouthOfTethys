import json

import streamlit as st
from snippet_processor import prompt_llm


def main():
    st.set_page_config(page_title="Vidur Portal: Story Snippet Processor", layout="wide")
    st.title("Vidur Portal: Story Snippet Processor")
    st.markdown(
        """
    Welcome to Vidur Portal! Paste your story snippet below and process it using our Hugging Face AI model.
    The extracted structured data will be shown for review and can be integrated into the SouthOfTethys world.
    """
    )

    snippet = st.text_area("Paste your story snippet here:", height=200)
    if st.button("Process Snippet"):
        if snippet.strip():
            with st.spinner("Processing snippet..."):
                result = prompt_llm(snippet)
            st.subheader("Extracted Structured Data")
            st.json(result)
        else:
            st.warning("Please enter a story snippet to process.")

    st.markdown("---")
    st.markdown("#### How it works")
    st.markdown(
        """
    - The snippet processor uses our custom Hugging Face model to extract characters, events, and timeline data.
    - All outputs follow the SouthOfTethys world conventions (fantasy date format, cross-referenced entities).
    - For more details, see the [project README](../README.md).
    """
    )


if __name__ == "__main__":
    main()
