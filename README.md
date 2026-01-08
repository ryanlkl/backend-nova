# backend-nova
## Project Initialisation
In your terminal, run:
```python -m venv venv```
```venv/Scripts/Activate```
```pip install -r requirements.txt```

To run the ChromaDB Server:
```chroma run --host localhost --port 8080 --path ./my_chroma_data```

To run FastAPI Backend:
```uvicorn main:app --reload --host 8000```