FROM nginx:alpine

# Copy frontend files to path expected by nginx.conf
COPY frontend/ /app/frontend/

# Provide a default runtime config (can be overridden with mounted config.js)
RUN echo "window.__LOTUS_CONFIG__ = { API_BASE_URL: 'http://localhost:8003' };" > /app/frontend/config.js

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
