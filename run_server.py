#!/usr/bin/env python3
"""
Run script for CourtroomAI: Legal Minds
This script properly sets up the Python path and starts the FastAPI server.
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
project_root = Path(__file__).parent
app_dir = project_root / "app"
sys.path.insert(0, str(app_dir))

# Change to app directory
os.chdir(app_dir)

# Import and run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("🚀 Starting CourtroomAI: Legal Minds Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🌐 Frontend: Open frontend/index.html in your browser")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 