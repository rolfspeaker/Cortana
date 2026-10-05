# Cortana

Cortana is a desktop task planner built with Python. It helps users organize their schedules, track tasks, and receive reminders through a character-based interface.

## Features

- Create an account and log in.
- Add tasks with a title, date, start and end times, priority, and category.
- View scheduled tasks using the calendar.
- Edit or delete tasks and mark them as complete.
- See upcoming incomplete tasks in the reminder panel.
- Receive desktop reminders with sound.
- Keep accounts and tasks saved locally between sessions.

## Built with

- **Python** — application logic, input validation, and task management.
- **CustomTkinter** — desktop interface.
- **SQLite** — local account and task storage.
- **Argon2** — password hashing.
- **Pillow and NumPy** — image handling and visual effects.
- **Pygame** — sound playback.
- **desktop-notifier** — desktop notifications.
- **email-validator** — email address validation during registration.

## Run the Windows app

If you have the packaged Windows version:

1. Extract the entire ZIP file.
2. Open the extracted **Cortana** folder.
3. Double-click **Cortana.exe**.

Keep the `_internal` folder beside `Cortana.exe`. This version does not require a separate Python installation or VS Code.

## Run from source

You need Python with Tkinter support. Open a terminal in the project folder containing `main.py`, then run these commands on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install customtkinter Pillow numpy pygame desktop-notifier email-validator argon2-cffi
.\.venv\Scripts\python.exe main.py
```

The first command creates a virtual environment, which keeps the project's Python packages together. The second installs the required packages. The third starts Cortana.

If the project already has a working virtual environment, you can start it with the last command.

## How to use Cortana

1. Launch the app and register an account, or log in to an existing account.
2. Open the task form and enter the task's details.
3. Choose its priority, category, and reminder setting, then save it.
4. Use the calendar to view your schedule.
5. Select a task to edit its details or delete it. Mark finished tasks as complete.
6. Keep Cortana running and stay logged in to receive your reminders.

Available reminder settings include the task's start time, 15 minutes before, 1 hour before, and 1 day before. A task needs a start time for a timed reminder. Completed tasks do not trigger reminders.

## Data storage

Accounts and tasks are stored in a local SQLite database. Passwords are stored as Argon2 hashes.

- **Source version:** `data/cortana.db` inside the project folder.
- **Packaged Windows version:** `%LOCALAPPDATA%\Cortana\cortana.db`.

The database is created automatically when needed. The packaged version starts with its own database, so accounts created in the source version will not automatically appear in the packaged version.

To back up your accounts and tasks, close Cortana and copy `cortana.db` to a safe location.

## Project structure

```text
Cortana_Seminar_Project/
|-- main.py              # Starts the application
|-- modules/
|   |-- core/            # Database, navigation, and account/task logic
|   |-- gui/             # Pages, task form, and interface notifications
|   `-- utility/         # Reminders, desktop alerts, sounds, and time formatting
|-- images/              # Character artwork and interface images
|-- sounds/              # Audio assets
`-- data/                # Local SQLite database
```

## Current limitations

- Reminders require Cortana to be running; closing the app stops reminder checks.
- Desktop alerts depend on the computer's notification settings.
- Accounts and tasks are stored on the current computer and do not sync across devices.
- Tasks currently do not repeat automatically.

## Troubleshooting

**A Python package is missing:** Run the package installation command above using the project's virtual environment.

**The Windows app cannot find its files:** Extract the whole ZIP and keep `_internal` beside the executable.

**A reminder did not appear:** Check that you are logged in, the task is incomplete, a start time and reminder are set, and Cortana is still running. Also check Windows notification settings.

**My accounts are missing after switching versions:** The source and packaged versions use different database locations. Check the Data storage section above.
