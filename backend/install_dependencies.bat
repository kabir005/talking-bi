@echo off
echo ========================================
echo Installing Talking BI Backend Dependencies
echo ========================================

echo.
echo Installing core dependencies...
pip install fastapi uvicorn python-multipart httpx python-dotenv tenacity

echo.
echo Installing data processing...
pip install pandas numpy openpyxl sqlalchemy aiosqlite

echo.
echo Installing web scraping...
pip install playwright beautifulsoup4 lxml

echo.
echo Installing AI/ML...
pip install faiss-cpu chromadb sentence-transformers scikit-learn shap statsmodels

echo.
echo Installing visualization...
pip install matplotlib scipy networkx

echo.
echo Installing document processing...
pip install reportlab python-pptx pdfplumber python-docx pytesseract opencv-python Pillow

echo.
echo Installing text processing...
pip install fuzzywuzzy python-Levenshtein

echo.
echo Installing LLM...
pip install groq

echo.
echo Installing background tasks...
pip install celery redis kombu

echo.
echo Installing authentication...
pip install "python-jose[cryptography]" "passlib[bcrypt]" email-validator

echo.
echo Installing database drivers...
pip install psycopg2-binary pymysql

echo.
echo Installing scheduling...
pip install APScheduler pytz

echo.
echo ========================================
echo Installation Complete!
echo ========================================
pause
