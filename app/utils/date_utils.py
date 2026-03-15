import datetime
import calendar

def get_current_month_start_date():
    now = datetime.datetime.now()
    month_start = datetime.datetime(now.year, now.month, 1)
    return int(month_start.timestamp() * 1000)


def get_current_month_end_date():
    now = datetime.datetime.now()
    last_day = calendar.monthrange(now.year, now.month)[1]
    month_end = datetime.datetime(now.year, now.month, last_day, 23, 59, 59)
    return int(month_end.timestamp() * 1000)
