# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install wget for healthcheck
RUN apk add --no-cache wget

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

