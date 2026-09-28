import uvicorn
import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("==================================================================")
    print("  [GatiSetu] Dynamic ETA Control Room & Operations System")
    print("  Unified Web App (Passenger + Station Board + Control Room)")
    print("  Server starting on: http://127.0.0.1:8000")
    print("==================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=[backend_dir])
