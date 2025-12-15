# Backend Dockerfile
# This is a flexible Dockerfile that can be adapted for Go, Python, or Node.js

# For Go backend (uncomment if using Go):
# FROM golang:1.21-alpine AS builder
# WORKDIR /app
# COPY go.mod go.sum ./
# RUN go mod download
# COPY . .
# RUN CGO_ENABLED=0 GOOS=linux go build -o server ./cmd/server
# 
# FROM alpine:latest
# RUN apk --no-cache add ca-certificates
# WORKDIR /root/
# COPY --from=builder /app/server .
# EXPOSE 8080
# CMD ["./server"]

# Python FastAPI backend serving frontend templates and static files
FROM python:3.11-slim

# Create app directory structure matching project layout
WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy entire project structure to maintain relative paths
COPY backend/ backend/
COPY frontend/ frontend/
COPY config/ config/

# Set working directory to backend for running the app
WORKDIR /app/backend

# Create data directory
RUN mkdir -p /app/data /app/data/motec/ld /app/data/motec/ldx

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# For Node.js backend (uncomment if using Node.js):
# FROM node:18-alpine
# WORKDIR /app
# COPY package*.json ./
# RUN npm ci --only=production
# COPY . .
# EXPOSE 3000
# CMD ["node", "server.js"]


