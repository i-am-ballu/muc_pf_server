from fastapi import FastAPI
from app.middleware.db_check import db_check_middleware
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user_routes
from app.routes import auth_routes

app = FastAPI()

# Angular application URL
origins = [
    "http://localhost:4200",
]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],         # Allows all methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],         # Allows all headers
)

app.middleware("http")(db_check_middleware);
app.include_router(auth_routes.router, prefix="/api");
app.include_router(user_routes.router, prefix="/api");
