from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import api_router

app = FastAPI(title="Chat API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Chat API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


