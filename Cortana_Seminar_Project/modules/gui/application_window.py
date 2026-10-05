import customtkinter as ctk

from modules.core import page_handler
from modules.utility.reminder_handler import ReminderChecker


def initialize():
    app = ctk.CTk()
    app.title("Cortana")
    app.geometry("800x600")

    page_handler.initialize_pages()
    page_handler.navigate_to_page("landing")

    # Keep checking reminders even when the home page is hidden
    reminders = ReminderChecker(app)
    reminders.start()

    def close_app():
        # Stop scheduled checks before destroying the window
        reminders.stop()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", close_app)
    try:
        app.mainloop()
    finally:
        reminders.stop()
    return app
