import uvicorn
import os
from dotenv import load_dotenv, find_dotenv

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting FastAPI backend on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
