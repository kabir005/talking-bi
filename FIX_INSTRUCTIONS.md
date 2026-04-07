# Quick Fix for NumPy Error

## The Problem

You're seeing this error:
```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6
AttributeError: _ARRAY_API not found
```

This happens because `faiss-cpu` and `chromadb` were compiled with NumPy 1.x but you have NumPy 2.x installed.

## The Solution

### Option 1: Run the Quick Fix Script (Easiest)

Open Command Prompt and run:

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi"
QUICK_FIX.bat
```

This will automatically:
1. Downgrade NumPy to 1.x
2. Reinstall faiss-cpu
3. Reinstall chromadb

### Option 2: Manual Fix

Open Command Prompt and run these commands:

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi\backend"

pip uninstall numpy -y
pip install "numpy<2.0.0"
pip install --force-reinstall faiss-cpu
pip install --force-reinstall chromadb
```

### Option 3: Use Python Script

```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi\backend"
python fix_numpy.py
```

## After Fixing

1. Stop the current backend server (Ctrl+C)
2. Restart it:
   ```cmd
   python start_server.py
   ```

You should now see:
```
✅ TALKING BI API - Ready!
📊 Dashboard generation: ENABLED
🌐 API running at: http://localhost:8000
```

Without any NumPy errors!

## Verify It's Working

### Check Backend Health
Open browser: http://localhost:8000/health

Should return:
```json
{"status":"healthy"}
```

### Check Frontend
The frontend should already be running on http://localhost:5174

If not, start it:
```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi\frontend"
npm run dev
```

## What Changed

- NumPy downgraded from 2.2.6 to 1.26.4
- This makes it compatible with faiss-cpu and chromadb
- All other functionality remains the same

## Expected Output After Fix

```
================================================================================
✅ TALKING BI API - Ready!
📊 Dashboard generation: ENABLED
🤖 Query system: ENABLED
🧠 LLM Insights: ENABLED (Groq llama-3.3-70b)
📈 Chart types: 10-12 charts per dashboard
🔴 Background tasks: Redis+Celery (if available)
================================================================================
🌐 API running at: http://localhost:8000
📚 API docs at: http://localhost:8000/docs
💡 Health check: http://localhost:8000/health
================================================================================
```

No errors, no warnings about NumPy!

## Frontend Connection

Once the backend is running without errors, the frontend will automatically connect to it at http://localhost:8000.

You can verify the connection by:
1. Opening http://localhost:5174 in your browser
2. Trying to upload a file
3. The upload should work without any CORS or connection errors

## Still Having Issues?

If you still see errors after the fix:

1. Make sure you stopped the old backend server (Ctrl+C)
2. Check that NumPy is the correct version:
   ```cmd
   pip show numpy
   ```
   Should show version 1.26.x (not 2.x)

3. If needed, reinstall all dependencies:
   ```cmd
   cd backend
   pip install -r requirements.txt
   ```
