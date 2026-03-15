from fastapi import APIRouter, Depends, Request
from app.database.db import get_db
from app.services.activity_service import getSuperAdminSupportDetailsBasedOnCompany
from app.services.activity_service import getSuperAdminActivityStreamBasedOnCompany
from app.services.activity_service import getYearMonthListBasedOnUserId

router = APIRouter(prefix="/activity_stream", tags=["Activity Stream"])

@router.get("/getSuperAdminSupportDetailsBasedOnCompany")
def get_superadmin_support_details(request: Request, db=Depends(get_db)):
    return getSuperAdminSupportDetailsBasedOnCompany(request, db)

@router.get("/getSuperAdminActivityStreamBasedOnCompany")
def get_superadmin_activity_stream_based_on_company(request: Request, db=Depends(get_db)):
    return getSuperAdminActivityStreamBasedOnCompany(request, db)

@router.get("/getYearMonthListBasedOnUserId")
def get_year_month_list_based_on_user_id(request: Request, db=Depends(get_db)):
    return getYearMonthListBasedOnUserId(request, db)
