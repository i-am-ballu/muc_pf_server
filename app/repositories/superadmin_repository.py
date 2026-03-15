from app.utils.response import api_response
import logging

logger = logging.getLogger(__name__)

# api for get the required payment based on user id and company_id
def get_superadmin_details(body):
    company_id = body.get("company_id");
    user_id = body.get("user_id");
    db = body.get("db");

    if not company_id:
        logger.error(f"Error#019 in water log views.pay. | Missing required fields | company_id: {company_id}");
        return api_response(False, "Error#019 Missing required fields", {}, status.HTTP_400_BAD_REQUEST);

    select_query = """ SELECT superadmin_id, water_department FROM `superadmin` WHERE superadmin_id = %s """
    select_params = [company_id]
    with db.cursor() as cursor:
        try:
            cursor.execute(select_query, select_params);
            superadmin_data = cursor.fetchall();
            return { "status": True, "message": "Data successfully found.", "superadmin_data": superadmin_data};

        except Exception as e:
            logger.error(f"Error#020 water logs views.pay | SQL Error: {e} | Query: {select_query} | Params: {select_params}");
            return { "status": False, "message": "Error#020 in water log views.pay."};
