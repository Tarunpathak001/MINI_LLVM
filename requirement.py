
import sys
import subprocess
import os

def install_requirements():
    print("🚀 Starting Project Setup...")
    
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        print(f"📦 Installing dependencies from {req_file}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
            print("✅ All requirements installed successfully.")
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements.")
            sys.exit(1)
    else:
        print(f"⚠️ {req_file} not found. Skipping dependency installation.")

    print("\n🎉 Project is ready to run!")
    print("Try running tests: python -m unittest discover -s tests")

if __name__ == "__main__":
    install_requirements()
