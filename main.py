from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from login import router as login_router
from call import router as call_router
from rag_api import router as rag_router

# Create tables on startup
Base.metadata.create_all(bind=engine)

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
app.include_router(call_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
