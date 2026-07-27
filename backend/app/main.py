import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import complaints, agent

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Customer Complaint Management System API",
    description="API for managing pharmaceutical quality complaints with AI/LangGraph integration",
    version="1.0.0"
)

# Setup CORS (allow React dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(complaints.router)
app.include_router(agent.router)

@app.get("/")
def read_root():
    return {
        "message": "AI-Powered Customer Complaint Management System API is running",
        "docs_url": "/docs",
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
