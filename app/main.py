from fastapi import FastAPI
from app.database.db import get_connection
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth_middleware import auth_middleware
from app.middleware.role_middleware import role_middleware
from app.routes import user_routes
from app.routes import auth_routes
from app.routes import activity_routes


app = FastAPI()

# run on startup
@app.on_event("startup")
def startup():

    connect_database()

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

app.middleware("http")(auth_middleware);
app.middleware("http")(role_middleware);
app.include_router(auth_routes.router, prefix="/api");
app.include_router(user_routes.router, prefix="/api");
app.include_router(activity_routes.router, prefix="/api")






# -----------------------
# DATABASE RETRY LOGIC
# -----------------------

def connect_database():

    retries = 5

    for attempt in range(retries):

        try:
            conn = get_connection()

            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")

            conn.close()

            print("Database connected successfully")
            return

        except Exception as e:

            print(f"Database connection failed attempt {attempt+1}")
            time.sleep(3)

    raise Exception("Database could not be connected")
