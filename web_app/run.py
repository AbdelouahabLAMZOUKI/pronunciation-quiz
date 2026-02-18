"""
Startup script that runs both backend API and frontend together
"""
import os
import sys
import subprocess
from pathlib import Path

# Add web_app and backend to path
web_app_dir = Path(__file__).parent
backend_dir = web_app_dir / 'backend'

PORT = int(os.environ.get('PORT', 10000))

# Start the backend API on a different port (internal only)
print("🚀 Starting backend API...")
api_process = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', '8000'],
    cwd=str(backend_dir),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Give backend a moment to start
import time
time.sleep(2)

# Now start the frontend
print(f"🚀 Starting frontend on port {PORT}...")
sys.path.insert(0, str(web_app_dir))
os.chdir(str(web_app_dir))

from serve_frontend import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
