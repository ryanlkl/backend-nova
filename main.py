"""
Main application file
"""
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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/api/v1")

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
