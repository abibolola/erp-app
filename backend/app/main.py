# Entry point for FastAPI
from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "ERP API is running"}