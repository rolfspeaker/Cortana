# Parse the task date and start and end times
from datetime import date, datetime
from PIL import Image

from pathlib import Path

import modules.gui.notification as notification_handler
import customtkinter as ctk

# Separate dialog used for both adding and editing tasks
class AddTaskWidget(ctk.CTkToplevel):
    def __init__(self, master, selected_date, on_submit, task=None, on_delete=None):
        # Attach this dialog to the home page
        super().__init__(master)

        # Store the home-page function that receives the completed task
        self.on_submit = on_submit
        # Work on a copy so closing the dialog leaves the original unchanged
        self.original_task = dict(task) if task is not None else None
        # Passing a task switches the dialog into editing mode
        editing = task is not None

        # Set the window title, size, and relationship to the main app
        self.title("Edit Task" if editing else "Add New Task")
        self.geometry("560x660")
        self.minsize(480, 560)
        self.configure(fg_color="#BA7FC7")
        self.transient(master.winfo_toplevel())

        self.on_delete = on_delete
        
        # Only show Delete when editing an existing task
        if editing and on_delete is not None:
            icon_path = (
                Path(__file__).resolve().parents[2]
                / "images"
                / "trash_icon.png"
            )

            with Image.open(icon_path) as source:
                icon = source.convert("RGBA")

            self.trash_image = ctk.CTkImage(
                light_image=icon,
                dark_image=icon,
                size=(24, 24),
            )

            self.delete_button = ctk.CTkButton(
                self,
                text="",
                image=self.trash_image,
                width=40,
                height=40,
                corner_radius=12,
                fg_color="#E4ADF0",
                hover_color="#F4C9E8",
                command=self.delete_task,
            )
            self.delete_button.grid(
                row=0,
                column=0,
                sticky="e",
                padx=28,
                pady=(24, 12),
            )

        self.grid_columnconfigure(0, weight=1)
        # Let the form area expand while the title and save button stay visible
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Edit Task" if editing else "Add New Task",
            text_color="white",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(
            row=0, column=0,
            sticky="w", padx=28, pady=(24, 12),
        )

        # A scrollable form keeps fields accessible in shorter windows
        self.form = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.form.grid(
            row=1, column=0,
            sticky="nsew", padx=20, pady=0,
        )
        # Make the two field columns share available width equally
        self.form.grid_columnconfigure(
            (0, 1), weight=1, uniform="fields"
        )

        # Task title spans both columns
        self.title_label = ctk.CTkLabel(
            self.form,
            text="Task Title",
            text_color="white",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.title_label.grid(
            row=0, column=0, columnspan=2,
            sticky="ew", padx=8, pady=(8, 5),
        )

        self.task_title = ctk.CTkEntry(
            self.form,
            placeholder_text="e.g. Study for Computer Science final exam",
            height=42,
            corner_radius=12,
            border_width=0,
            fg_color="#E4ADF0",
            text_color="#593568",
            placeholder_text_color="#80518F",
        )
        self.task_title.grid(
            row=1, column=0, columnspan=2,
            sticky="ew", padx=8,
        )

        ctk.CTkLabel(
            self.form,
            text="Description (Optional)",
            text_color="white",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(
            row=2, column=0, columnspan=2,
            sticky="ew", padx=8, pady=(16, 5),
        )

        # Optional multiline description
        self.description = ctk.CTkTextbox(
            self.form,
            height=80,
            corner_radius=12,
            border_width=0,
            fg_color="#E4ADF0",
            text_color="#593568",
        )
        self.description.grid(
            row=3, column=0, columnspan=2,
            sticky="ew", padx=8,
        )

        # Place date and time labels next to each other
        for column, text in enumerate(("Date", "Time — Start / End")):
            ctk.CTkLabel(
                self.form,
                text=text,
                text_color="white",
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
            ).grid(
                row=4, column=column,
                sticky="ew", padx=8, pady=(16, 5),
            )

        self.task_date = ctk.CTkEntry(
            self.form,
            placeholder_text="YYYY-MM-DD",
            height=40,
            corner_radius=12,
            border_width=0,
            fg_color="#E4ADF0",
            text_color="#593568",
        )
        # Default to the date selected on the home-page calendar
        self.task_date.insert(0, selected_date.isoformat())
        self.task_date.grid(
            row=5, column=0, sticky="ew", padx=8,
        )

        # Group start and end entries inside the time column
        time_frame = ctk.CTkFrame(
            self.form, fg_color="transparent"
        )
        time_frame.grid(
            row=5, column=1, sticky="ew", padx=8,
        )
        time_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_time = ctk.CTkEntry(
            time_frame,
            width=90,
            placeholder_text="09:00",
            height=40,
            corner_radius=12,
            border_width=0,
            fg_color="#E4ADF0",
            text_color="#593568",
        )
        self.start_time.grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )

        self.end_time = ctk.CTkEntry(
            time_frame,
            width=90,
            placeholder_text="10:00",
            height=40,
            corner_radius=12,
            border_width=0,
            fg_color="#E4ADF0",
            text_color="#593568",
        )
        self.end_time.grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

        # Store dropdown widgets by field name for later reading
        self.options = {}

        # Each definition supplies a field name, label, choices, and default
        definitions = [
            ("priority", "Priority", ["High", "Medium", "Low"], "Medium"),
            (
                "category",
                "Category",
                ["School", "Work", "Personal", "Other"],
                "Personal",
            ),
            (
                "reminder",
                "Reminder",
                ["None", "At start time", "15 minutes before", "1 hour before", "1 day before"],
                "None",
            ),
            (
                "repeat",
                "Repeat",
                ["Does not repeat", "Daily", "Weekly", "Monthly"],
                "Does not repeat",
            ),
        ]

        # Build dropdowns in two columns from their definitions
        for index, (name, label, values, default) in enumerate(definitions):
            # Split the field index into a row number and column number
            row, column = divmod(index, 2)
            label_row = 6 + row * 2

            ctk.CTkLabel(
                self.form,
                text=label,
                text_color="white",
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
            ).grid(
                row=label_row, column=column,
                sticky="ew", padx=8, pady=(16, 5),
            )

            menu = ctk.CTkOptionMenu(
                self.form,
                values=values,
                height=40,
                corner_radius=12,
                fg_color="#E4ADF0",
                button_color="#D699E3",
                button_hover_color="#CC8BD9",
                dropdown_fg_color="#FFE5F5",
                dropdown_hover_color="#E4ADF0",
                dropdown_text_color="#593568",
                text_color="#593568",
                dynamic_resizing=False,
            )
            # Select the initial dropdown value
            menu.set(default)
            menu.grid(
                row=label_row + 1, column=column,
                sticky="ew", padx=8,
            )
            self.options[name] = menu

        # Validation messages appear here without closing the form (SCRAPPED FOR NOTIFICATIONS)
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="#FFE5F5",
            wraplength=460,
            font=ctk.CTkFont(size=13),
        )
        self.error_label.grid(
            row=2, column=0,
            sticky="ew", padx=28, pady=(8, 0),
        )

        # Use the same submit logic for Add Task and Save Changes
        self.add_btn = ctk.CTkButton(
            self,
            text="Save Changes" if editing else "✓  Add Task",
            height=44,
            corner_radius=16,
            fg_color="#FFE5F5",
            hover_color="#F4C9E8",
            text_color="#7135A0",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.submit,
        )
        self.add_btn.grid(
            row=3, column=0,
            sticky="ew", padx=28, pady=(8, 24),
        )

        # Load every saved field when editing an existing task
        if editing:
            self.task_title.insert(0, task["title"])
            # Textbox position 1.0 means the start of the first line
            self.description.insert("1.0", task.get("description", ""))
            self.task_date.delete(0, "end")
            self.task_date.insert(0, task["date"].isoformat())
            self.start_time.insert(0, task.get("start_time", ""))
            self.end_time.insert(0, task.get("end_time", ""))
            for name, menu in self.options.items():
                menu.set(task.get(name, menu.get()))

        # Escape cancels without sending changes to the home page
        self.bind("<Escape>", lambda event: self.destroy())
        # Wait briefly for the window to appear before assigning focus
        self.after(100, self._activate)

    # Keep input in this dialog and focus the title entry
    def _activate(self):
        if self.winfo_exists():
            # Prevent interaction with the main window while the dialog is open
            self.grab_set()
            self.task_title.focus_set()

    def delete_task(self):
        # Remove the task through the home page
        self.on_delete(self.original_task)
        self.destroy()

    # Validate the form and send its data to the supplied callback
    def submit(self):
        # Read the title and remove surrounding whitespace
        title = self.task_title.get().strip()

        # Reject an empty title and keep the dialog open
        if not title:
            notification_handler.error_notification(
                "Every task needs a name, wouldn't you say? What are we calling this one?",
            )
            return

        #if 

        # Convert the entered date into a date object
        try:
            selected_date = date.fromisoformat(
                self.task_date.get().strip()
            )
        except ValueError:
            notification_handler.error_notification(
                "That date doesn't look right. Try YYYY-MM-DD. Y'know, like, 2026-10-03?",
                expression="worried"
            ); return

        # Times are optional, but both are required when either is supplied
        start = self.start_time.get().strip()
        end = self.end_time.get().strip()

        # Parse supplied times using the 24-hour clock
        if start or end:
            try:
                start_value = datetime.strptime(start, "%H:%M").time()
                end_value = datetime.strptime(end, "%H:%M").time()
            except ValueError:
                notification_handler.error_notification(
                    "Both times need to be in 24-hour HH:MM format. I run on military time, so bear with me."
                ); return

            # This form currently supports tasks that finish on the same day
            if end_value <= start_value:
                notification_handler.error_notification(
                    "Your task somehow ends before it starts. I'm flattered that you think I can time travel, but I'm afraid I have limits.",
                    duration=5000
                )
                return

            # Normalize valid times to the same HH:MM format
            start = start_value.strftime("%H:%M")
            end = end_value.strftime("%H:%M")

        # Preserve the ID and completion state when editing an existing task
        task = dict(self.original_task or {})
        # Replace form fields while retaining any other saved task information
        task.update({
            "title": title,
            # end-1c excludes the trailing newline added by the textbox
            "description": self.description.get("1.0", "end-1c").strip(),
            "date": selected_date,
            "start_time": start,
            "end_time": end,
            "priority": self.options["priority"].get(),
            "category": self.options["category"].get(),
            "reminder": self.options["reminder"].get(),
            "repeat": self.options["repeat"].get(),
        })

        # Add or update the task through the callback supplied by HomePage
        self.on_submit(task)
        # Close only after the callback finishes successfully
        self.destroy()