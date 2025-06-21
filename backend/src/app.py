from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from clerk_backend_api import Clerk
from .routes import challenge
import os

clerk_sdk = Clerk(bearer_auth=os.getenv("CLERK_API_KEY")) # Initialize Clerk SDK with your API key, which should be set in your environment variables.
app = FastAPI()

app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(challenge.router, prefix="/api")