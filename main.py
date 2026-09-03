import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 1. Load environment variables before importing application modules
load_dotenv(override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 2. Import database connection, models, and routers
from database.connection import engine, Base
import models  # Registers SQLAlchemy models for metadata creation
from routers import auth_router, user_router


# 3. Modern FastAPI Lifespan Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified successfully.")
    except Exception as e:
        print(f"Database connection warning/error: {e}")
    yield
    # Shutdown logic (if any)


# 4. Initialize FastAPI App
app = FastAPI(
    title=os.getenv("APP_NAME", "Pickles Business API"),
    description="Backend API for Pickles E-Commerce Platform",
    version="1.0.0",
    lifespan=lifespan
)

# 5. Add CORS Middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. Include API Routers
app.include_router(auth_router)
app.include_router(user_router)


# 7. Base Health Check Endpoint
@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "status": "online",
        "app_name": os.getenv("APP_NAME", "Pickles Business API"),
        "docs_url": "/docs"
    }
