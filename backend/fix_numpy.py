"""
Fix NumPy compatibility issue with faiss-cpu
"""
import subprocess
import sys

print("=" * 60)
print("Fixing NumPy Compatibility Issue")
print("=" * 60)
print()
print("Issue: faiss-cpu requires NumPy 1.x but NumPy 2.x is installed")
print("Solution: Downgrading NumPy to 1.26.4")
print()

try:
    print("Uninstalling NumPy 2.x...")
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "numpy", "-y"])
    
    print("\nInstalling NumPy 1.26.4...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<2.0.0"])
    
    print("\n" + "=" * 60)
    print("✓ NumPy Fixed Successfully!")
    print("=" * 60)
    print()
    print("Now restart the backend server:")
    print("  python start_server.py")
    
except subprocess.CalledProcessError as e:
    print(f"\n✗ Error: {e}")
    print("\nTry running manually:")
    print("  pip uninstall numpy -y")
    print("  pip install 'numpy<2.0.0'")
