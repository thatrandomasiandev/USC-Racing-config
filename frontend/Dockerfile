# Frontend Dockerfile
# Multi-stage build for React/Next.js frontend

# Build stage
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the application
# For Next.js (uncomment if using Next.js):
RUN npm run build

# For Create React App (uncomment if using CRA):
# RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app

# Copy built files and node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/public ./public

EXPOSE 3000

# For Next.js:
CMD ["npm", "start"]

# For Create React App (uncomment if using CRA):
# CMD ["npm", "run", "serve"]


