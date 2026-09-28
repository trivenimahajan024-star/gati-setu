import uvicorn
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

if __name__ == "__main__":
    print("==================================================================")
    print("  🚄 GatiSetu - Dynamic ETA & Railway Operations Platform")
    print("  Unified Shared Backend & Frontend on: http://127.0.0.1:8000")
    print("==================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
