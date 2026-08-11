# Canon API, packaged for Hugging Face Spaces (Docker SDK).
#
# Build from the repository root, not this directory -- the service reads database/ for the
# journal style examples and needs the prebuilt Chroma index:
#
#     docker build -f services/api/Dockerfile -t canon-api .
#
# The index is baked into the image rather than rebuilt at start-up. Rebuilding would pull
# the ~90MB embedding model on every cold boot and add minutes to the first request, and it
# would make the running service's answers depend on when it happened to restart. Baking it
# means canon changes reach the deployment only through a rebuild, which is the honest
# behaviour: staleness becomes a deliberate act instead of a silent one.

FROM python:3.11-slim

# HF_HOME lives in the image, not /tmp. On /tmp the 175MB embedding model is re-downloaded
# on every cold boot, and a free Space cold-boots often -- the first visitor would wait for a
# download before the first search could run.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/huggingface \
    CHROMA_PERSIST_DIR=/app/storage/chroma

WORKDIR /app

COPY services/api/requirements.txt /app/services/api/requirements.txt
RUN pip install --no-cache-dir -r /app/services/api/requirements.txt

# Bake the embedding model in. Retrieval cannot answer a single query without it, so
# downloading it lazily just moves ~175MB and a model load into the first request. This adds
# it to the image once, at build time, where nobody is waiting.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Only what the service actually reads at runtime.
COPY services/api/       /app/services/api/
COPY vidur_portal/snippet_processor.py /app/vidur_portal/snippet_processor.py
COPY database/           /app/database/

# The prebuilt index. Generate it before building:
#   REPO_DIR=. CHROMA_PERSIST_DIR=storage/chroma python services/chroma/index_chroma_service.py
COPY storage/chroma/     /app/storage/chroma/

# Spaces routes to 7860.
EXPOSE 7860

# HF_TOKEN, CANON_LLM, CANON_API_KEY and CANON_ALLOWED_ORIGINS come from the Space's
# Secrets and Variables. Never bake them into the image -- it is pullable.
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
