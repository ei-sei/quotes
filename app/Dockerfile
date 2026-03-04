# Build Flask image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY quotes.json .

# Expose port (documentation)
EXPOSE 5002

# Run Flask app
CMD ["python", "app.py"]