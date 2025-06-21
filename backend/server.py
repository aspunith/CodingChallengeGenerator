from src.app import app

if __name__ == "__main__":
    import uvicorn #web server for FastAPI, which is an ASGI server
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
    