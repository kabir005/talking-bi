"""
Quick installer for missing dependencies
"""
import subprocess
import sys

packages = [
    'fuzzywuzzy',
    'python-Levenshtein',
    'fastapi',
    'uvicorn',
    'python-multipart',
    'httpx',
    'python-dotenv',
    'tenacity',
    'pandas',
    'numpy<2.0.0',
    'openpyxl',
    'sqlalchemy',
    'aiosqlite',
    'playwright',
    'beautifulsoup4',
    'lxml',
    'faiss-cpu',
    'chromadb',
    'sentence-transformers',
    'scikit-learn',
    'shap',
    'statsmodels',
    'networkx',
    'reportlab',
    'python-pptx',
    'matplotlib',
    'scipy',
    'groq',
    'celery',
    'redis',
    'kombu',
    'python-jose[cryptography]',
    'passlib[bcrypt]',
    'email-validator',
    'pdfplumber',
    'python-docx',
    'pytesseract',
    'opencv-python',
    'Pillow',
    'psycopg2-binary',
    'pymysql',
    'APScheduler',
    'pytz'
]

print("=" * 60)
print("Installing Missing Dependencies")
print("=" * 60)

for package in packages:
    print(f"\nInstalling {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} installed successfully")
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")

print("\n" + "=" * 60)
print("Installation Complete!")
print("=" * 60)
