"""
Simple HTTP server for frontend files
Run this to serve the frontend on http://localhost:8001
"""

import http.server
import socketserver
import os

PORT = 8001
DIRECTORY = os.path.join(os.path.dirname(__file__), 'frontend')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✅ Frontend server running at http://localhost:{PORT}/")
        print(f"📂 Serving files from: {DIRECTORY}")
        print(f"🌐 Open http://localhost:{PORT}/templates/index.html in your browser")
        print("\nPress Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n⛔ Server stopped")
