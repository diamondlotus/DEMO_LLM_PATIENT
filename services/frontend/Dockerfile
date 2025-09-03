# Build stage
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --omit=dev

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

<<<<<<< HEAD
# Copy built app from build stage
COPY --from=build /app/build /usr/share/nginx/html
=======
# Copy frontend files to path expected by nginx.conf
COPY frontend/ /app/frontend/

# Provide a default runtime config (can be overridden with mounted config.js)
RUN echo "window.__LOTUS_CONFIG__ = { API_BASE_URL: 'http://localhost:8003' };" > /app/frontend/config.js
>>>>>>> fa748d05b9c5aa7dd7d25d00c5cb5fd2fdc1de7a

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
