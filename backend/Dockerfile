FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY backend/ .

# Run the application with reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
