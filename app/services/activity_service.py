from fastapi import APIRouter, HTTPException, Depends, Request
from app.database.db import get_db
from app.utils.response import api_response
from app.repositories.superadmin_repository import get_superadmin_details
import logging

logger = logging.getLogger(__name__)

def getSuperAdminSupportDetailsBasedOnCompany(request : Request, db = Depends(get_db)):
    try:
        # Example: getting data from token payload
        payload = request.state.user   # assuming middleware stored JWT payload here

        company_id = payload.get("company_id")
        user_id = payload.get("user_id", 0)
        final_response = {};

        if not company_id:
            logger.error(f"Error#08 in activity stream views.py | getSuperAdminSupportDetailsBasedOnCompany | Missing required fields | company_id: {company_id} ");
            return api_response(False, "Error#08 Missing required fields", {}, 400);

        req_obj = {
         "db" : db,
         "company_id": company_id
        }
        collection_count_list_response = processToGetCollectionCountBasedOnCompany(req_obj);
        final_response['collection_count_list'] = collection_count_list_response['collection_count_list'] if collection_count_list_response and collection_count_list_response.get('status') and collection_count_list_response.get('collection_count_list') else [];

        user_count_list_response = processToGetAdminUserCountBasedOnCompany(req_obj);
        final_response['admin_count_list'] = user_count_list_response['user_count_list'] if user_count_list_response and user_count_list_response.get('status') and user_count_list_response.get('user_count_list') else [];

        water_taken_count_list_response = processToGetWaterTakenCountBasedOnCompany(req_obj);
        final_response['water_taken_count_list'] = water_taken_count_list_response['water_taken_count_list'] if water_taken_count_list_response and water_taken_count_list_response.get('status') and water_taken_count_list_response.get('water_taken_count_list') else [];

        return api_response(True, "Data successfully found.", final_response, 200);

    except Exception as e:
        logger.error(f"Error#010 in activity stream views.py | getSuperAdminSupportDetailsBasedOnCompany | Unexpected error: {str(e)}");
        return api_response(False, f"Error#010 Unexpected error: {str(e)}", None, 500);

def processToGetCollectionCountBasedOnCompany(body):
    company_id = body.get('company_id');
    db = body.get('db');

    select_query = " SELECT ";
    select_query += " COUNT(DISTINCT mup.user_id) AS total_cu_count, ";
    select_query += " (COUNT(DISTINCT mu.user_id) - COUNT(DISTINCT mup.user_id)) AS total_cru_count ";
    select_query += " FROM muc_user mu ";
    select_query += " LEFT JOIN muc_user_payment mup ";
    select_query += " ON mu.company_id = mup.company_id and mu.user_id = mup.user_id ";
    select_query += " WHERE mu.company_id = %s ";

    select_params = [company_id]

    with db.cursor() as cursor:
        try:
            cursor.execute(select_query, select_params);
            collection_count_list = cursor.fetchall();
            return { "status": True, "message": "Data successfully found.", "collection_count_list": collection_count_list};

        except Exception as e:
            logger.error(f"Error#06 activity stream logs views.py | processToGetCollectionCountBasedOnCompany | SQL Error: {e} | Query: {select_query} | Params: {select_params}");
            return { "status": False, "message": "Error#06 in activity stream log views.pay."};

def processToGetAdminUserCountBasedOnCompany(body):
    company_id = body.get('company_id');
    db = body.get('db');

    select_query = " SELECT count(*) as total_users";
    select_query += " FROM muc_user";
    select_query += " WHERE company_id = %s ";

    select_params = [company_id]

    with db.cursor() as cursor:
        try:
            cursor.execute(select_query, select_params);
            user_count_list = cursor.fetchall();
            return { "status": True, "message": "Data successfully found.", "user_count_list": user_count_list};

        except Exception as e:
            logger.error(f"Error#05 activity stream views.py | processToGetAdminUserCountBasedOnCompany | SQL Error: {e} | Query: {select_query} | Params: {select_params}");
            return { "status": False, "message": "Error#05 in activity stream views.pay."};

