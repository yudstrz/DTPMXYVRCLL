import subprocess
import time
import sys
import os

# Helper to run commands in parallel
def run_dev():
    print("🚀 Starting DTPMXY Development Environment...")
    
    # Check if .env.local exists
    if not os.path.exists(".env.local"):
        print("⚠️ Warning: .env.local not found. API might fail.")

    # 1. Start Python Backend
    print("🐍 Starting Python API on port 8000...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.index:app", "--reload", "--port", "8000"],
        cwd=os.getcwd()
    )

    # 2. Wait a bit for backend
    time.sleep(2)

    # 3. Start Next.js Frontend
    print("⚛️ Starting Next.js Frontend on port 3000...")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.getcwd(),
        shell=True
    )

    try:
        frontend.wait()
        backend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        frontend.terminate()
        backend.terminate()
        sys.exit(0)

if __name__ == "__main__":
    run_dev()
