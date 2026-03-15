from fastapi import APIRouter, Depends, Request
from app.database.db import get_db
from app.services.user_service import getUserListBasedOnCompany
from app.services.user_service import getUserPaymentStatusDetails

router = APIRouter()
router = APIRouter(prefix="/account", tags=["Accounts"])

@router.get("/getUserListBasedOnCompany")
def get_user_list_based_on_company(request: Request, db=Depends(get_db)):
    return getUserListBasedOnCompany(request, db)

@router.post("/getUserPaymentStatusDetails")
async def get_user_payment_status_details(request: Request, db=Depends(get_db)):
    return await getUserPaymentStatusDetails(request, db)
