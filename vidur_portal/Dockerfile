# Vidur Portal Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy repo and install vidur_portal requirements
COPY . /app
RUN pip install --no-cache-dir -r vidur_portal/requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Entrypoint for Streamlit app
CMD ["streamlit", "run", "vidur_portal/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
