from fastapi.responses import JSONResponse

def database_error():
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "Database connection failed",
            "data": {}
        }
    )
