"""
Frontend server using Flask
Serves index.html for all routes (SPA support)
"""

from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'frontend', 'static'))

PORT = int(os.environ.get('PORT', 8001))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def catch_all(path):
    # Serve static files if they exist
    static_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'static')
    file_path = os.path.join(static_dir, path)
    
    if os.path.isfile(file_path):
        return send_from_directory(static_dir, path)
    
    # Otherwise serve index.html (SPA routing)
    return render_template('index.html')

if __name__ == '__main__':
    print(f"✅ Frontend server running at http://localhost:{PORT}/")
    print("\nPress Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=PORT, debug=False)
