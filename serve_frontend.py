#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend for testing the LotusHealth API
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 3000
FRONTEND_DIR = Path(__file__).parent / "frontend"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Change to frontend directory
    if not FRONTEND_DIR.exists():
        print(f"❌ Frontend directory not found: {FRONTEND_DIR}")
        print("Please ensure the frontend folder exists with index.html")
        return
    
    os.chdir(FRONTEND_DIR)
    
    # Create server
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 Frontend server started at http://localhost:{PORT}")
        print(f"📁 Serving files from: {FRONTEND_DIR.absolute()}")
        print(f"🔗 API endpoint: http://localhost:8000")
        print("\n💡 Make sure your LotusHealth API is running on port 8000")
        print("   docker-compose up --build")
        print("\n🌐 Opening browser...")
        
        # Open browser
        try:
            webbrowser.open(f"http://localhost:{PORT}")
        except:
            print(f"📱 Please manually open: http://localhost:{PORT}")
        
        print(f"\n⏹️  Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
