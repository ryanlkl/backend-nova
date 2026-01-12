from fastapi import FastAPI
from src.routers.router import example_router

app = FastAPI(root_path="/api/v1")
## Include routers
app.include_router(example_router)

@app.get("/")
def example_route():
    return {
        "Hello": "World"
    }
