import calendar
from datetime import date

import customtkinter as ctk
from PIL import Image, ImageTk


class HomePage(ctk.CTkFrame):
    def __init__(self):
        super().__init__(master=None, corner_radius=0)

        self.canvas = ctk.CTkCanvas(
            self, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self._background = None
        self._last_size = None

        # Reference data until the database is connected
        self.selected_date = date(2026, 7, 23)
        self.year = 2026
        self.month = 7

        self.card_color = "#E4ADF0"
        self.accent_color = "#BA7FC7"

        self.menu_btn = ctk.CTkButton(
            self.canvas,
            text="☰",
            width=42,
            height=42,
            fg_color="#A25BEF",
            hover_color="#9450DC",
            text_color="white",
            font=ctk.CTkFont(size=27),
            command=self.open_menu,
        )
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

        self.calendar_card = ctk.CTkFrame(
            self.canvas,
            fg_color=self.card_color,
            bg_color=self.card_color,
            corner_radius=22,
        )
        self.calendar_card.grid_columnconfigure(
            tuple(range(7)), weight=1, uniform="days"
        )

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

        for column, name in enumerate(
            ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        ):
            ctk.CTkLabel(
                self.calendar_card,
                text=name,
                text_color="white",
                font=ctk.CTkFont(size=13),
            ).grid(row=1, column=column, pady=(0, 6))

        self._day_buttons = []
        self._calendar_window = self.canvas.create_window(
            0, 0, window=self.calendar_card, anchor="nw"
        )

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

        self.task_list = ctk.CTkFrame(
            self.tasks_card,
            fg_color="transparent",
            corner_radius=0,
        )
        self.task_list.grid(
            row=1, column=0, columnspan=2,
            sticky="ew", padx=16, pady=(0, 18),
        )
        self.task_list.grid_columnconfigure(0, weight=1)

        self._tasks_window = self.canvas.create_window(
            0, 0, window=self.tasks_card, anchor="nw"
        )

        self.insight_card = ctk.CTkFrame(
            self.canvas,
            fg_color=self.accent_color,
            bg_color=self.card_color,
            border_color=self.card_color,
            border_width=9,
            corner_radius=24,
        )
        self.insight_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.insight_card,
            text="Today's Insight:",
            text_color="white",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(
            row=0, column=0, sticky="ew",
            padx=20, pady=(18, 4),
        )

        self.insight_text = ctk.CTkLabel(
            self.insight_card,
            text=(
                "You're busiest in the afternoon.\n"
                'Finish "Math Homework" before Biology '
                "to stay on schedule."
            ),
            text_color="white",
            anchor="w",
            justify="left",
            font=ctk.CTkFont(size=14),
        )
        self.insight_text.grid(
            row=1, column=0, sticky="ew",
            padx=20, pady=(0, 18),
        )
        self._insight_window = self.canvas.create_window(
            0, 0, window=self.insight_card, anchor="nw"
        )

        self.reminder_card = ctk.CTkFrame(
            self.canvas,
            fg_color=self.accent_color,
            bg_color=self.card_color,
            border_color=self.card_color,
            border_width=9,
            corner_radius=24,
        )
        self.reminder_card.grid_columnconfigure(0, weight=1)

        self.reminder_text = ctk.CTkLabel(
            self.reminder_card,
            text="⚠ You have three assignments due within 48 hours.",
            text_color="white",
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.reminder_text.grid(
            row=0, column=0, sticky="ew",
            padx=20, pady=22,
        )
        self._reminder_window = self.canvas.create_window(
            0, 0, window=self.reminder_card, anchor="nw"
        )

        self.draw_calendar()
        self.show_tasks()
        self.canvas.bind("<Configure>", self._layout)
        self.canvas.bind("<MouseWheel>", self._scroll)

    def draw_calendar(self):
        for button in self._day_buttons:
            button.destroy()
        self._day_buttons.clear()

        self.month_label.configure(
            text=f"{calendar.month_name[self.month]} {self.year}"
        )

        weeks = calendar.Calendar(
            firstweekday=6
        ).monthdatescalendar(self.year, self.month)

        for row, week in enumerate(weeks, start=2):
            for column, day in enumerate(week):
                selected = day == self.selected_date

                button = ctk.CTkButton(
                    self.calendar_card,
                    text=str(day.day),
                    width=34,
                    height=34,
                    corner_radius=17,
                    fg_color="#FF9150" if selected else "transparent",
                    hover_color=self.accent_color,
                    text_color=(
                        "white" if day.month == self.month else "#F4D8F9"
                    ),
                    font=ctk.CTkFont(size=13),
                    command=lambda chosen=day: self.select_day(chosen),
                )
                button.grid(
                    row=row, column=column,
                    padx=4, pady=(2, 6),
                )
                self._day_buttons.append(button)

    def change_month(self, offset):
        month_index = self.year * 12 + self.month - 1 + offset
        self.year, month_index = divmod(month_index, 12)
        self.month = month_index + 1
        self.draw_calendar()

    def select_day(self, day):
        self.selected_date = day
        self.year, self.month = day.year, day.month
        self.draw_calendar()
        self.show_tasks()

    def show_tasks(self):
        self.date_label.configure(
            text=(
                f"{self.selected_date:%A}, "
                f"{self.selected_date:%B} "
                f"{self.selected_date.day}, "
                f"{self.selected_date.year}"
            )
        )

        for widget in self.task_list.winfo_children():
            widget.destroy()

        tasks = [
            ("Math Homework", "9:00 AM - 10:00 AM", "High"),
            ("Biology Exam Prep", "2:00 PM - 4:00 PM", "Medium"),
            ("Read 20 Pages", "7:00 PM - 7:30 PM", "Low"),
        ] if self.selected_date == date(2026, 7, 23) else []

        if not tasks:
            ctk.CTkLabel(
                self.task_list,
                text="No tasks scheduled",
                text_color="white",
                font=ctk.CTkFont(size=14),
            ).grid(row=0, column=0, pady=26)
            return

        for index, (title, time, priority) in enumerate(tasks):
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

            checkbox = ctk.CTkCheckBox(
                row,
                text="",
                width=22,
                checkbox_width=18,
                checkbox_height=18,
                border_width=1,
                border_color="#DAB4E6",
                fg_color=self.accent_color,
                hover_color="#D7A2E5",
            )
            checkbox.grid(
                row=0, column=0, rowspan=2,
                padx=(12, 10), pady=12,
            )

            ctk.CTkLabel(
                row,
                text=title,
                text_color=self.accent_color,
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
            ).grid(
                row=0, column=1,
                sticky="ew", pady=(8, 0),
            )

            ctk.CTkLabel(
                row,
                text=time,
                text_color=self.accent_color,
                anchor="w",
                font=ctk.CTkFont(size=12),
            ).grid(
                row=1, column=1,
                sticky="ew", pady=(0, 8),
            )

            ctk.CTkLabel(
                row,
                text=f"{priority} >",
                text_color=self.accent_color,
                font=ctk.CTkFont(size=12, underline=True),
            ).grid(
                row=0, column=2, rowspan=2,
                padx=(10, 14),
            )

    def _layout(self, event):
        w, h = event.width, event.height
        if w < 2 or h < 2 or self._last_size == (w, h):
            return
        self._last_size = (w, h)

        content_width = min(1100, max(340, w - 64))
        left = (w - content_width) / 2
        gap = 24
        compact = w < 850

        c = self.canvas
        c.coords(self._menu_window, left, 28)
        c.coords(self.title, left + 58, 44)
        c.coords(self.subtitle, left + 58, 72)
        c.coords(self._profile_window, left + content_width, 30)

        calendar_width = (
            content_width if compact else (content_width - gap) * 0.43
        )
        tasks_width = (
            content_width if compact else content_width - calendar_width - gap
        )

        c.coords(self._calendar_window, left, 110)
        c.itemconfigure(
            self._calendar_window,
            width=calendar_width,
            height=340,
        )

        tasks_x = left if compact else left + calendar_width + gap
        tasks_y = 474 if compact else 110
        c.coords(self._tasks_window, tasks_x, tasks_y)
        c.itemconfigure(
            self._tasks_window,
            width=tasks_width,
            height=340,
        )

        insights_y = tasks_y + 364
        insight_width = (
            content_width if compact else (content_width - gap) * 0.6
        )
        reminder_width = (
            content_width if compact else content_width - insight_width - gap
        )

        c.coords(self._insight_window, left, insights_y)
        c.itemconfigure(
            self._insight_window,
            width=insight_width,
            height=150,
        )

        reminder_x = left if compact else left + insight_width + gap
        reminder_y = insights_y + 174 if compact else insights_y
        c.coords(self._reminder_window, reminder_x, reminder_y)
        c.itemconfigure(
            self._reminder_window,
            width=reminder_width,
            height=150,
        )

        self.insight_text.configure(
            wraplength=max(180, insight_width - 48)
        )
        self.reminder_text.configure(
            wraplength=max(180, reminder_width - 48)
        )

        content_height = max(h, reminder_y + 182)
        c.configure(scrollregion=(0, 0, w, content_height))

        gradient = Image.new("RGB", (256, 1))
        gradient.putdata([
            tuple(
                round(a + (b - a) * x / 255)
                for a, b in zip(
                    (151, 78, 248), (255, 145, 80)
                )
            )
            for x in range(256)
        ])
        gradient = gradient.resize(
            (w, int(content_height)),
            Image.Resampling.BILINEAR,
        )

        self._background = ImageTk.PhotoImage(
            gradient, master=c
        )
        c.delete("gradient")
        c.create_image(
            0, 0,
            image=self._background,
            anchor="nw",
            tags="gradient",
        )
        c.tag_lower("gradient")

    def _scroll(self, event):
        bounds = self.canvas.cget("scrollregion").split()
        if bounds and float(bounds[3]) > self.canvas.winfo_height():
            self.canvas.yview_scroll(
                -int(event.delta / 120), "units"
            )
            return "break"

    def open_menu(self):
        pass

    def open_profile(self):
        pass

    def add_task(self):
        pass