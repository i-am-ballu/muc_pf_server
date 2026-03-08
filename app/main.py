from fastapi import FastAPI
from app.middleware.db_check import db_check_middleware
from app.routes import user_routes

app = FastAPI()

app.middleware("http")(db_check_middleware)
app.include_router(user_routes.router);
