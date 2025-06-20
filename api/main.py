from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="GitHub Filtered Users API",
    description="API pour accéder aux utilisateurs GitHub filtrés",
    version="1.0.0"
)

app.include_router(router)
