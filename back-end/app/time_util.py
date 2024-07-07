import pytz
from datetime import datetime
import logging

def convert_to_utc(date, timezone):
    try:
        local_tz = pytz.timezone(timezone)
        local_dt = local_tz.localize(date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt
    except Exception as e:
        logging.error(f"Error attempting to convert {date} to UTC with the {timezone} timezone.")
        return None

def current_time() {
    return datetime.now(pytz.utc)
}