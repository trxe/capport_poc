import datetime as dt

import pytz

from capport.tools.constants import DEFAULT_TIMEZONE, RECOGNIZED_DT_FORMATS


def tz(timezone: str = DEFAULT_TIMEZONE) -> dt.tzinfo:
    return pytz.timezone(timezone)


def now(timezone: str = DEFAULT_TIMEZONE) -> dt.datetime:
    return dt.datetime.astimezone(tz(timezone))


def strptime(datetime_str: str) -> dt.datetime:
    for fmt in RECOGNIZED_DT_FORMATS:
        try:
            datetime_val = dt.datetime.strptime(datetime_str, fmt)
            return datetime_val
        except Exception:
            continue
    raise Exception(
        f"Invalid datetime: failed to parse '{datetime_str}' as any of [{RECOGNIZED_DT_FORMATS}]"
    )
