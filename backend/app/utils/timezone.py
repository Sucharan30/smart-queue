from datetime import datetime, date, timezone
import zoneinfo

DEFAULT_TIMEZONE = "Asia/Kolkata"

def get_clinic_date(tz_name: str | None = None) -> date:
    """
    Derives the local calendar operating date for a clinic based on its timezone.
    Always uses UTC timestamps under the hood and derives local date cleanly.
    """
    tz_str = tz_name or DEFAULT_TIMEZONE
    try:
        tz = zoneinfo.ZoneInfo(tz_str)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")
    return datetime.now(tz).date()


def now_utc() -> datetime:
    """Returns current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)