def processToGetWaterTakenCountBasedOnCompany(body):
    company_id = body.get('company_id');
    db = body.get('db');

    superadmin_response = get_superadmin_details({"company_id": company_id, "user_id": 0, "db" : db});
    superadmin_details = superadmin_response['superadmin_data'][0] if superadmin_response and len(superadmin_response['superadmin_data']) > 0 else {}
    column_key = 'water_cane' if superadmin_details['water_department'] and superadmin_details['water_department'] == 1 else 'liters';

    select_query = " SELECT ";
    select_query += f" CAST(COALESCE(SUM({column_key}),0) AS UNSIGNED) AS total_water_cane, ";
    select_query += " COUNT(DISTINCT mu.user_id) AS total_water_users ";
    select_query += " FROM muc_water_logs mu ";
    select_query += " WHERE mu.company_id = %s ";
    select_query += f" and {column_key} > 0";

    select_params = [company_id]

    with db.cursor() as cursor:
        try:
            cursor.execute(select_query, select_params);
            water_taken_count_list = cursor.fetchall();
            return { "status": True, "message": "Data successfully found.", "water_taken_count_list": water_taken_count_list};

        except Exception as e:
            logger.error(f"Error#07 activity stream views.py | processToGetWaterTakenCountBasedOnCompany | SQL Error: {e} | Query: {select_query} | Params: {select_params}");
            return { "status": False, "message": "Error#07 in activity stream views.py."};

def getSuperAdminActivityStreamBasedOnCompany(request : Request, db = Depends(get_db)):
    try:
        payload = request.state.user   # assuming middleware stored JWT payload here
        company_id = payload.get('company_id');

        if not company_id:
            logger.error(f"Error#011 in activity stream log views.pay. | Missing required fields | company_id: {company_id} ");
            return api_response(False, "Error#011 Missing required fields", {}, status.HTTP_400_BAD_REQUEST);

        select_query = " SELECT ";
        select_query += " u.user_id, u.full_name AS user_fn, u.email AS user_email, u.mobile_number AS user_mobn,";
        select_query += " CAST(COALESCE(SUM(up.amount), 0) AS UNSIGNED) AS total_payment,";
        select_query += " CAST(COALESCE(DATEDIFF(CURDATE(), FROM_UNIXTIME(MAX(up.created_on) / 1000)), 0) AS UNSIGNED) AS payment_db_days,"
        select_query += " (CASE ";
        select_query += " WHEN MAX(up.payment_status) = 'success' THEN 'Paid' ";
        select_query += " WHEN MAX(up.payment_status) = 'error' THEN 'Error' ";
        select_query += " ELSE 'Not Paid' "
        select_query += " END) AS payment_status ";
        select_query += " FROM muc_user u ";
        select_query += " LEFT JOIN muc_user_payment up ON u.company_id = up.company_id and u.user_id = up.user_id ";
        select_query += " WHERE u.company_id = %s ";
        select_query += " GROUP BY u.user_id, u.full_name, u.email, u.mobile_number ";
        select_query += " ORDER BY u.full_name ";

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

def getYearMonthListBasedOnUserId(request : Request, db = Depends(get_db)):
        try:
            payload = request.state.user   # assuming middleware stored JWT payload here
            company_id = payload.get("company_id");
            user_id = request.query_params.get("user_id", 0);

            if not company_id or not user_id:
                logger.error(f"Error#021 in activity stream log views.pay. | Missing required fields | company_id: {company_id} | user_id: {user_id}");
                return api_response(False, "Error#021 Missing required fields", {}, status.HTTP_400_BAD_REQUEST);

            select_query = " SELECT ";
            select_query += " YEAR(FROM_UNIXTIME(created_on / 1000)) AS year, "
            select_query += " DATE_FORMAT(FROM_UNIXTIME(created_on / 1000), '%%Y-%%m') AS month_value, "
            select_query += " MIN(DATE_FORMAT(FROM_UNIXTIME(created_on / 1000), '%%M %%Y')) AS month_label "
            select_query += " FROM muc_water_logs ";
            select_query += " WHERE company_id = %s and user_id = %s ";
            select_query += " GROUP BY year, month_value "
            select_query += " ORDER BY year, month_value ";

            select_params = [company_id, user_id];

            with db.cursor() as cursor:
                try:
                    cursor.execute(select_query, select_params);
                    year_month_list = cursor.fetchall();
                    return api_response(True, "Data successfully found.", year_month_list, 200);

                except Exception as e:
                    logger.error(f"Error#022 activity stream views.pay | getYearMonthListBasedOnUserId | SQL Error: {e} | Query: {select_query} | Params: {select_params}");
                    return { "status": False, "message": "Error#022 in activity stream log views.pay."};

        except Exception as e:
            logger.error(f"Error#024 in activity stream views.pay | getYearMonthListBasedOnUserId | Unexpected error: {str(e)}");
            return api_response(False, f"Error#024 Unexpected error: {str(e)}", None, 500);
