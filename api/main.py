from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scanner"))

try:
    from aggregate import get_history, get_latest_findings, get_summary, update_history
    from scan import scan
except ImportError as e:
    print(f"Error importing scanner modules: {e}")
    # Provide dummy functions for initial load if scanner is broken
    def get_history(*args, **kwargs): return []
    def get_latest_findings(*args, **kwargs): return []
    def get_summary(*args, **kwargs): return {}
    def scan(*args, **kwargs): return {}
    def update_history(*args, **kwargs): return 0

app = FastAPI(title="IaC Compliance Scanner API")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    dirs: Optional[List[str]] = None
    insecure_only: bool = False

class CustomScanRequest(BaseModel):
    code: str

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/summary")
def summary():
    try:
        return get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
def history(limit: int = 30):
    try:
        return get_history(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/findings")
def findings(limit_scans: int = 1):
    try:
        return get_latest_findings(limit_scans=limit_scans)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan")
def run_scan(request: ScanRequest):
    try:
        if request.dirs:
            tf_dirs = [Path(d) if Path(d).is_absolute() else ROOT / d for d in request.dirs]
        elif request.insecure_only:
            tf_dirs = [ROOT / "terraform" / "insecure"]
        else:
            tf_dirs = [
                ROOT / "terraform" / "insecure",
                ROOT / "terraform" / "secure",
            ]
        
        # Run the scan synchronously for now to return immediate results
        # In a production app, this might be a background task returning a job ID
        result = scan(tf_dirs)
        
        # Save to database
        update_history(result)
        
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan/custom")
def run_custom_scan(request: CustomScanRequest):
    import tempfile
    
    # 5MB Payload Limit
    if len(request.code.encode('utf-8')) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Payload too large. Limit is 5MB.")

    tmpdir = tempfile.TemporaryDirectory()
    try:
        tmp_path = Path(tmpdir.name)
        main_tf = tmp_path / "main.tf"
        main_tf.write_text(request.code)
        
        # Run scan safely isolated. Do not save to db.
        result = scan([tmp_path])
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmpdir.cleanup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
