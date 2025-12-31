# Multi-stage build for FastAPI + React frontend
FROM node:18-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ .
RUN npm run build

# Python runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Create outputs directory
RUN mkdir -p outputs/images

# Expose port (PORT will be set at runtime by Koyeb)
EXPOSE 8000

# Start application using PORT environment variable
# Use shell form (sh -c) to ensure environment variable expansion works correctly
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"

