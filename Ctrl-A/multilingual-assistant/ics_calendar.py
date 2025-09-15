import os
from datetime import datetime, timedelta
from typing import Optional


def _format_dt_utc(dt: datetime) -> str:
    # Treat naive datetimes as local; write as floating time (no Z) for compatibility.
    return dt.strftime("%Y%m%dT%H%M%S")


def write_event_ics(
    title: str,
    start: datetime,
    duration_minutes: int = 5,
    out_dir: str = "calendar"
) -> str:
    os.makedirs(out_dir, exist_ok=True)
    end = start + timedelta(minutes=duration_minutes)

    dtstart = _format_dt_utc(start)
    dtend = _format_dt_utc(end)
    nowstamp = _format_dt_utc(datetime.now())

    uid = f"reminder-{start.strftime('%Y%m%dT%H%M%S')}-{abs(hash(title))}@ctrl-a"
    content = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//Ctrl-A Assistant//EN\n"
        "CALSCALE:GREGORIAN\n"
        "METHOD:PUBLISH\n"
        "BEGIN:VEVENT\n"
        f"DTSTAMP:{nowstamp}\n"
        f"DTSTART:{dtstart}\n"
        f"DTEND:{dtend}\n"
        f"SUMMARY:{title}\n"
        f"UID:{uid}\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )

    filename = f"{start.strftime('%Y%m%dT%H%M%S')}-{abs(hash(title))}.ics"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


