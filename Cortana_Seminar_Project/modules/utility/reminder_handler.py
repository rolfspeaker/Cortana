from contextlib import closing
from datetime import datetime, timedelta
import sqlite3

from modules.core import database
from modules.core.backend import account_handler, task_handler
from modules.utility import desktop_alert
from modules.utility.time_format import format_time

from modules.utility import sound_service

# These offsets are subtracted from the task start time
REMINDER_OFFSETS = {
    "At start time": timedelta(),
    "15 minutes before": timedelta(minutes=15),

    "1 hour before": timedelta(hours=1),
    "1 day before": timedelta(days=1),
}


def reminder_window(task):
    # Completed tasks and None reminders do not produce alerts
    offset = REMINDER_OFFSETS.get(task.get("reminder"))
    if task.get("completed") or offset is None or not task.get("start_time"):
        return None
    start = datetime.combine(
        task["date"], datetime.strptime(task["start_time"], "%H:%M").time()
    )
    due = start - offset
    # Early reminders remain eligible until the task starts
    # At-start reminders allow five minutes for polling or reopening the app
    expires = start if offset else start + timedelta(minutes=5)
    return due, expires


class ReminderChecker:
    def __init__(self, master):
        self.master = master
        self._timer = None
        self._running = False
        # Track alerts still being sent so another check cannot queue them again
        self._pending = {}
        # Also remember successes if recording them in SQL temporarily fails
        self._sent = set()

    def start(self):
        if self._running:
            return
        # A separate table remembers which reminder occurrences were submitted
        with closing(database.connect()) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS reminder_deliveries (
                        user_id INTEGER NOT NULL,
                        task_id TEXT NOT NULL,
                        reminder_at TEXT NOT NULL,
                        PRIMARY KEY (user_id, task_id, reminder_at),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                    )
                """)
        desktop_alert.start()
        self._running = True
        self._tick()

    def stop(self):
        # Cancel the Tk timer before the main window is destroyed
        self._running = False
        if self._timer is not None:
            self.master.after_cancel(self._timer)
            self._timer = None

    def _finish_pending(self):
        # Check Futures on the GUI thread without waiting for unfinished work
        for key, future in list(self._pending.items()):
            if not future.done():
                continue
            del self._pending[key]
            try:
                future.result()
            except Exception as error:
                # Failed sends are not marked as sent and can be tried again
                print(f"Desktop reminder failed: {error}")
                continue
            self._sent.add(key)
            try:
                with closing(database.connect()) as connection:
                    with connection:
                        connection.execute("""
                            INSERT OR IGNORE INTO reminder_deliveries
                                (user_id, task_id, reminder_at)
                            VALUES (?, ?, ?)
                        """, key)
            except sqlite3.Error as error:
                print(f"Could not record desktop reminder: {error}")

    def check(self, now=None):
        self._finish_pending()
        account = account_handler.current_account
        if account is None:
            return
        now = now or datetime.now()
        user_id = account["id"]
        # Read fresh SQL records so edits and deletions take effect automatically
        tasks = task_handler.load_tasks(user_id)
        with closing(database.connect()) as connection:
            rows = connection.execute(
                "SELECT task_id, reminder_at FROM reminder_deliveries WHERE user_id = ?",
                (user_id,),
            ).fetchall()
        recorded = {(user_id, row["task_id"], row["reminder_at"]) for row in rows}
        for task in tasks:
            try:
                window = reminder_window(task)
            except (ValueError, TypeError):
                # Ignore malformed dates or times instead of stopping every reminder
                continue
            if window is None:
                continue
            due, expires = window
            if not due <= now < expires:
                continue
            # A changed reminder time creates a new occurrence for the same task
            key = (user_id, task["id"], due.isoformat())
            if key in recorded or key in self._pending or key in self._sent:
                continue
            start = datetime.combine(
                task["date"], datetime.strptime(task["start_time"], "%H:%M").time()
            )
            message = (
                f"{task['title']}\n"
                f"{start:%b %d, %Y} at {format_time(task['start_time'])} | "
                f"{task.get('category', 'Other')}"
            )
            self._pending[key] = desktop_alert.send_alert(
                "Cortana Reminder", message, task.get("priority", "Medium"),
                # Play the voiceline when sending finishes rather than at the next poll
                on_sent=lambda: sound_service.play_voiceline("down_here_chief"),
            )

    def _tick(self):
        self._timer = None
        if not self._running:
            return
        try:
            self.check()
        except (sqlite3.Error, ValueError) as error:
            print(f"Could not check desktop reminders: {error}")
        finally:
            # after schedules another check without pausing the GUI
            if self._running:
                self._timer = self.master.after(10000, self._tick)
