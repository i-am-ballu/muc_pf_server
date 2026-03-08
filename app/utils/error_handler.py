from fastapi.responses import JSONResponse

def database_error():
    return JSONResponse(
        status_code=500,
        content={"message": "Database connection failed"}
    )
