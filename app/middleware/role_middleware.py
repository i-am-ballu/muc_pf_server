from fastapi import Request
from fastapi.responses import JSONResponse
from app.config.api_roles import API_ROLE_MAP


async def role_middleware(request: Request, call_next):

    print("Headers --------- ", request.headers)

    if not hasattr(request.state, "user"):
        return await call_next(request)

    payload = request.state.user
    role = payload.get("role")

    endpoint = request.scope.get("endpoint")

    if endpoint:
        api_name = endpoint.__name__

        allowed_roles = API_ROLE_MAP.get(api_name)

        if allowed_roles and role not in allowed_roles:
            return JSONResponse(
                status_code=403,
                content={
                    "status": False,
                    "message": "You are not authorized to access this API"
                }
            )

    response = await call_next(request)

    return response
