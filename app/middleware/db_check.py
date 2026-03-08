from fastapi import Request
from app.database.db import engine
from app.utils.error_handler import database_error

async def db_check_middleware(request: Request, call_next):
    try:
        conn = engine.connect()
        conn.close()
    except Exception:
        return database_error()

    response = await call_next(request)
    return response
