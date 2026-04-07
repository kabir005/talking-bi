# Talking BI - Setup Instructions

## Quick Fix for Current Error

The error you're seeing is: `ModuleNotFoundError: No module named 'fuzzywuzzy'`

### Option 1: Install Missing Dependencies (Recommended)

Open a **Command Prompt** (not PowerShell) and run:

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\Talking BI\talking-bi\backend"
python install_missing.py
```

This will install all required dependencies automatically.

### Option 2: Install from requirements.txt

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\Talking BI\talking-bi\backend"
pip install -r requirements.txt
```

### Option 3: Install Just the Missing Package

```cmd
pip install fuzzywuzzy python-Levenshtein
```

## Complete Setup Process

### Backend Setup

1. Open Command Prompt (cmd.exe)
2. Navigate to backend folder:
   ```cmd
   cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\Talking BI\talking-bi\backend"
   ```
3. Install dependencies:
   ```cmd
   python install_missing.py
   ```
   OR
   ```cmd
   pip install -r requirements.txt
   ```
4. Start the backend:
   ```cmd
   python start_server.py
   ```

### Frontend Setup

1. Open a NEW Command Prompt
2. Navigate to frontend folder:
   ```cmd
   cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\Talking BI\talking-bi\frontend"
   ```
3. Install dependencies (first time only):
   ```cmd
   npm install
   ```
4. Start the frontend:
   ```cmd
   npm run dev
   ```

## Verify Everything is Running

### Backend Check
- Open browser: http://localhost:8000/health
- Should see: `{"status":"healthy"}`

### Frontend Check
- Open browser: http://localhost:5173 (or 5174 if 5173 is in use)
- Should see the Talking BI interface

## Common Issues

### Issue 1: PowerShell Execution Policy
**Error:** "running scripts is disabled on this system"

**Solution:** Use Command Prompt (cmd.exe) instead of PowerShell

### Issue 2: Port Already in Use
**Error:** "Address already in use"

**Solution:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 3: Module Not Found
**Error:** "ModuleNotFoundError: No module named 'xxx'"

**Solution:**
```cmd
cd backend
python install_missing.py
```

### Issue 4: Redis Not Running
**Error:** "Redis connection failed"

**Solution:** The start_server.py should handle Redis automatically. If not:
- Download Redis for Windows
- Or use the built-in fallback (memory broker)

## Quick Start Commands

### Start Everything (Two Command Prompts)

**Terminal 1 - Backend:**
```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\Talking BI\talking-bi\backend"
python start_server.py
```

**Terminal 2 - Frontend:**
```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\Talking BI\talking-bi\frontend"
npm run dev
```

## What Should You See?

### Backend Terminal:
```
================================================================================
✅ TALKING BI - All Services Running
================================================================================
🌐 API Server:    http://localhost:8000
📚 API Docs:      http://localhost:8000/docs
💡 Health Check:  http://localhost:8000/health
🔴 Celery Worker: Running (2 concurrent tasks)
================================================================================
```

### Frontend Terminal:
```
VITE v5.4.21  ready in 934 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

## Next Steps

Once both servers are running:
1. Open http://localhost:5173 in your browser
2. Upload a CSV file
3. Generate a dashboard
4. Start analyzing your data!

## Need Help?

Check the logs in both terminals for detailed error messages.
