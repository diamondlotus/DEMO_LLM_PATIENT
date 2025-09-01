FROM nginx:alpine

# Copy frontend files to path expected by nginx.conf
COPY frontend/ /app/frontend/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
