# Web App Project Structure

The `web_app/` folder contains the complete web-based refactoring of the Tkinter application.

## Directory Structure

```
web_app/
├── backend/                          # Python FastAPI backend
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py                  # FastAPI application & endpoints
│   ├── core/                        # Business logic (UI-independent)
│   │   ├── __init__.py
│   │   ├── word_service.py          # Word data abstraction
│   │   ├── progress_service.py      # Progress/stats tracking
│   │   ├── pronunciation_engine.py  # ARPAbet→IPA, sentence generation
│   │   └── audio_service.py         # Audio playback abstraction
│   └── requirements.txt             # Python dependencies
│
├── frontend/                        # HTML/CSS/JS web interface
│   ├── templates/
│   │   └── index.html              # Single-page application
│   └── static/
│       ├── css/
│       │   └── style.css           # Responsive design (mobile-first)
│       └── js/
│           └── app.js              # Frontend logic & API calls
│
└── config.json                     # Shared configuration (in parent dir)
```

## Key Architecture Principles

### 1. **Business Logic → Backend Only**
All business logic has been extracted into the `core/` modules:
- No UI framework dependencies (no tkinter imports!)
- Pure Python functions that work with dictionaries/lists
- Easy to test independently

### 2. **REST API Layer**
The `api/main.py` defines endpoints for all user actions:
- GET/POST endpoints for every Tkinter button/action
- Clean separation between logic and HTTP handling

### 3. **Frontend → Lightweight Client**
The frontend is just HTML/CSS/JS:
- Calls REST API for everything
- No business logic embedded
- Can easily be replaced with native mobile app using same API

### 4. **Easy Future Transitions**
The architecture allows:
- Swap JSON files for database (just modify `core/word_service.py`)
- Add authentication (middleware in FastAPI)
- Add real-time features with WebSockets
- Deploy mobile app reusing same API

---

## Running the Web App

### Prerequisites
- Python 3.8+
- NodeJS (optional, for frontend build tools)

### Setup Backend

```bash
# From web_app/backend/
pip install -r requirements.txt

# Copy config.json from parent directory
cp ../../../config.json ../

# Run development server
cd api/
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

### Setup Frontend

```bash
# From web_app/frontend/
# Start any HTTP server to serve files

# Option 1: Python built-in server
python -m http.server 8001 --directory .

# Option 2: Node.js http-server
npx http-server -p 8001

# Option 3: Use Live Server (VS Code extension)
```

Frontend will be available at `http://localhost:8001`

### Access the App

Open `http://localhost:8001/templates/index.html` in your browser.

---

## API Documentation

### Quiz Flow (Main Interaction)

1. **Get a word**
   ```
   POST /api/quiz/new-word?session_id=user123
   ```
   Returns: Word object with IPA conversion

2. **Submit an answer** (replaces Tkinter button click!)
   ```
   POST /api/quiz/submit-answer
   {
     "session_id": "user123",
     "feature": "stress"  // or "rhythm", "assimilation", etc.
   }
   ```
   Returns: Feedback + next word

3. **Get stats**
   ```
   GET /api/stats
   ```
   Returns: Accuracy, total rounds, per-feature stats

### Supporting Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/words` | GET | Get all words |
| `/api/words/add` | POST | Add new word |
| `/api/pronunciation/ipa/{word}` | GET | Convert ARPAbet→IPA |
| `/api/pronunciation/sentences/{word}` | GET | Generate example sentences |
| `/api/reference/definition/{word}` | GET | Fetch definition (Wikipedia) |
| `/api/reference/etymology/{word}` | GET | Fetch etymology (Wikipedia) |
| `/api/audio/synthesize` | POST | TTS synthesis (stub) |
| `/api/stats` | GET | Get stats |
| `/api/stats/reset` | POST | Reset stats |

---

## Core Modules Reference

### `word_service.py`
- **JSONWordDataSource**: Load from JSON (current)
- **APIWordDataSource**: Template for future API-based loading
- **DatabaseWordDataSource**: Template for future DB integration

### `progress_service.py`
- **LocalProgressTracker**: In-memory stats (session only)
- **FileProgressTracker**: Save to JSON file (current)
- **CloudProgressTracker**: Template for cloud sync

