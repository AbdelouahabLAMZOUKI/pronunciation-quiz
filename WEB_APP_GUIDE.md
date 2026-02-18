# 🎯 Pronunciation Quiz Web App - Quick Start Guide

## ✅ Fixed Issues
The app has been updated with the following fixes:

1. **Unified Interface**: Search and Quiz Word now share the same display area
2. **Feature Isolation**: When one feature is active, the other is disabled
3. **Clear Button**: Added to reset and switch between features
4. **Removed**:fixed HTML/JavaScript mismatches
5. **Removed**: Feature selection buttons (simplified interface)

## 🚀 How to Start the App

### Option 1: Use the Startup Script (Easiest)
```bash
# Just double-click this file:
start_app.bat
```

This will:
- Activate the virtual environment
- Start the backend server (port 8000)
- Start the frontend server (port 8001)
- Open the app in your browser

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```powershell
.\.venv\Scripts\Activate.ps1
cd web_app\backend\api
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
python web_app\serve_frontend.py
```

**Then open:** http://localhost:8001/templates/index.html

## 📖 How to Use the App

### Getting a Quiz Word
1. Click **"📚 Get Quiz Word"** to load a random word from your quiz list
2. This will:
   - Disable the search feature
   - Show word pronunciation (ARPAbet, IPA)
   - Show definition
   - Enable TTS playback
   - Show Clear button

### Searching for Any Word
1. Type a word in the search box
2. Click **"🔍 Search"** or press Enter
3. This will:
   - Disable the quiz word feature  
   - Fetch pronunciation and definition
   - Show "Add to Quiz" section if word is new
   - Enable TTS playback
   - Show Clear button

### Switching Between Features
- Click the **"❌ Clear"** button to reset
- This re-enables both features

### Other Features
- **🔊 Neural TTS**: Speaks the current word
- **🎵 Listen to Clip**: Plays audio clip (if available)
- **🌐 YouGlish**: Opens YouGlish for pronunciation examples
- **Generate Sentences**: Creates example sentences
- **📖 Definition / 🌳 Etymology**: Shows reference information

## 🔧 Key Files Modified

- `web_app/frontend/templates/index.html` - Unified interface
- `web_app/frontend/static/js/app.js` - Fixed element references
- `web_app/serve_frontend.py` - Frontend server
- `start_app.bat` - Easy startup script

## ℹ️ URLs

- **Frontend**: http://localhost:8001/templates/index.html
- **Backend API**: http://localhost:8000/api/health
- **API Docs**: http://localhost:8000/docs

## 🐛 Troubleshooting

**App not loading?**
- Check both servers are running
- Backend should show: uvicorn running on http://0.0.0.0:8000
- Frontend should show: serving on http://localhost:8001
- Open browser console (F12) to check for JavaScript errors

**No words showing?**
- Check that `test_words.json` exists in the project root
- Backend should load words on startup

**Features not working?**
- Make sure you clicked "Get Quiz Word" or searched for a word first
- Check browser console for errors
