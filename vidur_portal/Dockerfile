# Vidur Portal Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and source code
COPY vidur_portal/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY vidur_portal/ ./

# Expose Streamlit default port
EXPOSE 8501

# Entrypoint for Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
