# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Install git for pre-commit compatibility in CI/CD
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install pre-commit for code quality hooks
RUN python -m pip install pre-commit

# Set working directory
WORKDIR /app

# Copy project files (canon lives in database/)
COPY utils/ utils/
COPY database/ database/
COPY docs/ docs/
COPY CONTEXT.md .
COPY DESIGN.md .
COPY README.md .

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Set default command to run all utility scripts for artifact generation
# The same gate CI runs, in the same order. `check_export_boundary` is here because the
# question it answers -- can lore reach the game by accident -- is not one you want to find
# the answer to only on a pull request.
CMD ["sh", "-c", "python utils/lint_story.py && python utils/check_export_boundary.py && python utils/generate_timeline_mermaid.py && python utils/generate_timeline.py && python utils/generate_atlas.py && python utils/evolve_species.py"]
