FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the server
CMD ["python", "app.py"]