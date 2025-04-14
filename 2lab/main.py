import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi import FastAPI
import uvicorn

from app.api import auth, fuzzy, ws, async_fuzzy
from app.db.database import create_tables
app = FastAPI(title="Fuzzy Search API")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(fuzzy.router, prefix="/fuzzy", tags=["fuzzy"])
app.include_router(ws.router)
app.include_router(async_fuzzy.router, prefix="/fuzzy", tags=["fuzzy-async"])

@app.on_event("startup")
async def startup_event():
    create_tables()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
