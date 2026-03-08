from fastapi.responses import JSONResponse

def api_response(status=True, message="", data=None, http_code=200):

    if data is None:
        data = {}

    return JSONResponse(
        status_code = http_code,
        content = {
            "status": status,
            "http_code": http_code,
            "message": message,
            "data": data
        }
    )
