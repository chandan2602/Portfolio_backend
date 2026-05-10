from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from database import Base, engine
from login import router as login_router

# Try to import optional routers
try:
    from call import router as call_router
    CALL_AVAILABLE = True
except Exception as e:
    print(f"Call router not available: {e}")
    CALL_AVAILABLE = False

try:
    from rag_api import router as rag_router
    RAG_AVAILABLE = True
except Exception as e:
    print(f"RAG router not available: {e}")
    RAG_AVAILABLE = False

# Create tables on startup
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization failed: {e}")

app = FastAPI(title="Portfolio Login API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Portfolio API is running", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(login_router, prefix="/api")

if CALL_AVAILABLE:
    app.include_router(call_router, prefix="/api")

if RAG_AVAILABLE:
    app.include_router(rag_router, prefix="/api")
