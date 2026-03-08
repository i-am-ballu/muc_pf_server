from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.schemas.user_schema import LoginRequest
from app.utils.auth import create_access_token, create_refresh_token
from app.utils.response import api_response
import bcrypt
from sqlalchemy import text

router = APIRouter()

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        isSuperadmin = 0;

        if not data.email or not data.password:
            return api_response(False, "Email and password required", {}, 400);

        # check in superadmin table
        query = text("SELECT * FROM superadmin WHERE email=:email")
        result = db.execute(query, {"email": data.email})
        user = result.fetchone();

        if user:
            isSuperadmin = 1;
        else:
            query = text("SELECT * FROM muc_user WHERE email = :email")
            result = db.execute(query, {"email": data.email})
            user = result.fetchone();
            isSuperadmin = 0;

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email")

        user = dict(user._mapping)

        # password check
        if not bcrypt.checkpw(data.password.encode(), user["password"].encode()):
            return api_response(False, "Invalid password", {}, 401)

        token = create_access_token({
            "user_id": user["superadmin_id"] if isSuperadmin else user["user_id"],
            "email": user["email"]
        })

        refresh_token = create_refresh_token({
            "user_id": user["superadmin_id"] if isSuperadmin else user["user_id"],
            "email": user["email"]
        })

        re_data = {
            "id": user["superadmin_id"] if isSuperadmin else user["user_id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "company_id": user["superadmin_id"] if isSuperadmin else user["company_id"],
            "rate_per_cane": 0 if isSuperadmin else user["rate_per_cane"],
            "isSuperadmin":isSuperadmin,
            "water_department": user["water_department"] if isSuperadmin else (1 if user["company_id"] == 1 else 0),
            "access_token": token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

        return api_response(True, "User login successful", re_data, 200)
        
    except HTTPException as e:
        # rethrow HTTP exceptions
        raise e

    except Exception as e:
        print("Login Error:", e)
        return api_response(False, "Something went wrong", {}, 500)
