import streamlit as st
from snippet_processor import (
    CHROMA_ENABLED,
    CHROMA_PERSIST_DIR,
    DEFAULT_INSTRUCTION,
    prompt_llm,
    retrieve,
)


def render_hit(hit: dict) -> None:
    meta = hit.get("meta", {})
    source = meta.get("source", "unknown")
    entity_id = meta.get("entity_id", "—")
    name = meta.get("name") or meta.get("title") or ""
    distance = hit.get("distance")

    header = f"`{source}` — **{entity_id}**"
    if name:
        header += f" ({name})"
    if distance is not None:
        header += f" · distance {distance:.4f}"
    st.markdown(header)
    st.text(hit.get("text", ""))
    st.divider()


def render_retrieval() -> None:
    st.subheader("Ask the canon")
    st.caption(
        "Semantic search over the Chroma index built from `database/`. "
        "No language model involved — this is retrieval only."
    )

    if not CHROMA_ENABLED:
        st.error(
            "Chroma is not installed. Run "
            "`pip install -r services/chroma/requirements.txt`."
        )
        return

    query = st.text_input(
        "Query", placeholder="Who is Kavik Stoneheart?", key="canon_query"
    )
    k = st.slider("Results", min_value=1, max_value=10, value=5)

    if not st.button("Search canon"):
        return
    if not query.strip():
        st.warning("Enter a query first.")
        return

    with st.spinner("Searching..."):
        hits = retrieve(query, k=k)

    if not hits:
        st.warning(
            f"No results. Is the index built at `{CHROMA_PERSIST_DIR}`? "
            "Build it with `python services/chroma/index_chroma_service.py`."
        )
        return

    st.success(f"{len(hits)} results")
    for hit in hits:
        render_hit(hit)


def render_snippet_processor() -> None:
    st.subheader("Process a story snippet")
    st.caption(
        "Extracts structured data with the Hugging Face model. "
        "The first run downloads model weights and needs network access."
    )

    snippet = st.text_area("Paste your story snippet here:", height=200)
    use_retrieval = st.checkbox(
        "Ground the prompt with retrieved canon", value=CHROMA_ENABLED
    )
    enable_generation = st.checkbox(
        "Enable model generation (downloads weights)", value=False
    )

    if not st.button("Process Snippet"):
        return
    if not snippet.strip():
        st.warning("Please enter a story snippet to process.")
        return
    if not enable_generation:
        st.info(
            "Generation is off. Tick 'Enable model generation' to run the model, "
            "or use 'Ask the canon' above for retrieval only."
        )
        return

    with st.spinner("Processing snippet..."):
        result = prompt_llm(
            snippet, DEFAULT_INSTRUCTION, use_retrieval=use_retrieval
        )
    st.subheader("Extracted Structured Data")
    st.write(result)


def main():
    st.set_page_config(
        page_title="Vidur Portal: Story Snippet Processor", layout="wide"
    )
    st.title("Vidur Portal: Story Snippet Processor")
    st.markdown(
        """
    Welcome to Vidur Portal! Search the SouthOfTethys canon directly, or paste a story
    snippet to extract structured data with our Hugging Face model.
    """
    )

    render_retrieval()
    st.markdown("---")
    render_snippet_processor()

    st.markdown("---")
    st.markdown("#### How it works")
    st.markdown(
        """
    - **Ask the canon** queries a Chroma index built from `database/**/*.json`
      by `services/chroma/index_chroma_service.py`. Each result cites its source file.
    - **Process a story snippet** uses our custom Hugging Face model to extract
      characters, events, and timeline data, optionally grounded in retrieved canon.
    - All outputs follow the SouthOfTethys world conventions (fantasy date format,
      cross-referenced entities).
    - For more details, see the [project README](../README.md).
    """
    )


if __name__ == "__main__":
    main()
