from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router,router 
from app.core.config import SNAPSHOT_DIR, CLIP_DIR

app = FastAPI(title="Fire & Smoke Detection Microservice", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@router.get("/")
async def root():
    return {"message": "Welcome to the Fire & Smoke Detection Microservice!"}
app.mount("/snapshots", StaticFiles(directory=str(SNAPSHOT_DIR)), name="snapshots")
app.mount("/clips", StaticFiles(directory=str(CLIP_DIR)), name="clips")

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)