import datetime as _dt

from django.utils import timezone


def get_period_boundaries(date: _dt.date) -> tuple[_dt.date, _dt.date]:
    """Return the (start, end) of the 26th-to-25th OT period containing *date*.

    The OT pay period runs from the 26th of one month to the 25th of the next.
    For example, a date of 2025-01-10 falls into the period 2024-12-26 → 2025-01-25.
    """
    if date.day >= 26:
        period_start = date.replace(day=26)
    else:
        period_start = (date.replace(day=1) - _dt.timedelta(days=1)).replace(day=26)
    period_end = (period_start + _dt.timedelta(days=32)).replace(day=25)
    return period_start, period_end


def format_time_ago(created_at, *, compact: bool = False) -> str:
    """Return a human-readable "time ago" string for *created_at*.

    Parameters
    ----------
    created_at : datetime
        The timestamp to compare against the current time.
    compact : bool
        When ``True`` use short labels (``5m ago``) and fall back to
        a date string (``Jan 05, 2025``) after 7 days.
        When ``False`` use longer labels (``5 min ago``, ``2 hours ago``).
    """
    diff = timezone.now() - created_at
    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"

    if seconds < 3600:
        minutes = int(seconds / 60)
        if compact:
            return f"{minutes}m ago"
        return f"{minutes} min ago"

    if seconds < 86400:
        hours = int(seconds / 3600)
        if compact:
            return f"{hours}h ago"
        return f"{hours} hour{'s' if hours > 1 else ''} ago"

    days = int(seconds / 86400)
    if compact and seconds >= 604800:
        return created_at.strftime("%b %d, %Y")

    if compact:
        return f"{days}d ago"

    return f"{days} day{'s' if days > 1 else ''} ago"
