import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.api import routes_trains, routes_station, routes_control, routes_auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_trains.router, prefix="/api", tags=["Trains & Telemetry"])
app.include_router(routes_station.router, prefix="/api", tags=["Station Board (FIDS)"])
app.include_router(routes_control.router, prefix="/api", tags=["Control Room (OCC)"])
app.include_router(routes_auth.router, prefix="/api", tags=["Authentication & Roles"])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GatiSetu Unified Dynamic ETA Engine",
        "version": settings.VERSION,
        "mock_mode": settings.MOCK_MODE
    }

@app.get("/api/config")
@app.get("/api/map/config")
def get_map_config():
    return {
        "maptiler_api_key": settings.MAPTILER_API_KEY
    }

# Mount static frontend directories
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")
    assets_dir = os.path.join(FRONTEND_DIR, "assets")

    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
@app.get("/passenger")
@app.get("/station-board")
@app.get("/control-room")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "GatiSetu API is running. Frontend static directory not found."}

@app.get("/staff/login")
@app.get("/staff-login")
@app.get("/staff_login")
@app.get("/staff-portal")
def serve_staff_login():
    staff_login_path = os.path.join(FRONTEND_DIR, "staff_login.html")
    if os.path.exists(staff_login_path):
        return FileResponse(staff_login_path)
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "GatiSetu Staff Login page not found."}

@app.get("/download/apk")
@app.get("/api/download/apk")
@app.get("/GatiSetu.apk")
@app.get("/GatiSetu-v1.0.0.apk")
@app.get("/app-release.apk")
def download_android_apk():
    """
    Direct deployment endpoint to download the compiled GatiSetu Android APK.
    """
    candidates = [
        os.path.abspath(os.path.join(FRONTEND_DIR, "downloads", "GatiSetu-v1.0.0.apk")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "GatiSetu-v1.0.0.apk")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "android", "app", "build", "outputs", "apk", "release", "app-release.apk"))
    ]
    for apk_path in candidates:
        if os.path.exists(apk_path):
            return FileResponse(
                apk_path,
                media_type="application/vnd.android.package-archive",
                filename="GatiSetu-v1.0.0.apk"
            )
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="GatiSetu Android APK release file not found on server.")

