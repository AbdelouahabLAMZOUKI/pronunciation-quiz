# 🚀 Web App is Live!

## Access the Application

### Frontend UI (Web Browser)
```
http://localhost:8001/templates/index.html
```

### Backend API (REST Endpoints)
```
http://localhost:8000/api/
```

---

## Quick Test Commands

### Health Check
```bash
# Backend is alive?
curl http://localhost:8000/api/health

# Or with Python:
python -c "import requests; print(requests.get('http://localhost:8000/api/health').json())"
```

### Get All Words
```bash
curl http://localhost:8000/api/words
```

### Start a Quiz (Get New Word)
```bash
# PowerShell/CMD:
curl -X POST http://localhost:8000/api/quiz/new-word?session_id=test_user

# Or Python:
python -c "import requests; r = requests.get('http://localhost:8000/api/quiz/new-word?session_id=test'); print(r.json())"
```

### Submit an Answer
```bash
# PowerShell/CMD (JSON body):
curl -X POST http://localhost:8000/api/quiz/submit-answer `
  -H "Content-Type: application/json" `
  -d '{\"session_id\": \"test_user\", \"feature\": \"stress\"}'

# Or Python:
python -c "
import requests
import json
payload = {'session_id': 'test', 'feature': 'stress'}
r = requests.post('http://localhost:8000/api/quiz/submit-answer', json=payload)
print(r.json())
"
```

### Get Stats
```bash
curl http://localhost:8000/api/stats
```

---

## What's Running

| Service | URL | Status | Purpose |
|---------|-----|--------|---------|
| **Backend API** | `http://localhost:8000` | ✅ Running | FastAPI REST endpoints |
| **Frontend Web** | `http://localhost:8001` | ✅ Running | HTML/CSS/JS UI |

---

## API Documentation

Auto-generated docs available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Architecture

```
User Browser
    ↓
http://localhost:8001/templates/index.html
    ↓
JavaScript (app.js) makes HTTP requests
    ↓
http://localhost:8000/api/*
    ↓
FastAPI Backend
    ↓
Python Business Logic (core/)
    ↓
JSON Files / Storage
```

---

## Next Steps

1. **Open in Browser**: `http://localhost:8001/templates/index.html`
2. **Click "New Word"** to load your first word
3. **Click a feature button** to answer
4. **Watch stats update** in real-time
5. **Add new words** using the form

---

## Troubleshooting

### Backend not responding?
```bash
# Check if port 8000 is in use:
netstat -ano | findstr :8000

# Kill the process:
taskkill /PID <PID> /F
```

### Frontend not loading?
- Make sure you're at `http://localhost:8001/templates/index.html` (not `/frontend/`)
- Check browser console (F12) for errors

### CORS errors?
- Backend has CORS enabled for all origins
- Frontend should connect without issues

---

## Connected to Original App?

Your original Tkinter app files are still in the parent directory:
- `pronunciation_quiz_ui.py`
- `pronunciation_quiz.py`
- `services.py`
- `config.json` (shared with web app)
- `test_words.json` (shared with web app)

**The web app uses the same data files!**

---

## Key Files

| Path | Purpose |
|------|---------|
| `web_app/backend/api/main.py` | FastAPI server (20+ endpoints) |
| `web_app/backend/core/*` | Pure business logic (no UI) |
| `web_app/frontend/templates/index.html` | App UI |
| `web_app/frontend/static/js/app.js` | Frontend logic |
| `web_app/frontend/static/css/style.css` | Responsive design |
| `config.json` | Shared configuration |
| `test_words.json` | Quiz word data |

---

**Status**: ✅ Full-stack web application running and ready to use!
