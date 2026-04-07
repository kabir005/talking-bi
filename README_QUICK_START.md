# 🚀 Talking BI - Quick Start

## ⚡ Fix & Run in 3 Steps

### 1️⃣ Fix NumPy Error

Open Command Prompt:
```cmd
cd "C:\Users\yoron\OneDrive\Desktop\Talking BI\talking-bi"
QUICK_FIX.bat
```

### 2️⃣ Restart Backend

Stop current backend (Ctrl+C), then:
```cmd
cd backend
python start_server.py
```

### 3️⃣ Access Application

Open browser: **http://localhost:5174**

---

## ✅ What's Fixed

- ❌ NumPy 2.x → ✅ NumPy 1.x (compatible with faiss-cpu)
- ❌ AttributeError → ✅ Clean startup
- ❌ Module errors → ✅ All modules working

## 📊 What You Get

- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5174
- **API Docs:** http://localhost:8000/docs

## 🎯 Quick Test

1. Open http://localhost:5174
2. Upload a CSV file
3. Generate dashboard
4. See 15-20 charts instantly!

---

**Need detailed help?** See `START_GUIDE.md` or `FIX_INSTRUCTIONS.md`
