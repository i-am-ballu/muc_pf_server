from fastapi import APIRouter, HTTPException, Depends, Request
from app.database.db import get_db
from app.utils.response import api_response
from app.utils.json_helper import convert_decimal
from app.utils.date_utils import get_current_month_start_date, get_current_month_end_date
from app.repositories.superadmin_repository import get_superadmin_details
import logging

logger = logging.getLogger(__name__)

def getUserListBasedOnCompany(request : Request, db = Depends(get_db)):
    try:
        payload = request.state.user   # assuming middleware stored JWT payload here
        company_id = payload.get('company_id');

        if not company_id:
            logger.error(f"Error#012 in activity stream log views.pay. | Missing required fields | company_id: {company_id} ");
            return api_response(False, "Error#011 Missing required fields", {}, status.HTTP_400_BAD_REQUEST);

        select_query = " SELECT u.* ";
        select_query += " FROM muc_user u ";
        select_query += " WHERE u.company_id = %s ";

        select_params = [company_id]

        with db.cursor() as cursor:
            try:
                cursor.execute(select_query, select_params);
                activity_stream_list = cursor.fetchall();
                return api_response(True, "Data successfully found.", activity_stream_list, 200);

            except Exception as e:
                logger.error(f"Error#012 activity stream views.pay | getActivityStreamBasedOnCompany | SQL Error: {e} | Query: {select_query} | Params: {select_params}");
                return { "status": False, "message": "Error#012 in activity stream log views.pay."};

    except Exception as e:
        logger.error(f"Error#014 in activity stream views.pay | getActivityStreamBasedOnCompany | Unexpected error: {str(e)}");
        return api_response(False, f"Error#014 Unexpected error: {str(e)}", None, 500);


async def getUserPaymentStatusDetails(request : Request, db = Depends(get_db)):

    payload = request.state.user   # assuming middleware stored JWT payload here

    company_id = payload.get("company_id")

    # user_id = request.query_params.get("user_id", 0);
    # is_range_between = request.query_params.get("is_range_between", 0);
    # start_date = request.query_params.get("start_date", 0);
    # end_date = request.query_params.get("end_date", 0);


    body = await request.json();
    user_id = body.get("user_id", 0);
    is_range_between = body.get("is_range_between", 0);
    start_date = body.get("start_date", 0);
    end_date = body.get("end_date", 0);

    if not company_id or not user_id:
        logger.error(f"Error#01 in water log views.pay | User Not Found | company_id: {company_id} | user_id: {user_id}");
        return api_response(False, "Error#01 User Not Found", {}, status.HTTP_400_BAD_REQUEST);
    else:
        try:
            start_ts = start_date if start_date else get_current_month_start_date(epoch_in_ms=True);
            end_ts = end_date if end_date else get_current_month_end_date(epoch_in_ms=True);

            obj = {
                "company_id" : company_id,
                "user_id" : user_id,
                "start_ts" : start_ts,
                "end_ts" : end_ts,
                "is_range_between" : is_range_between,
            };

            data = get_user_payment_status_method(obj, db);
            return api_response(True, "Payment status fetched successfully", data, 200);
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Error#03 in water log views.pay. | Unexpected error: {str(e)} | company_id: {company_id} | user_id: {user_id}");
            return api_response(False,f"Error#03 Unexpected error: {str(e)}",None,500);


def get_user_payment_status_method(request_data, db):
     # Case 2: query params (new style)
    company_id = request_data["company_id"]
    user_id = request_data["user_id"]
    start_ts = request_data["start_ts"]
    end_ts = request_data["end_ts"]
    is_range_between = request_data["is_range_between"]

    if not company_id or not user_id:
        logger.error(f"Error#04 in water log views.pay | User Not Found | company_id: {company_id} | user_id: {user_id}");
        return api_response(False, "Error#04 User Not Found", {}, status.HTTP_400_BAD_REQUEST);
    else:
        select_query = " SELECT ";
        select_query += " mu.first_name, mu.last_name, mu.full_name as user_name, mu.company_id, mu.user_id, mu.rate_per_cane, mul.water_id, mul.liters, ";
        select_query += " mul.water_cane, IFNULL(mup.payment_id, 0) AS payment_id, IFNULL(mupd.payment_id, 0) AS distribution_id, ";
        select_query += " IFNULL(SUM(mupd.distributed_amount), 0) AS paid_amount, "
        select_query += " (CASE ";
        select_query += " WHEN IFNULL(SUM(mupd.distributed_amount), 0) = 0 THEN 'Not Paid' ";
        select_query += " WHEN IFNULL(SUM(mupd.distributed_amount), 0) < (mul.liters * 2) THEN 'Partially Paid' ";
        select_query += " ELSE 'Paid' ";
        select_query += " END) AS payment_status, ";
        select_query += " mul.created_on as log_created_on,mup.modified_on as last_payment_date, mupd.created_on as distribution_created_date ";
        select_query += " FROM muc_user mu ";
        select_query += " LEFT JOIN muc_water_logs mul ";
        select_query += " ON mu.company_id = mul.company_id AND mu.user_id = mul.user_id ";
        select_query += " LEFT JOIN muc_user_payment mup ";
        select_query += " ON mul.company_id = mup.company_id AND mul.user_id = mup.user_id AND mul.water_id = mup.water_id ";
        select_query += " LEFT JOIN muc_user_payment_distribution mupd ";
        select_query += " ON mup.company_id = mupd.company_id AND mup.payment_id = mupd.payment_id AND mul.water_id = mupd.water_id AND mul.user_id = mupd.user_id ";
        select_query += " WHERE mu.user_id = %s AND mu.company_id = %s ";

        params = [user_id, company_id]

        if is_range_between:
            select_query += " AND mul.created_on BETWEEN %s AND %s ";
            params.extend([start_ts, end_ts]);

        select_query += " GROUP BY mul.water_id, mup.payment_id ";

        with db.cursor() as cursor:
            try:
                cursor.execute(select_query, params)
                results = cursor.fetchall()
                return convert_decimal(results);
            except Exception as e:
                logger.error(f"Error#05 water logs views.pay | SQL Error: {e} | Query: {select_query} | Params: {params}");
                return [];
