import threading
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional


class Reminder:
    def __init__(self, run_at: datetime, note: str):
        self.run_at = run_at
        self.note = note
        self.timer: Optional[threading.Timer] = None

class ReminderScheduler:
    def __init__(self, on_reminder: Callable[[str], None]):
        self.on_reminder = on_reminder
        self._lock = threading.Lock()
        self._reminders: List[Reminder] = []

    @staticmethod
    def _next_datetime_for_hhmm(hhmm: str) -> datetime:
        now = datetime.now()
        try:
            hours, minutes = [int(x) for x in hhmm.split(":", 1)]
        except Exception:
            # Fallback: 1 minute from now
            return now + timedelta(minutes=1)

        target = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    def add_reminder(self, time_hhmm: str, note: str) -> datetime:
        run_at = self._next_datetime_for_hhmm(time_hhmm)
        delay_seconds = max((run_at - datetime.now()).total_seconds(), 0)

        reminder = Reminder(run_at=run_at, note=note)

        def _fire():
            try:
                self.on_reminder(reminder.note)
            finally:
                with self._lock:
                    if reminder in self._reminders:
                        self._reminders.remove(reminder)

        timer = threading.Timer(delay_seconds, _fire)
        reminder.timer = timer

        with self._lock:
            self._reminders.append(reminder)

        timer.daemon = True
        timer.start()

        return run_at

    def cancel_all(self) -> None:
        with self._lock:
            for r in list(self._reminders):
                try:
                    if r.timer is not None:
                        r.timer.cancel()
                except Exception:
                    pass
            self._reminders.clear()


