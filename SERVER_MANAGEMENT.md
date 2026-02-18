# Server Management Scripts

Quick reference for managing the Pronunciation Quiz web app servers.

## Available Scripts

### 📦 `start_app.bat` - Start the App
**When to use**: First time starting the app or after a full shutdown

**What it does**:
- Activates Python virtual environment
- Starts backend server (port 8000) with auto-reload
- Starts frontend server (port 8001)
- Opens browser automatically

**Usage**: Double-click `start_app.bat`

---

### 🔄 `restart_app.bat` - Restart Everything
**When to use**: After making code changes (like adding new features)

**What it does**:
- Stops all running servers
- Waits 2 seconds
- Starts fresh backend server with auto-reload
- Starts fresh frontend server
- Shows server URLs

**Usage**: Double-click `restart_app.bat`

**Important**: Use this after:
- Editing Python files in `web_app/backend/`
- Adding new features to `feature_engine.py`
- Modifying API endpoints in `main.py`
- Making database changes

---

### ⏹️ `stop_app.bat` - Stop All Servers
**When to use**: When you're done and want to shut everything down

**What it does**:
- Finds processes using port 8000 (backend)
- Finds processes using port 8001 (frontend)
- Kills both server processes

**Usage**: Double-click `stop_app.bat`

---

## Auto-Reload Feature

The backend server now runs with `--reload` flag, which means:

✅ **Automatically reloads** when you edit Python files  
✅ **No need to restart** for most backend changes  
✅ **Faster development** workflow

**BUT**: You still need to manually restart if you:
- Add new Python packages (requirements.txt changes)
- Change environment variables or config.json
- Experience crashes or unexpected behavior

---

## How to Fix "Contractions Not Showing" Issue

If new features (like contractions) aren't showing up:

1. **Close browser tabs** showing the app
2. **Run `restart_app.bat`** (double-click)
3. **Wait for browser to open** automatically
4. **Test the feature** in Feature Guide

---

## Typical Workflow

### Development Mode
```
1. Edit code in VS Code
2. Save files
3. Backend auto-reloads (watch terminal)
4. Refresh browser to see changes
5. If issues → run restart_app.bat
```

### Daily Use
```
Morning:  Double-click start_app.bat
[Use app throughout the day]
Evening:  Double-click stop_app.bat
```

---

## Troubleshooting

### "Port already in use" error
**Solution**: Run `stop_app.bat`, wait 5 seconds, then run `start_app.bat`

### Backend shows old code
**Solution**: Run `restart_app.bat`

### Frontend won't load
**Solution**: 
1. Check both terminal windows are running
2. Visit http://localhost:8001/templates/index.html
3. If still broken, run `restart_app.bat`

### Can't stop servers normally
**Solution**: 
1. Run `stop_app.bat` 
2. If that fails, open Task Manager (Ctrl+Shift+Esc)
3. Find Python processes
4. End task for each

---

## Server URLs

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (auto-generated)
- **Frontend**: http://localhost:8001/templates/index.html
- **Health Check**: http://localhost:8000/api/health

---

## Quick Tips

💡 **Keep terminal windows visible** - Easy to see errors and logs  
💡 **Use auto-reload** - Save time during development  
💡 **Bookmark frontend URL** - Quick access in browser  
💡 **Check API docs** - Visit /docs to test endpoints  
💡 **Watch terminal output** - Errors show up here first

---

## What's Running?

To see what's running on your ports:
```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :8001
```

To see all Python processes:
```powershell
Get-Process python
```
