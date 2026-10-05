from datetime import datetime, time
import re


def parse_time(value: str) -> time:
    # Require a 12-hour time with AM or PM and accept either letter case
    match = re.fullmatch(
        r"(0?[1-9]|1[0-2]):([0-5][0-9])\s*(AM|PM)", value.strip().upper()
    )
    if match is None:
        raise ValueError("Use a time such as 9:00 AM or 2:30 PM")
    hour, minute, period = match.groups()
    # Midnight becomes 0 and noon stays 12 in the stored format
    hour = int(hour) % 12 + (12 if period == "PM" else 0)
    return time(hour, int(minute))


def format_time(value: str) -> str:
    # Leave empty saved times empty when opening old tasks
    if not value:
        return ""
    clock = datetime.strptime(value, "%H:%M").time()
    period = "AM" if clock.hour < 12 else "PM"
    return f"{clock.hour % 12 or 12}:{clock.minute:02d} {period}"
