from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"


async def auth_middleware(request: Request, call_next):
     # Allow preflight CORS requests
    if request.method == "OPTIONS":
        return await call_next(request);

    public_routes = [
        "/api/login",
    ]
    path = request.url.path.rstrip("/")
    # Skip authentication for public routes
    if path in public_routes:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")

    print('auth_header --------- ', auth_header);

    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"status": False, "message": "Authorization token missing"}
        )

    try:
        token = auth_header.split(" ")[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # STORE payload in request.state
        print('payload -------- ', payload);
        request.state.user = payload

    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"status": False, "message": "Invalid token"}
        )

    response = await call_next(request)

    return response
