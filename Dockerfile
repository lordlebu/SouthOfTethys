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

# Copy all necessary project files
COPY utils/ utils/
COPY timeline/ timeline/
COPY cartography/ cartography/
COPY characters/ characters/
COPY flora_fauna/ flora_fauna/
COPY docs/ docs/
COPY CONTEXT.md .
COPY README.md .

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Set default command to run all utility scripts for artifact generation
CMD ["sh", "-c", "python utils/lint_story.py && python utils/generate_timeline_mermaid.py && python utils/generate_timeline.py && python utils/generate_map.py && python utils/evolve_species.py # && python utils/snippet_processor.py # && python utils/hometown.py"]
