# Build month grids and access account-owned task storage
import calendar
import sqlite3

from modules.gui.add_task_widget import AddTaskWidget
from modules.core.backend import account_handler, task_handler

# Track dates and supply dimensions when requesting a layout refresh
from datetime import date, datetime, time, timedelta
from types import SimpleNamespace

# Use CTk widgets and Pillow for the gradient image
import customtkinter as ctk
from PIL import Image, ImageTk

import modules.gui.notification as notification_handler
import random

# Main calendar page with tasks saved in SQL and cached for display
class HomePage(ctk.CTkFrame):
    def __init__(self):
        # Attach this page to the existing app window
        super().__init__(master=None, corner_radius=0)

        # The canvas holds the gradient and positions the CTk cards
        self.canvas = ctk.CTkCanvas(
            self, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Keep the image alive and avoid redrawing for unchanged dimensions
        self._background = None
        self._last_size = None

        # Start on today with no example account data
        self.selected_date = date.today()
        self.year = self.selected_date.year
        self.month = self.selected_date.month
        # This display cache groups saved tasks by date
        # SQL remains the permanent source when the app restarts
        self.tasks_by_date = {}
        self._task_user_id = None

        # Shared lavender colors for cards and controls
        self.card_color = "#E4ADF0"
        self.accent_color = "#BA7FC7"

        # Header controls and page title
        self.menu_btn = ctk.CTkButton(
            self.canvas,
            text="☰",
            width=42,
            height=42,
            corner_radius=14,
            fg_color="#A25BEF",
            hover_color="#9450DC",
            text_color="white",
            font=ctk.CTkFont(size=27),
            command=self.open_menu,
        )
        # create_window embeds a real widget and returns its canvas item ID
        # anchor="nw" positions it using its top-left corner
        self._menu_window = self.canvas.create_window(
            0, 0, window=self.menu_btn, anchor="nw"
        )

        self.title = self.canvas.create_text(
            0, 0,
            text="Calendar",
            fill="white",
            anchor="w",
            font=("Segoe UI", -30, "bold"),
        )
        self.subtitle = self.canvas.create_text(
            0, 0,
            text="Plan ahead. Stay productive",
            fill="white",
            anchor="w",
            font=("Segoe UI", -14),
        )

        self.profile_btn = ctk.CTkButton(
            self.canvas,
            text="●",
            width=44,
            height=44,
            corner_radius=22,
            fg_color="#DCE3E7",
            hover_color="#CBD4DA",
            text_color="#76828B",
            font=ctk.CTkFont(size=28),
            command=self.open_profile,
        )
        self._profile_window = self.canvas.create_window(
            0, 0, window=self.profile_btn, anchor="ne"
        )

        # Calendar card with seven equally sized weekday columns
        self.calendar_card = ctk.CTkFrame(
            self.canvas,
            fg_color=self.card_color,
            bg_color=self.card_color,
            corner_radius=22,
        )
        self.calendar_card.grid_columnconfigure(
            tuple(range(7)), weight=1, uniform="days"
        )

        # Month navigation buttons call change_month with an offset
        self.previous_btn = ctk.CTkButton(
            self.calendar_card,
            text="<",
            width=32,
            height=30,
            fg_color="transparent",
            hover_color=self.accent_color,
            command=lambda: self.change_month(-1),
        )
        self.previous_btn.grid(
            row=0, column=0, pady=(16, 8)
        )

        self.month_label = ctk.CTkLabel(
            self.calendar_card,
            text="",
            text_color="white",
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        self.month_label.grid(
            row=0, column=1, columnspan=5, pady=(16, 8)
        )

        self.next_btn = ctk.CTkButton(
            self.calendar_card,
            text=">",
            width=32,
            height=30,
            fg_color="transparent",
            hover_color=self.accent_color,
            command=lambda: self.change_month(1),
        )
        self.next_btn.grid(
            row=0, column=6, pady=(16, 8)
        )

        # enumerate supplies both the column number and weekday name
        for column, name in enumerate(
            ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        ):
            ctk.CTkLabel(
                self.calendar_card,
                text=name,
                text_color="white",
                font=ctk.CTkFont(size=13),
            ).grid(row=1, column=column, pady=(0, 6))

        # Retain day buttons so they can be replaced when the month changes
        self._day_buttons = []
        self._calendar_window = self.canvas.create_window(
            0, 0, window=self.calendar_card, anchor="nw"
        )

        # Task card contains the selected date, Add Task button, and task rows
        self.tasks_card = ctk.CTkFrame(
            self.canvas,
            fg_color=self.card_color,
            bg_color=self.card_color,
            corner_radius=22,
        )
        self.tasks_card.grid_columnconfigure(0, weight=1)

        self.date_label = ctk.CTkLabel(
            self.tasks_card,
            text="",
            text_color="white",
            anchor="w",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.date_label.grid(
            row=0, column=0, sticky="ew",
            padx=(18, 10), pady=(16, 10),
        )

        self.add_task_btn = ctk.CTkButton(
            self.tasks_card,
            text="+ Add Task",
            width=90,
            height=28,
            corner_radius=14,
            fg_color=self.accent_color,
            hover_color="#AC70BA",
            text_color="white",
            command=self.add_task,
        )
        self.add_task_btn.grid(
            row=0, column=1,
            padx=(0, 18), pady=(16, 10),
        )

        # Task rows are rebuilt here whenever the selected date changes
        # Scroll task rows inside the card instead of growing the whole page
        self.task_list = ctk.CTkScrollableFrame(
            self.tasks_card,
            fg_color=self.card_color,
            corner_radius=14,
            height=220,
            scrollbar_fg_color=self.card_color,
            scrollbar_button_color=self.accent_color,
            scrollbar_button_hover_color="#AC70BA",
        )
        self.tasks_card.grid_rowconfigure(1, weight=1)
        self.task_list.grid(
            row=1, column=0, columnspan=2,
            sticky="nsew", padx=16, pady=(0, 18),
        )
        self.task_list.grid_columnconfigure(0, weight=1)

        self._tasks_window = self.canvas.create_window(
            0, 0, window=self.tasks_card, anchor="nw"
        )

        # Show up to three upcoming tasks across the full page width
        self.reminder_card = ctk.CTkFrame(
            self.canvas,
            fg_color=self.accent_color,
            bg_color=self.card_color,
            border_color=self.card_color,
            border_width=9,
            corner_radius=24,
        )
        self.reminder_card.grid_columnconfigure(0, weight=1)

        self.reminder_heading = ctk.CTkLabel(
            self.reminder_card,
            text="Upcoming Reminders · Next 7 Days",
            text_color="white", anchor="w",
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        self.reminder_heading.grid(
            row=0, column=0, sticky="ew", padx=24, pady=(20, 6),
        )

        self.reminder_text = ctk.CTkLabel(
            self.reminder_card,
            text="No incomplete tasks due in the next 7 days.",
            text_color="white",
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.reminder_text.grid(
            row=1, column=0, sticky="ew", padx=24, pady=(0, 22),
        )
        self._reminder_window = self.canvas.create_window(
            0, 0, window=self.reminder_card, anchor="nw"
        )

        # Draw initial content and connect resize and scrolling events
        self.draw_calendar()
        self.show_tasks()
        self.canvas.bind("<Map>", self._on_page_shown, add="+")
        self.canvas.bind("<Configure>", self._layout)
        self.canvas.bind("<MouseWheel>", self._scroll)
        self._bind_scroll(self.calendar_card)
        self._bind_scroll(self.tasks_card)
        self._bind_scroll(self.reminder_card)
        self._reminder_timer = self.after(60000, self._refresh_reminder_clock)

    # Rebuild date buttons for the displayed month
    def draw_calendar(self):
        for button in self._day_buttons:
            button.destroy()
        self._day_buttons.clear()
        # Rebuild the legend below the month grid even for six-week months
        legend = getattr(self, "_priority_legend", None)
        if legend is not None:
            legend.destroy()

        self.month_label.configure(
            text=f"{calendar.month_name[self.month]} {self.year}"
        )

        # Start weeks on Sunday and include adjoining dates to fill each week
        weeks = calendar.Calendar(
            firstweekday=6
        ).monthdatescalendar(self.year, self.month)

        # Compare full dates so past months and years are also blocked
        today = date.today()
        for row, week in enumerate(weeks, start=2):
            for column, day in enumerate(week):
                past = day < today
                selected = day == self.selected_date and not past
                priority_color = self._day_priority_color(day)

                button = ctk.CTkButton(
                    self.calendar_card,
                    text=str(day.day),
                    width=34,
                    height=34,
                    corner_radius=17,
                    fg_color="#FF9150" if selected else priority_color,
                    hover_color=self.accent_color,
                    # Past dates stay visible but cannot be clicked
                    state="disabled" if past else "normal",
                    text_color_disabled="white" if priority_color != "transparent" else "#C18DCF",
                    text_color=(
                        "white" if selected or priority_color != "transparent" or day.month == self.month else "#F4D8F9"
                    ),
                    font=ctk.CTkFont(size=13),
                    # Capture this specific date so every button has its own callback
                    command=lambda chosen=day: self.select_day(chosen),
                )
                button.grid(
                    row=row, column=column,
                    padx=4, pady=(2, 6),
                )
                button.bind("<MouseWheel>", self._scroll, add="+")
                self._day_buttons.append(button)

        # Keep the priority legend centered beneath the final calendar week
        self._priority_legend = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        self._priority_legend.grid(
            row=len(weeks) + 2, column=0, columnspan=7, pady=(10, 16),
        )
        for column, (priority, color) in enumerate(self._priority_colors().items()):
            ctk.CTkLabel(
                self._priority_legend, text="●", text_color=color,
                font=ctk.CTkFont(size=22), width=22,
            ).grid(row=0, column=column * 2, padx=(8, 3))
            ctk.CTkLabel(
                self._priority_legend, text=priority, text_color="white",
                font=ctk.CTkFont(size=12),
            ).grid(row=0, column=column * 2 + 1, padx=(0, 8))

    # Use the same colors for both the legend and date highlights
    @staticmethod
    def _priority_colors():
        return {"Low": "#189F9A", "Medium": "#3984ED", "High": "#E34B59"}

    # If several tasks share a day, show the highest priority
    def _day_priority_color(self, day):
        ranks = {"Low": 1, "Medium": 2, "High": 3}
        tasks = self.tasks_by_date.get(day, [])
        if not tasks:
            return "transparent"
        priority = max(
            (task.get("priority", "Medium") for task in tasks),
            key=lambda value: ranks.get(value, 2),
        )
        return self._priority_colors().get(priority, "#3984ED")

    # Move across months and years without special December or January cases
    def change_month(self, offset):
        month_index = self.year * 12 + self.month - 1 + offset
        # divmod returns the year and remaining month index
        self.year, month_index = divmod(month_index, 12)
        self.month = month_index + 1
        self.draw_calendar()
        self._reflow()

    # Select a date and update its calendar highlight and task list
    def select_day(self, day):
        # Also reject past dates when another function calls this method
        if day < date.today():
            return
        self.selected_date = day
        self.year, self.month = day.year, day.month
        self.draw_calendar()
        self.show_tasks()
        self._reflow()

    # Display only tasks belonging to the selected date
    def show_tasks(self):
        self.show_reminders()
        self.date_label.configure(
            text=(
                f"{self.selected_date:%A}, "
                f"{self.selected_date:%B} "
                f"{self.selected_date.day}, "
                f"{self.selected_date.year}"
            )
        )

        # Clear displayed rows without deleting the stored task records
        for widget in self.task_list.winfo_children():
            widget.destroy()

        # Use an empty list when the selected date has no tasks
        tasks = self.tasks_by_date.get(self.selected_date, [])

        if not tasks:
            ctk.CTkLabel(
                self.task_list,
                text="No tasks scheduled",
                text_color="white",
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, pady=26)
            return

        # Build one row per task from its saved dictionary
        for index, task in enumerate(tasks):
            title = task["title"]
            time = (
                f'{task["start_time"]} - {task["end_time"]}'
                if task.get("start_time") else "No time set"
            )
            # Show the saved category beside the time range
            details = f'{time} | {task.get("category", "Other")}'
            priority = task["priority"]
            row = ctk.CTkFrame(
                self.task_list,
                fg_color="white",
                corner_radius=14,
            )
            row.grid(
                row=index, column=0,
                sticky="ew", pady=5,
            )
            row.grid_columnconfigure(1, weight=1)

            # The checkbox updates this task's completion state
            checkbox = ctk.CTkCheckBox(
                row,
                text="",
                command=lambda record=task: self.toggle_task(record),
                width=22,
                checkbox_width=18,
                checkbox_height=18,
                border_width=1,
                border_color="#DAB4E6",
                fg_color=self.accent_color,
                hover_color="#D7A2E5",
            )
            if task.get("completed", False):
                checkbox.select()
            checkbox.grid(
                row=0, column=0, rowspan=2,
                padx=(12, 10), pady=12,
            )

            # Clicking the title, time, or priority opens the editing dialog
            title_label = ctk.CTkLabel(
                row, text=title, text_color=self.accent_color, anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"), cursor="hand2",
            )
            title_label.grid(row=0, column=1, sticky="ew", pady=(8, 0))
            title_label.bind("<Button-1>", lambda event, record=task: self.edit_task(record))

            time_label = ctk.CTkLabel(
                row, text=details, text_color=self.accent_color, anchor="w",
                font=ctk.CTkFont(size=12), cursor="hand2",
            )
            time_label.grid(row=1, column=1, sticky="ew", pady=(0, 8))
            time_label.bind("<Button-1>", lambda event, record=task: self.edit_task(record))

            edit_btn = ctk.CTkButton(
                row, text=f"{priority} >", width=90, height=30,
                corner_radius=10, fg_color="transparent",
                hover_color="#F8E9FC", text_color=self.accent_color,
                font=ctk.CTkFont(size=12, underline=True),
                command=lambda record=task: self.edit_task(record),
            )
            edit_btn.grid(row=0, column=2, rowspan=2, padx=(10, 14))
            row.bind("<Button-1>", lambda event, record=task: self.edit_task(record))
            self._bind_scroll(row)


    # Recalculate layout after content changes, once pending UI work is done
    def _reflow(self):
        self._last_size = None
        # Supply the same width and height fields used by a resize event
        self.after_idle(lambda: self._layout(SimpleNamespace(
            width=self.canvas.winfo_width(),
            height=self.canvas.winfo_height(),
        )))

    # Arrange cards side by side on desktop and stack them on narrow windows
    def _layout(self, event):
        w, h = event.width, event.height
        # Ignore initial tiny dimensions and repeated resize notifications
        if w < 2 or h < 2 or self._last_size == (w, h):
            return
        self._last_size = (w, h)

        content_width = min(1100, max(280, w - 64))
        left = max(16, (w - content_width) / 2)
        gap = 24
        compact = w < 1000
        c = self.canvas
        c.coords(self._menu_window, left, 28)
        c.itemconfigure(self._menu_window, width=44, height=44)
        c.coords(self.title, left + 58, 44)
        c.coords(self.subtitle, left + 58, 72)
        c.coords(self._profile_window, left + content_width, 30)
        c.itemconfigure(self._profile_window, width=44, height=44)

        calendar_width = content_width if compact else (content_width-gap)*0.43
        tasks_width = content_width if compact else content_width-calendar_width-gap
        reminder_width = content_width

        # Size canvas windows in screen pixels to avoid extra CTk DPI scaling
        for window, width in (
            (self._calendar_window, calendar_width),
            (self._tasks_window, tasks_width),
            (self._reminder_window, reminder_width),
        ):
            c.itemconfigure(window, width=round(width))

        # Wrap lengths use CTk logical units while the canvas uses screen pixels
        scale = self.reminder_card._get_widget_scaling()
        self.reminder_text.configure(wraplength=max(140, (reminder_width-48)/scale))
        self.date_label.configure(wraplength=max(140, (tasks_width-160)/scale))
        # Let widgets measure their updated text before choosing card heights
        self.update_idletasks()

        # Size cards from their content so calendar weeks and text cannot be cut off
        calendar_height = max(340, self.calendar_card.winfo_reqheight()+20)
        # Keep task-card height fixed relative to the calendar
        tasks_height = calendar_height
        if not compact:
            calendar_height = tasks_height = max(calendar_height, tasks_height)
        reminder_height = max(150, self.reminder_card.winfo_reqheight()+12)

        # Calculate each card position using the space occupied by previous cards
        tasks_x = left if compact else left+calendar_width+gap
        tasks_y = 110+calendar_height+gap if compact else 110
        reminder_x = left
        reminder_y = tasks_y+tasks_height+gap

        for window, x, y, height in (
            (self._calendar_window, left, 110, calendar_height),
            (self._tasks_window, tasks_x, tasks_y, tasks_height),
            (self._reminder_window, reminder_x, reminder_y, reminder_height),
        ):
            c.coords(window, x, y)
            c.itemconfigure(window, height=round(height))

        # Blend purple and orange to find the page color at a horizontal position
        def background_color(x):
            t = max(0, min(1, x/max(1, w-1)))
            return "#" + "".join(f"{round(a+(b-a)*t):02x}" for a, b in
                                  zip((151, 78, 248), (255, 145, 80)))

        # Match the area outside each rounded corner to the page gradient
        for card, x, width in (
            (self.calendar_card, left, calendar_width),
            (self.tasks_card, tasks_x, tasks_width),
            (self.reminder_card, reminder_x, reminder_width),
        ):
            lcolor = background_color(x+8)
            rcolor = background_color(x+width-8)
            card.configure(bg_color=background_color(x+width/2),
                           background_corner_colors=(lcolor, rcolor, rcolor, lcolor))
        self.menu_btn.configure(bg_color=background_color(left+22))
        self.profile_btn.configure(bg_color=background_color(left+content_width-22))

        # Extend the scrollable area when the cards exceed the visible window
        content_height = max(h, reminder_y+reminder_height+32)
        c.configure(scrollregion=(0, 0, max(w, left+content_width+16), content_height))
        # Create a small horizontal gradient and stretch it across the page
        gradient = Image.new("RGB", (256, 1))
        gradient.putdata([
            tuple(round(a+(b-a)*x/255) for a, b in
                  zip((151, 78, 248), (255, 145, 80)))
            for x in range(256)
        ])
        gradient = gradient.resize((w, int(content_height)), Image.Resampling.BILINEAR)
        # Keep a Python reference so Tk does not discard the displayed image
        self._background = ImageTk.PhotoImage(gradient, master=c)
        c.delete("gradient")
        c.create_image(0, 0, image=self._background, anchor="nw", tags="gradient")
        # Put the gradient behind every card and control
        c.tag_lower("gradient")
        if content_height <= h:
            c.yview_moveto(0)

    # Allow scrolling while the pointer is over nested widgets
    def _bind_scroll(self, widget):
        # Leave task-list scrolling to CTkScrollableFrame
        current = widget
        while current is not None:
            if current is self.task_list:
                return
            current = getattr(current, "master", None)
        widget.bind("<MouseWheel>", self._scroll, add="+")
        for child in widget.winfo_children():
            self._bind_scroll(child)

    # Scroll only when content is taller than the visible canvas
    def _scroll(self, event):
        # Avoid moving the page while scrolling inside the task list
        current = event.widget
        while current is not None:
            if current is self.task_list:
                return
            current = getattr(current, "master", None)
        bounds = self.canvas.cget("scrollregion").split()
        if bounds and float(bounds[3]) > self.canvas.winfo_height():
            self.canvas.yview_scroll(
                -int(event.delta / 120), "units"
            )
            # Stop other bindings from processing this scroll event
            return "break"

    # Placeholder for the future navigation menu
    def open_menu(self):
        pass

    # Placeholder for the future account profile screen
    def open_profile(self):
        pass

    # Open one task dialog at a time
    def add_task(self):
        # getattr returns None if a dialog has not been created yet
        existing = getattr(self, "_add_task_dialog", None)

        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_set()
            return

        self._add_task_dialog = AddTaskWidget(
            master=self,
            selected_date=self.selected_date,
            on_submit=self.receive_task,
        )


    # Receive a new task from the dialog
    def receive_task(self, task):
        try:
            user_id = self._require_task_account()
            record = task_handler.create_task(user_id, task)
        except (sqlite3.Error, ValueError, PermissionError):
            notification_handler.error_notification(
                "I couldn't save that task. Please check your account and try again.",
                expression="worried",
            )
            return False
        # Update the display only after SQL commits successfully
        # Create the date group if needed and add the saved task
        self.tasks_by_date.setdefault(record["date"], []).append(record)
        self.select_day(record["date"])

        rng = random.randint(1, 4)

        notification_handler.success_notification(
            "Task saved! {}".format("One less thing for you to worry about."
                if rng == 1 else
                "One more thing off your mind and onto mine."
                if rng == 2 else
                "I'll keep an eye on it so you don't have to."
                if rng == 3 else
                "Look at you, getting things done."
                )
        )
        return True

    # Open the same dialog with existing values and an update callback
    def edit_task(self, task):
        existing = getattr(self, "_add_task_dialog", None)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_set()
            return
        self._add_task_dialog = AddTaskWidget(
            master=self,
            selected_date=task["date"],
            task=task,
            on_submit=self.update_task,
            on_delete=self.delete_task
        )

    # Delete from SQL before removing the displayed task
    def delete_task(self, task):
        try:
            user_id = self._require_task_account()
            task_handler.delete_task(user_id, task["id"])
        except (sqlite3.Error, ValueError, PermissionError):
            notification_handler.error_notification(
                "I couldn't delete that task. Please try again.", expression="worried"
            )
            return False
        # list makes a snapshot so empty date groups can be removed safely
        for task_date, tasks in list(self.tasks_by_date.items()):
            tasks[:] = [existing for existing in tasks if existing["id"] != task["id"]]
            if not tasks:
                del self.tasks_by_date[task_date]
        self.draw_calendar()
        self.show_tasks()
        self._reflow()
        return True
    
    # Replace an existing task rather than creating another one
    def update_task(self, updated_task):
        try:
            user_id = self._require_task_account()
            record = task_handler.update_task(user_id, updated_task)
        except (sqlite3.Error, ValueError, PermissionError):
            notification_handler.error_notification(
                "I couldn't save those changes. Your original task is still there.",
                expression="worried",
            )
            return False
        # Remove the old cached version, including when its date changed
        for old_date, tasks in list(self.tasks_by_date.items()):
            tasks[:] = [task for task in tasks if task["id"] != record["id"]]
            if not tasks:
                del self.tasks_by_date[old_date]
        # Create the date group if needed and add the saved task
        self.tasks_by_date.setdefault(record["date"], []).append(record)
        self.select_day(record["date"])
        notification_handler.success_notification(
            "Task updated. Your changes are saved!"
        )
        return True

    # Flip completion between True and False
    def toggle_task(self, task):
        completed = not task.get("completed", False)
        try:
            user_id = self._require_task_account()
            task_handler.set_completed(user_id, task["id"], completed)
        except (sqlite3.Error, ValueError, PermissionError):
            # Restore the checkbox if the SQL update fails
            self.show_tasks()
            self._reflow()
            notification_handler.error_notification(
                "I couldn't save that checkbox change. Please try again.",
                expression="worried",
            )
            return False
        task["completed"] = completed
        self.show_reminders()
        self._reflow()
        return True

    # Find the next three unfinished tasks across all calendar dates
    def upcoming_tasks(self, now=None):
        now = now or datetime.now()
        cutoff = now + timedelta(days=7)
        candidates = []
        for task_date, tasks in self.tasks_by_date.items():
            for task in tasks:
                if task.get("completed", False):
                    continue
                # End time is the deadline, with start time as a fallback
                clock = task.get("end_time") or task.get("start_time")
                deadline = datetime.combine(
                    task_date,
                    datetime.strptime(clock, "%H:%M").time() if clock else time.max,
                )
                if now <= deadline <= cutoff:
                    candidates.append((deadline, task))
        # Sort by deadline and use the title to break ties
        candidates.sort(key=lambda item: (item[0], item[1]["title"]))
        # Limit the reminder panel to the three soonest tasks
        return candidates[:3]

    # Populate the reminder panel without adding any sample tasks
    def show_reminders(self):
        upcoming = self.upcoming_tasks()
        if not upcoming:
            text = "No incomplete tasks due in the next 7 days."
        else:
            lines = []
            for deadline, task in upcoming:
                due = f"{deadline:%a, %b} {deadline.day}"
                if task.get("end_time") or task.get("start_time"):
                    due += f" at {deadline:%H:%M}"
                else:
                    due += " · All day"
                lines.append(f"• {task['title']} — {due}")
            text = "\n\n".join(lines)
        self.reminder_text.configure(text=text)

    # Refresh the panel as time passes even without user interaction
    def _refresh_reminder_clock(self):
        self._sync_task_account()
        self.show_reminders()
        self._reflow()
        self._reminder_timer = self.after(60000, self._refresh_reminder_clock)

    # Cancel the refresh callback when the page is destroyed
    def destroy(self):
        timer = getattr(self, "_reminder_timer", None)
        if timer is not None:
            self.after_cancel(timer)
            self._reminder_timer = None
        super().destroy()

    # Load only the signed-in account's persisted tasks
    def load_tasks(self):
        account = account_handler.current_account
        user_id = account["id"] if account is not None else None
        # Clear previous account data before attempting a new load
        self.tasks_by_date = {}
        self._task_user_id = None
        if user_id is not None:
            records = task_handler.load_tasks(user_id)
            for task in records:
                self.tasks_by_date.setdefault(task["date"], []).append(task)
            self._task_user_id = user_id
        self.selected_date = date.today()
        self.year, self.month = self.selected_date.year, self.selected_date.month
        self.draw_calendar()
        self.show_tasks()
        self._reflow()

    # Prevent a stale dialog from writing to a different account
    def _require_task_account(self):
        account = account_handler.current_account
        if account is None or account["id"] != self._task_user_id:
            raise PermissionError("Sign into the account that owns this task list")
        return account["id"]

    # Discard another account's cached tasks after logout or account switching
    def _sync_task_account(self):
        account = account_handler.current_account
        user_id = account["id"] if account is not None else None
        if user_id != self._task_user_id:
            try:
                self.load_tasks()
            except (sqlite3.Error, ValueError):
                self.tasks_by_date = {}
                self._task_user_id = None
                self.show_tasks()
                self._reflow()

    # Check the active account after Tk finishes showing the page
    def _on_page_shown(self, event):
        self.after_idle(self._sync_task_account)
