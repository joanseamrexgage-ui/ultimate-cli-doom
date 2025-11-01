FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 doom && chown -R doom:doom /app
USER doom

# Expose port for multiplayer
EXPOSE 8080

# Default command
CMD ["python", "main.py"]