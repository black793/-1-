#!/usr/bin/env python3
"""
YouTube Subscribers Boost - Local Server
Simple HTTP server to run the script on localhost
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Configuration
PORT = 8000
HOST = 'localhost'

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Default to index.html if no file specified
        if self.path == '/':
            self.path = '/youtube-subscribers-boost/run_simple.html'
        return super().do_GET()

def start_server():
    """Start the local server"""
    print("🚀 Starting YouTube Subscribers Boost Server...")
    print(f"📡 Server will run on: http://{HOST}:{PORT}")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ Server started successfully!")
            print(f"🌐 Open your browser and go to: http://{HOST}:{PORT}")
            print("=" * 50)
            print("📋 Available files:")
            
            # List available HTML files
            html_files = list(Path('.').glob('**/*.html'))
            for html_file in html_files:
                print(f"   - http://{HOST}:{PORT}/{html_file}")
            
            print("=" * 50)
            print("⌨️  Press Ctrl+C to stop the server")
            print("=" * 50)
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://{HOST}:{PORT}')
                print("🌐 Browser opened automatically!")
            except:
                print("⚠️  Could not open browser automatically")
                print(f"   Please manually open: http://{HOST}:{PORT}")
            
            print("\n🔄 Server is running...")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Goodbye!")
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"❌ Error: Port {PORT} is already in use!")
            print(f"   Try closing other applications or use a different port")
            print(f"   You can also try: http://{HOST}:{PORT+1}")
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_server()
