from fastapi import FastAPI
from src.routers.agent import agent_router
from src.routers.legislation import legislation_router
from src.routers.market import market_router
from src.routers.payment import payment_router

app = FastAPI(root_path="/api/v1")
## Include routers
app.include_router(agent_router)
app.include_router(legislation_router)
app.include_router(market_router)
app.include_router(payment_router)

@app.get("/")
def example_route():
    return {
        "Hello": "World"
    }
