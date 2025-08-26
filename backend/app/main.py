# Entry point for FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import lead, role, permission, auth
app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "ERP API is running"}

app.include_router(lead.router)
app.include_router(role.router)
app.include_router(permission.router)
app.include_router(auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)