### `pronunciation_engine.py`
Pure business logic functions:
- `arpabet_to_ipa(arpabet_str)` - Phonetic conversion
- `generate_sentences(word, min, max)` - Example sentences
- `fetch_word_definition(word)` - Wikipedia lookup
- `fetch_word_etymology(word)` - Etymology lookup

### `audio_service.py`
- **WebAudioPlayer**: Returns file path for frontend
- **WindowsAudioPlayer**: Windows-native playback
- **WavAudioPlayer**: WAV file playback

---

## Migration: Tkinter → Web

### Before (Tkinter)
```python
def handle_guess(feature):
    """Button callback"""
    global attempts
    attempts += 1
    correct_feature = current_word["feature_id"]
    
    if feature == correct_feature:
        feedback_label.config(text="✅ Correct!", fg="green")
        progress_tracker.save_attempt(word, True, feature)
        pick_random_word()
```

### After (Web)
```javascript
// app.js
async function submitAnswer(feature) {
    const response = await fetch(`${API_BASE}/quiz/submit-answer`, {
        method: 'POST',
        body: JSON.stringify({
            session_id: SESSION_ID,
            feature: feature
        })
    });
    
    const data = await response.json();
    // UI updates from response
    showFeedback(data.feedback);
    currentWord = data.next_word;
    updateUI();
}
```

**Key Difference:**
- ✅ **Before**: Direct function calls, UI manipulation
- ✅ **After**: HTTP requests, state-driven updates

---

## Future Enhancements

### Phase 1: Database
Replace `JSONWordDataSource` with `DatabaseWordDataSource`:
```python
# Update main.py:
# word_service = DatabaseWordDataSource("postgresql://...")
```

### Phase 2: Authentication
Add FastAPI dependency injection:
```python
@app.post("/api/quiz/submit-answer")
async def submit_answer(
    session_id: str,
    feature: str,
    user: User = Depends(get_current_user)  # Add auth
):
    # Save to user's account
```

### Phase 3: Real-time Notifications
Add WebSocket support:
```python
@app.websocket("/ws/progress/{session_id}")
async def websocket_endpoint(websocket, session_id: str):
    # Push updates to frontend in real-time
```

### Phase 4: Mobile App
Reuse exact same API:
```swift
// iOS app
let response = await APIClient.shared.post("/quiz/submit-answer")
```

---

## Configuration

The app uses `../config.json` for settings:
```json
{
  "tts": {
    "provider": "google",
    "voice_name": "en-US-Neural2-D"
  },
  "data": {
    "word_file": "test_words.json"
  },
  "quiz": {
    "sentence_min": 5,
    "sentence_max": 10
  }
}
```

---

## Testing

### Test API with cURL
```bash
# Get all words
curl http://localhost:8000/api/words

# Get new word
curl -X POST http://localhost:8000/api/quiz/new-word?session_id=test1

# Submit answer
curl -X POST http://localhost:8000/api/quiz/submit-answer \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test1","feature":"stress"}'

# Get stats
curl http://localhost:8000/api/stats
```

### Test Frontend
1. Open browser console (F12)
2. Check Network tab while interacting
3. All requests should go to `/api/*` endpoints

---

## Original Tkinter App

The original code remains in the parent directory:
- `pronunciation_quiz_ui.py` - Original Tkinter UI
- `pronunciation_quiz.py` - Original quiz logic
- `services.py` - Original service layer

These are preserved for reference and future development.

---

## Notes for Developers

1. **Don't duplicate code**: Business logic stays in `core/`
2. **Backend agnostic**: Frontend doesn't care if API is FastAPI, Flask, Node.js, etc.
3. **Test independently**: Core modules are testable without web frameworks
4. **Configuration-driven**: Use `config.json` for settings, not hardcoded values
5. **Error handling**: Frontend shows user-friendly messages, backend logs errors

---

## Support for Future Transitions

This architecture supports:
- ✅ Database migration (swap `WordDataSource`)
- ✅ New TTS providers (swap audio synthesis)
- ✅ Authentication/multi-user (add middleware + database)
- ✅ Real-time features (add WebSockets)
- ✅ Mobile app (use same API)
- ✅ Desktop app (PyQt/Electron with same API)

No rewrites needed—just extend!
