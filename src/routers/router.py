"""
Router for example endpoints.
"""
from fastapi import APIRouter

example_router = APIRouter(prefix="/example")

@example_router.get("/")
def example_route():
    """
    Docstring for example_route
    """
    return {
        "Example": "Route"
    }
