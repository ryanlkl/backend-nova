from fastapi import FastAPI
from src.example.router import example_router

app = FastAPI(root_path="/api/v1")
app.include_router(example_router)

@app.get("/")
def example_route():
    return {
        "Hello": "World"
    }
