# Entry point for FastAPI
from fastapi import FastAPI
from app.api.routes import lead, role, permission, auth
app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "ERP API is running"}

app.include_router(lead.router)
app.include_router(role.router)
app.include_router(permission.router)
app.include_router(auth.router)