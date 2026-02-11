"""
Main application file
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routers.agent import agent_router
from src.routers.legislation import legislation_router
from src.routers.market import market_router
from src.routers.notification import notif_router
from src.routers.payment import payment_router
from src.routers.content import content_router
from src.models.legislation import Legislation  # Ensure models are imported
from src.models.market import Market  # Ensure models are imported
from src.models.insight import Insight  # Ensure models are imported
from src.models.payment import PaymentStatistic  # Payment statistics model
from src.utils.db import Base, engine
from src.utils.scheduler import start_scheduler, stop_scheduler
from fastapi.middleware.cors import CORSMiddleware

# Try to create tables, but don't fail startup if DB is unavailable
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create tables at startup: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - handles startup and shutdown events."""
    # Startup: Start the scheduler
    start_scheduler()
    yield
    # Shutdown: Stop the scheduler
    stop_scheduler()


app = FastAPI(root_path="/api/v1", lifespan=lifespan)

## Include routers
app.include_router(agent_router)
app.include_router(legislation_router)
app.include_router(market_router)
app.include_router(payment_router)
app.include_router(content_router)
app.include_router(notif_router)

## Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def example_route():
    """
    Docstring for example_route
    """
    return {
        "Hello": "World"
    }
