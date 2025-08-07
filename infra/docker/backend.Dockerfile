# Stage 1: Build the backend application
FROM python:3.11-slim-buster AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements files to leverage Docker cache
COPY telegram-automation/backend/requirements/base.txt ./requirements/base.txt
COPY telegram-automation/backend/requirements/prod.txt ./requirements/prod.txt

# Install production dependencies
RUN pip install --no-cache-dir -r requirements/base.txt -r requirements/prod.txt

# Copy the rest of the application code
COPY telegram-automation/backend/app ./app

# Stage 2: Create the final image
FROM python:3.11-slim-buster AS runner

WORKDIR /app

# Create a non-root user
RUN adduser --system --group appuser
USER appuser

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code from builder stage
COPY --from=builder /app/app ./app

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

