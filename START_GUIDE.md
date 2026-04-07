# Talking BI - Complete Start Guide

## Current Status

✅ Frontend: Running on http://localhost:5174  
❌ Backend: Has NumPy compatibility error  
🔧 Fix Required: Downgrade NumPy from 2.x to 1.x

## Step-by-Step Fix & Start

### Step 1: Fix NumPy Error

Open **Command Prompt** (not PowerShell) and run:

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi"
QUICK_FIX.bat
```

OR manually:

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi\backend"
pip uninstall numpy -y
pip install "numpy<2.0.0"
pip install --force-reinstall faiss-cpu chromadb
```

### Step 2: Stop Current Backend

In the terminal where backend is running, press **Ctrl+C**

### Step 3: Restart Backend

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi\backend"
python start_server.py
```

Wait for this message:
```
✅ TALKING BI API - Ready!
🌐 API running at: http://localhost:8000
```

### Step 4: Verify Frontend

Frontend should already be running. If not:

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi\frontend"
npm run dev
```

### Step 5: Test the Connection

1. Open browser: http://localhost:5174
2. You should see the Talking BI interface
3. Try uploading a CSV file
4. If upload works, backend is connected! ✅

## What You Should See

### Backend Terminal (After Fix):
```
================================================================================
✅ TALKING BI API - Ready!
📊 Dashboard generation: ENABLED
🤖 Query system: ENABLED
🧠 LLM Insights: ENABLED (Groq llama-3.3-70b)
📈 Chart types: 10-12 charts per dashboard
================================================================================
🌐 API running at: http://localhost:8000
📚 API docs at: http://localhost:8000/docs
💡 Health check: http://localhost:8000/health
================================================================================
```

NO NumPy errors!

### Frontend Terminal:
```
VITE v5.4.21  ready in 934 ms

➜  Local:   http://localhost:5174/
➜  Network: use --host to expose
```

## Quick Health Checks

### Backend Health
```cmd
curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

### Frontend Access
Open: http://localhost:5174
Should show: Talking BI dashboard interface

### API Documentation
Open: http://localhost:8000/docs
Should show: Interactive API documentation

## Common Issues & Solutions

### Issue 1: NumPy Error Still Appears
**Solution:**
```cmd
pip show numpy
```
If version is 2.x, run:
```cmd
pip uninstall numpy -y
pip install "numpy==1.26.4"
```

### Issue 2: Port 8000 Already in Use
**Solution:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 3: Frontend Can't Connect to Backend
**Check:**
1. Backend is running on port 8000
2. No firewall blocking localhost
3. Browser console for errors (F12)

**Solution:**
- Restart both servers
- Clear browser cache (Ctrl+Shift+R)

### Issue 4: CORS Errors
**Check backend .env file:**
```
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

## File Structure

```
talking-bi/
├── backend/
│   ├── start_server.py          ← Start backend
│   ├── fix_numpy.py             ← Fix NumPy issue
│   ├── requirements.txt         ← Dependencies
│   └── main.py                  ← FastAPI app
├── frontend/
│   ├── package.json             ← Frontend config
│   └── src/                     ← React app
├── QUICK_FIX.bat                ← Run this to fix NumPy
└── START_GUIDE.md               ← This file
```

## Next Steps After Starting

1. **Upload Data**
   - Click "Upload" in sidebar
   - Drop CSV/Excel file
   - Wait for processing

2. **Generate Dashboard**
   - Go to "Datasets"
   - Click "Generate Dashboard"
   - Wait 10-15 seconds

3. **Explore Charts**
   - View 15-20 auto-generated charts
   - Hover for details
   - Interact with visualizations

4. **Ask Questions**
   - Use chat at bottom
   - Type questions about your data
   - Get AI-powered insights

## Support

### Logs Location
- **Backend:** Terminal where `python start_server.py` runs
- **Frontend:** Browser console (F12 → Console tab)

### Configuration Files
- **Backend:** `backend/.env`
- **Frontend:** `frontend/.env` (if exists)

### API Endpoints
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs
- Upload: http://localhost:8000/api/upload/file
- Datasets: http://localhost:8000/api/datasets

## Summary

1. Run `QUICK_FIX.bat` to fix NumPy
2. Restart backend: `python start_server.py`
3. Frontend should already be running
4. Open http://localhost:5174
5. Start analyzing data!

---

**Need help?** Check the terminal logs for detailed error messages.
