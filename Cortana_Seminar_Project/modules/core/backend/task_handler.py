# Read and write account-owned tasks in SQLite
from contextlib import closing
from datetime import date, datetime
from uuid import uuid4

from modules.core import database


# Report a missing task or a task owned by another account
class TaskNotFoundError(ValueError):
    pass


def _record(row):
    # Convert SQL text and integers back to Python dates and booleans
    # Turn the database row into a normal dictionary
    task = dict(row)
    task["date"] = date.fromisoformat(task.pop("task_date"))
    task["completed"] = bool(task["completed"])
    return task


def _values(task):
    # Validate before writing, even when the form already checked its inputs
    title = task["title"].strip()
    if not title:
        raise ValueError("Enter a task title")
    # Accept a Python date or convert a YYYY-MM-DD string
    day = task["date"]
    if isinstance(day, str):
        day = date.fromisoformat(day)
    if not isinstance(day, date) or isinstance(day, datetime):
        raise ValueError("Task date must be a date")
    # Both times can be blank or must form a valid same-day range
    start = task.get("start_time", "")
    end = task.get("end_time", "")
    if start or end:
        start_value = datetime.strptime(start, "%H:%M").time()
        end_value = datetime.strptime(end, "%H:%M").time()
        if end_value <= start_value:
            raise ValueError("End time must be after start time")
        start, end = start_value.strftime("%H:%M"), end_value.strftime("%H:%M")
    # Match the order of SQL placeholders and store completion as 0 or 1
    return (
        title, task.get("description", ""), day.isoformat(), start, end,
        task["priority"], task["category"], task["reminder"], task["repeat"],
        int(bool(task.get("completed", False))),
    )


# SQL handles permanent storage while the home page keeps a display copy
# Question marks receive values separately so input is never treated as SQL
# closing closes the connection and with connection saves or rolls back writes
def load_tasks(user_id):
    # Never load another account's tasks
    with closing(database.connect()) as connection:
        rows = connection.execute(
            "SELECT * FROM tasks WHERE user_id = ? ORDER BY task_date, start_time, id",
            (user_id,),
        ).fetchall()
    # Convert every saved row into the format used by the task widgets
    return [_record(row) for row in rows]


# Save a new task under the active account
def create_task(user_id, task):
    # Generate a unique ID independent of the title or date
    task_id = uuid4().hex
    values = _values(task)
    with closing(database.connect()) as connection:
        with connection:
            connection.execute("""
                INSERT INTO tasks (
                    id, user_id, title, description, task_date, start_time,
                    end_time, priority, category, reminder, repeat, completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (task_id, user_id, *values))
            # Read back the saved version for the home page
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            ).fetchone()
    return _record(row)


# Change the existing record while keeping its ID and owner
def update_task(user_id, task):
    values = _values(task)
    with closing(database.connect()) as connection:
        with connection:
            cursor = connection.execute("""
                UPDATE tasks SET
                    title = ?, description = ?, task_date = ?, start_time = ?,
                    end_time = ?, priority = ?, category = ?, reminder = ?,
                    repeat = ?, completed = ?
                WHERE id = ? AND user_id = ?
            """, (*values, task["id"], user_id))
            # Exactly one owned task must have been changed
            if cursor.rowcount != 1:
                raise TaskNotFoundError("This task does not belong to the active account")
            # Read back the saved version for the home page
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
                (task["id"], user_id),
            ).fetchone()
    return _record(row)


# Delete only the record matching both the task ID and its owner
def delete_task(user_id, task_id):
    with closing(database.connect()) as connection:
        with connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            )
            # Exactly one owned task must have been changed
            if cursor.rowcount != 1:
                raise TaskNotFoundError("This task does not belong to the active account")


# Save the checkbox state without changing the other task fields
def set_completed(user_id, task_id, completed):
    with closing(database.connect()) as connection:
        with connection:
            cursor = connection.execute(
                "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?",
                (int(bool(completed)), task_id, user_id),
            )
            # Exactly one owned task must have been changed
            if cursor.rowcount != 1:
                raise TaskNotFoundError("This task does not belong to the active account")
